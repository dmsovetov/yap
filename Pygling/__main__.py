#!/usr/bin/python

#################################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Dmitry Sovetov
#
# https://github.com/dmsovetov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#################################################################################

import os, argparse
from Workspace import Workspace

# class Pygling
class Pygling:
	@staticmethod
	def main():
		name = os.path.basename( os.getcwd() )

		# Parse arguments
		parser = argparse.ArgumentParser( prog = 'Pygling', description = 'Pygling C++ workspace generator.', prefix_chars = '--', formatter_class = argparse.ArgumentDefaultsHelpFormatter )

		parser.add_argument( "action",                                          type = str, help = "Action", choices = ["configure", "build", "install"] )
		parser.add_argument( "-p", "--platform",        default = 'all',        type = str, help = "Target platform" )
		parser.add_argument( "-s", "--source",          default = '.',          type = str, help = "Project source path" )
		parser.add_argument( "-o", "--output",          default = 'projects',   type = str, help = "Output path" )
		parser.add_argument( "-n", "--name",            default = name,         type = str, help = "Workspace (solution) name" )
		parser.add_argument( "-a", "--arch",            default = 'default',    type = str, help = "Target build architecture" )
		parser.add_argument( "-x", "--std",             default = 'cxx98',      type = str, help = "C++ standard", choices = ['cxx99', 'cxx11'] )
		parser.add_argument( "-c", "--configuration",   default = 'Release',    type = str, help = "Build configuration" )
		parser.add_argument( "--package",										type = str, help = "Application package identifier" )
		parser.add_argument( "--platformSdk",									type = str, help = "Platform SDK identifier" )
		parser.add_argument( "--xcteam",                                        type = str, help = "Xcode provisioning profile to be used" )

		# Check action
		args, unknown = parser.parse_known_args()

		workspace = Workspace(args.name, args.source, args.output, args, unknown)

		if   args.action == 'configure':  workspace.configure(args.platform)
		elif args.action == 'build':      workspace.build(args.platform)
		elif args.action == 'install':    workspace.install(args.platform)
		
# Entry point
if __name__ == "__main__":
	Pygling.main()