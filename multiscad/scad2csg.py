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
        self.modules = {}
        self.module_variants = {} 
        print "Arguments: ",args
        subprocess.check_output([self.openscad,"-o",self.workdir+"/"+self.csg_file,self.scad_file])
        self.read_csg()
    def read_csg(self):
        with open( self.workdir+"/"+self.csg_file, "r") as ins:
            array = []
            hier_level=0
            for line in ins:
                module_parts=False
                parse_line=line.rstrip('\n').rstrip('\r')
                parse_line=parse_line.lstrip(' ').lstrip('\t')
                if re.search('{\Z',parse_line) :
                    hier_level=hier_level+1
                if re.search('\A}',parse_line) :
                    hier_level=hier_level-1
                module_parts=re.match(r"([^(]+)\(([^)]+)\)",parse_line)
                if module_parts :
                    module_name=module_parts.group(1)
                    module_params=module_parts.group(2)
                    variant_name=self.analyze_module(module_name,module_params)
                print "read_csg: ",hier_level," : ",parse_line
                if module_parts :
                    print "   module_name = ",module_name
                    print "   module_params = ",module_params
                    print "   variant_name = ",variant_name
                array.append(parse_line)
            ins.close()
        print "Summary:"
        for module_name in self.modules.keys() :
            print "  module ",module_name
            for module_params in self.modules[module_name].keys() :
                print "    params ",module_params
                print "      variant = ",self.modules[module_name][module_params]['variant']
                print "      count = ",self.modules[module_name][module_params]['count']
    def analyze_module(self,name,params) :
        print "  analyze_module : name = ",name," params = ",params
        if not self.modules.has_key(name) :
            self.modules[name]={}
            self.module_variants[name]={}
        if not self.modules[name].has_key(params) :
            self.modules[name][params]={}
            self.modules[name][params]['count']=1
            module_variant_name=name+str(len(self.module_variants[name].keys()))
            self.modules[name][params]['variant']=module_variant_name
            self.module_variants[name][module_variant_name]=params
        else :
            self.modules[name][params]['count'] += 1
            module_variant_name=self.modules[name][params]['variant']
        return module_variant_name

if __name__ == '__main__':
    print 'Running multiscad...'
    hello = OpenSCAD()

