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

from FindLibrary import FindLibrary

# class Platform
class Platform:
	# ctor
	def __init__( self ):
		self._headerSearchPaths  = []
		self._librarySearchPaths = []
		self._libraries          = {}

		self.register_library('vorbis',  headers=['vorbis/codec.h', 'vorbis/vorbisfile.h'],     libraries=['vorbis', 'vorbisfile', 'ogg'])
		self.register_library('fbx',     headers=['fbxsdk.h'],                                  libraries=['fbxsdk'])
		self.register_library('yaml',    headers=['yaml/yaml.h'],                               libraries=['yaml'])
		self.register_library('embree2', headers=['embree2/rtcore.h', 'embree2/rtcore_ray.h'],  libraries=['embree', 'sys', 'simd', 'embree_sse41', 'embree_sse42'])

	# userPaths
	@property
	def userPaths(self):
		return []

	# headers
	@property
	def headers(self):
		return self._headerSearchPaths + self.userPaths

	# libraries
	@property
	def libraries(self):
		return self._librarySearchPaths + self.userPaths

	# find_library
	def find_library(self, name):
		if name in self._libraries.keys():
			return self._libraries[name].find( self )

		return None

	# library_file_names
	def library_file_names(self, name):
		return [name]

	# add_header_search_paths
	def add_header_search_paths(self, *paths):
		[self._headerSearchPaths.append(path) for path in paths]

	# add_library_search_paths
	def add_library_search_paths(self, *paths):
		[self._librarySearchPaths.append(path) for path in paths]

	# register_library
	def register_library(self, name, headers = [], libraries = [], defines = []):
		self._libraries[name] = FindLibrary(headers=headers, libraries=libraries, defines=defines)