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

#!/usr/bin/python

import argparse, os, glob

from Makefile   import Makefile
from Target     import Target
from Target     import StaticLibrary
from Target     import Executable
from Target     import ExternalLibrary
from Target     import ExternalPackage

# parseUnknownArguments
def parseUnknownArguments( args ):
	for arg in args:
		if not arg.startswith( '--' ):
			continue

		items = arg.split( '=' )
		name  = items[0][2:].upper()

		if len( items ) == 1:
			Makefile.getProject().define( 'DC_' + name + '_ENABLED' )
		else:
			Makefile.getProject().define( 'DC_' + name + '=' + items[1] )
			Makefile.getProject().define( 'DC_' + name + '_' + items[1].upper() )
			Makefile.set( name, items[1] )

# Entry point
if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser( description = 'Yet Another Project Generator', prefix_chars = '--' )

	parser.add_argument( "platform",                        type = str, help = "Target platform" )
	parser.add_argument( "-s", "--source", default = '',    type = str, help = "Project source path" )
	parser.add_argument( "-o", "--output", default = '',    type = str, help = "Output path" )
	parser.add_argument( "-n", "--name",   default = '',    type = str, help = "Workspace (solution) name" )

	args, unknown = parser.parse_known_args()

	if not os.path.exists( os.path.join( args.source, 'Makefile.py' ) ):
		print 'Error: no Makefile.py file found.'
		exit(1)

	# Generate project
	Makefile.set( 'PLATFORM', args.platform )
	Makefile.setPaths( os.path.abspath( args.source ), os.path.abspath( args.output ) )
	Makefile.Initialize( args.name, args.platform, (lambda fileName: execfile( fileName )) )
	Makefile.getProject().define( 'DC_PLATFORM_' + args.platform.upper() )
	Makefile.getProject().define( 'DC_PLATFORM=' + args.platform )

	# Parse unknown arguments
	parseUnknownArguments( unknown )

	# Build config
	platform	    = args.platform
	findFramework   = ExternalLibrary.find
	findPackage     = ExternalPackage.find

	# Include
	def Include( *list ):
		for path in list:
			Makefile.getProject().target( path )

	# Has
	def Has( name ):
		return Makefile.get( name.upper() ) != None

	# Folders
	def Folders( path ):
		# class Folder
		class Folder:
			def __init__( self, path ):
				self.name = os.path.basename( path )
				self.path = path

		return [Folder( path ) for path in glob.glob( os.path.join( Makefile.getCurrentSourceDir(), path ) ) if os.path.isdir( path )]

	# Files
	def Files( path ):
		# class Folder
		class File:
			def __init__( self, path ):
				self.name = os.path.basename( path )
				self.path = path

		return [File( path ) for path in glob.glob( os.path.join( Makefile.getCurrentSourceDir(), path ) ) if os.path.isfile( path )]

	execfile( Makefile.SourceDir + '/Makefile.py' )

	Makefile.Generate()
