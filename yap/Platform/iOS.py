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

from Unix import Unix

# class iOS
class iOS(Unix):
	# ctor
	def __init__(self):
		Unix.__init__(self)

		# Add system search paths
		sdk = '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/'

		self.add_header_search_paths( os.path.join( sdk, 'System/Library/Frameworks' ) )
		self.add_library_search_paths( os.path.join( sdk, 'System/Library/Frameworks' ) )

		# Register libraries
		self.register_library('OpenAL',  headers=['OpenAL/al.h', 'OpenAL/alc.h'],               libraries=['OpenAL'])
		self.register_library('OpenGL',  headers=['ES2/gl.h', 'ES2/OpenGL.h', 'ES2/glext.h'],   libraries=['OpenGLES', 'QuartzCore'], defines = ['OPENGL_ES'])
		self.register_library('GLUT',    headers=['GLUT/GLUT.h'],                               libraries=['GLUT'])

	# library_file_names
	def library_file_names(self, name):
		return [name + '.framework'] + Unix.library_file_names(self, name)

	# header_file_names
	def header_file_names(self, name, filename):
		return [name + '.framework/Headers/' + os.path.basename(filename)] + Unix.header_file_names(self, name, filename)