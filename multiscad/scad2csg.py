# Take in a .scad file, run OpenSCAD to generate .csg file.

import sys
import os
import platform
import re
import subprocess
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--scad', help='OpenSCAD input file')
parser.add_argument('--csg', help='OpenSCAD CSG output file')
parser.add_argument('--threads', help='Number of threads to run in parallel', type=int, default=1)
parser.add_argument('--workdir', help='Working Directory', default="./workdir")
args = parser.parse_args()

class CSGTree(object):
    """ OpenSCAD CSG Tree"""
    def __init__(self, name='root', type=None, params=None, children=None, parent=None):
        self.name = name
        self.children = []
        self.type=type
        self.params = []
        self.parent = parent
        if params is not None:
            for param in params:
                self.add_param(param)
        if children is not None:
            for child in children:
                self.add_child(child)
    def __repr__(self):
        return self.name
    def add_child(self, node):
        assert isinstance(node, CSGTree)
        self.children.append(node)
    def add_param(self, param):
        assert isinstance(param, CSGParam)
        self.params.append(param)
    def print_tree(self, indent=""):
        print indent+"CSGTree: "+str(self.name)+" type:"+str(self.type)
        if len(self.params) > 0:
            for param in self.params:
                param.print_pair(indent=indent+"    ")
        if len(self.children) > 0:
            for child in self.children:
                child.print_tree(indent=indent+"  ")

class CSGParam(object):
    """ OpenSCAD CSG Parameter Name/Value pair"""
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
    def print_pair(self,indent=""):
        print indent+"CSGParam: "+self.name+" = "+self.value

class OpenSCAD(object):
    """ Run OpenSCAD processes """
    def __init__(self):
        if platform.system() == 'Darwin' :
            self.openscad = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
        elif platform.system() == 'Linux' :
            self.openscad = subprocess.check_output(['which','openscad'])
        self.openscad=self.openscad.rstrip('\n').rstrip('\r')
        self.workdir = args.workdir
        if not os.path.isdir(self.workdir) :
            os.makedirs(self.workdir)
        self.scad_file = args.scad
        self.csg_file = args.csg
        self.threads = args.threads
        self.operators = {}
        self.instances = {}
        self.hierarchy = []
        self.file_stack = []
        self.operator_variants = {} 
        self.instance_variants = {} 
        self.tree=CSGTree()
        self.node=self.tree
        print "Arguments: ",args
        subprocess.check_output([self.openscad,"-o",self.workdir+"/"+self.csg_file,self.scad_file])
        self.read_csg()
    def read_csg(self):
        with open( self.workdir+"/"+self.csg_file, "r") as ins:
            lines = []
            hier_level=0
            for line in ins:
                variant_name=""
                module_parts=False
                parse_line=line.rstrip('\n').rstrip('\r')
                parse_line=parse_line.lstrip(' ').lstrip('\t')
                module_parts=re.match(r"([^(]+)\(([^)]*)\)\s*([;{])",parse_line)
                if module_parts :
                    module_name=module_parts.group(1)
                    module_params=module_parts.group(2)
                    module_suffix=module_parts.group(3)
                    if module_suffix == ";" :
                        variant_name=self.analyze_instance(module_name,module_params)
                        new_params=CSGParam(name="params",value=module_params)
                        new_node=CSGTree(name=variant_name,type=module_name,params=[ new_params ],parent=self.node)
                        self.node.add_child(new_node)
                    else :
                        hier_level=hier_level+1
                        variant_name=self.analyze_operator(module_name,module_params)
                        self.hierarchy.append(variant_name)
                        new_params=CSGParam(name="params",value=module_params)
                        new_node=CSGTree(name=variant_name,type=module_name,params=[ new_params ],parent=self.node)
                        self.node.add_child(new_node)
                        self.node=new_node
                print "read_csg: ",hier_level," : ",parse_line
                if module_parts :
                    print "   module_name = ",module_name
                    print "   module_params = ",module_params
                    print "   module_suffix = ",module_suffix
                    print "   variant_name = ",variant_name
                if re.search('\A}',parse_line) :
                    hier_level=hier_level-1
                    self.hierarchy.pop()
                    self.node=self.node.parent
                lines.append(parse_line)
            ins.close()
        print ""
        print "Summary:"
        for operator_name in self.operators.keys() :
            print "  operator '"+operator_name+"'"
            for operator_params in self.operators[operator_name].keys() :
                print "    params ("+operator_params+")"
                print "      variant = '"+self.operators[operator_name][operator_params]['variant']+"'"
                print "      count = "+str(self.operators[operator_name][operator_params]['count'])
        for instance_name in self.instances.keys() :
            print "  instance '"+instance_name+"'"
            for instance_params in self.instances[instance_name].keys() :
                print "    params ("+instance_params+")"
                print "      variant = '"+self.instances[instance_name][instance_params]['variant']+"'"
                print "      count = "+str(self.instances[instance_name][instance_params]['count'])
                print "      paths:"
                for path in self.instances[instance_name][instance_params]['paths'] :
                    print "        "+str(path)
        print "Tree:"
        print self.tree.print_tree()
    def analyze_operator(self,name,params) :
        print "  analyze_operator : name = ",name," params = ",params
        param_key=params
        if not self.operators.has_key(name) :
            self.operators[name]={}
            self.operator_variants[name]={}
        if not self.operators[name].has_key(param_key) :
            self.operators[name][param_key]={}
            self.operators[name][param_key]['count']=1
            self.operators[name][param_key]['paths']=[]
            operator_variant_name=name+str(len(self.operator_variants[name].keys()))
            self.operators[name][param_key]['variant']=operator_variant_name
            self.operator_variants[name][operator_variant_name]=param_key
        else :
            self.operators[name][param_key]['count'] += 1
            operator_variant_name=self.operators[name][param_key]['variant']
        return operator_variant_name
    def analyze_instance(self,name,params) :
        print "  analyze_instance : name = ",name," params = ",params
        print "                     path = ",self.hierarchy
        if not self.instances.has_key(name) :
            self.instances[name]={}
            self.instance_variants[name]={}
        if not self.instances[name].has_key(params) :
            self.instances[name][params]={}
            self.instances[name][params]['count']=1
            self.instances[name][params]['paths']=[]
            instance_variant_name=name+str(len(self.instance_variants[name].keys()))
            self.instances[name][params]['variant']=instance_variant_name
            self.instance_variants[name][instance_variant_name]=params
        else :
            self.instances[name][params]['count'] += 1
            instance_variant_name=self.instances[name][params]['variant']
        self.instances[name][params]['paths'].append(list(self.hierarchy))
        return instance_variant_name

if __name__ == '__main__':
    print 'Running multiscad...'
    hello = OpenSCAD()

