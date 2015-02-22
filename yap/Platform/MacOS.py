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

# class MacOS
class MacOS( Platform ):
	# ctor
	def __init__(self):
		Platform.__init__(self)

		# Add system search paths
		sdk = '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.10.sdk/'

		self.add_header_search_paths( '/usr/local/include', os.path.join( sdk, 'System/Library/Frameworks' ) )
		self.add_library_search_paths( '/usr/local/include', os.path.join( sdk, 'System/Library/Frameworks' ) )

		# Register libraries
		self.register_library('OpenAL',  headers=['OpenAL/al.h', 'OpenAL/alc.h'],                       libraries=['OpenAL'])
		self.register_library('OpenGL',  headers=['OpenGL/gl.h', 'OpenGL/OpenGL.h', 'OpenGL/glext.h'],  libraries=['OpenGL', 'QuartzCore'])
		self.register_library('GLUT',    headers=[ 'GLUT/GLUT.h' ],                                     libraries=['GLUT'])

	# userPaths
	@property
	def userPaths(self):
		return os.environ['PATH'].split( ':' )

	# library_file_names
	def library_file_names(self, name):
		return [name + '.framework', 'lib' + name + '.a', 'lib' + name + '.dylib']