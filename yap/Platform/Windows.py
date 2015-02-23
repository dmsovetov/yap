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

from Platform import Platform

# class Windows
class Windows( Platform ):
	# ctor
	def __init__( self ):
		Platform.__init__( self )

		# Add system search paths
		sdk = os.path.join( os.environ['ProgramFiles(x86)'], 'Microsoft SDKs/Windows/v7.0A/' )
		self.add_header_search_paths( os.path.join( sdk, 'Include' ) )
		self.add_library_search_paths( os.path.join( sdk, 'Lib' ) )

		# Register libraries
		self.register_library('OpenAL',  headers=['OpenAL/al.h', 'OpenAL/alc.h'],   libraries=['openal32'])
		self.register_library('OpenGL',  headers=['gl/gl.h'],                       libraries=['opengl32'])
		self.register_library('GLUT',    headers=['glut/glut.h'],                   libraries=['glut32'])

	# userpaths
	@property
	def userpaths(self):
		return os.environ['PATH'].split( ';' )

	# library_file_names
	def library_file_names(self, name):
		return [name + '.lib', 'lib' + name + '.lib']