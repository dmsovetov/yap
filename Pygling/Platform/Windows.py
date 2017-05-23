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

import os, glob

from .Platform import Platform

# class Windows
class Windows( Platform ):
	# ctor
	def __init__( self ):
		Platform.__init__( self )

		# Add system search paths
		sdk = os.path.join( os.environ['ProgramFiles(x86)'], 'Microsoft SDKs/Windows' )

		if os.path.exists(sdk):
			for path in glob.glob(sdk + '/*'):
				self.register_windows_sdk(path)

		kits = os.path.join(os.environ['ProgramFiles(x86)'], 'Windows Kits')

		if os.path.exists(kits):
			for kit in glob.glob(kits + '/*'):
				self.register_windows_kit(kit)

		# Register libraries
		self.register_library('OpenAL',  	headers=['OpenAL/al.h', 'OpenAL/alc.h'],   libraries=['openal32'])
		self.register_library('OpenGL',  	headers=['gl/gl.h'],                       libraries=['opengl32'])
		self.register_library('GLUT',    	headers=['glut/glut.h'],                   libraries=['glut32'])
		self.register_library('Winsock2', 	headers=['winsock2.h', 'Ws2tcpip.h'],      libraries=['Ws2_32'])

    # register_windows_kit
	def register_windows_kit(self, path):
		headers = ['shared', 'um', 'WinRT']

		for folder in headers:
			header_path = os.path.join(path, 'Include', folder )
			if os.path.exists(header_path):
				self.add_header_search_paths(header_path)

		self.add_library_search_paths(os.path.join(path, 'Lib/win8/um/x86'))

	# register_windows_sdk
	def register_windows_sdk(self, path):
		header_path  = os.path.join(path, 'Include')
		library_path = os.path.join(path, 'Lib')

		if os.path.exists(header_path):
			self.add_header_search_paths(header_path)

		if os.path.exists(library_path):
			self.add_library_search_paths(library_path)

	# toolset
	def toolset(self, sdk):
		if sdk == None:
			return self.latest_toolset()

		toolsets = dict(vs2010='v100', vs2012='v110', vs2013='v120')

		if sdk in list(toolsets.keys()):
			return toolsets[sdk]

		return self.latest_toolset()

	# latest_toolset
	def latest_toolset(self):
		commonTools = [key for key in list(os.environ.keys()) if key.endswith('COMNTOOLS')]
		toolSets	= [tools.replace( 'COMNTOOLS', '' ).replace('VS', 'v') for tools in commonTools]
		return toolSets[-1]

	# userpaths
	@property
	def userpaths(self):
		return os.environ['PATH'].split( ';' )

	# library_file_names
	def library_file_names(self, name):
		return [name + '.lib', 'lib' + name + '.lib']