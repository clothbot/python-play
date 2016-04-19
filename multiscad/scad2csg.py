# Take in a .scad file, run OpenSCAD to generate .csg file.

import sys
import os
import re
import subprocess
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--scad', help='OpenSCAD input file')
parser.add_argument('--csg', help='OpenSCAD CSG output file')
parser.add_argument('--threads', help='Number of threads to run in parallel', type=int, default=1)
parser.add_argument('--workdir', help='Working Directory', default="./workdir")
args = parser.parse_args()

class OpenSCAD(object):
    """ Run OpenSCAD processes """
    def __init__(self):
        self.openscad = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
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
                    else :
                        hier_level=hier_level+1
                        variant_name=self.analyze_operator(module_name,module_params)
                        self.hierarchy.append(variant_name)
                print "read_csg: ",hier_level," : ",parse_line
                if module_parts :
                    print "   module_name = ",module_name
                    print "   module_params = ",module_params
                    print "   module_suffix = ",module_suffix
                    print "   variant_name = ",variant_name
                if re.search('\A}',parse_line) :
                    hier_level=hier_level-1
                    self.hierarchy.pop()
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

