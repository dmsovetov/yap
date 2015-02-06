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

import os
import sys

from ..Makefile  import Makefile
from Target      import Target

sys.path.insert( 1, os.path.join( sys.path[0], '..' ) )

# class Project
class Project( Target ):
	# ctor
	def __init__( self, name, platform, importer, generator ):
		Target.__init__( self, name )

		self.message( 'Configuring build environment for ' + name + '...' )

		self._targets 		= []
		self.importer		= importer
		self.platform       = platform
		self.generator      = generator
		self.toolsPath 		= None
		self.outputLibPath	= None
		self.outputExePath	= None

	# target
	def target( self, *list ):
		for item in list:
			current = Makefile.getCurrentSourceDir()
			binary  = Makefile.getCurrentBinaryDir()

			Makefile.CurrentSourceDir.append( os.path.join( current, item ) )
			Makefile.CurrentBinaryDir.append( os.path.join( binary, item + '.dir' ) )

			self.importer( os.path.join( current, item, 'Makefile.py' ) )

			Makefile.CurrentBinaryDir.pop()
			Makefile.CurrentSourceDir.pop()

	# registerTarget
	def registerTarget( self, target ):
		self._targets.append( target )

	# setToolsPath
	def setToolsPath( self, path ):
		self.toolsPath = path
		
	# setLibraryOutput
	def setLibraryOutput( self, path ):
		self.outputLibPath = path

	# setExecutableOutput
	def setExecutableOutput( self, path ):
		self.outputExePath = path

	# filterTargets
	def filterTargets( self, filter = None ):
		return [target for target in self._targets if filter == None or filter( target )]

	# findTarget
	def findTarget( self, name, types ):
		for target in self._targets:
			if target.name == name and target.type in types:
				return target

		return None