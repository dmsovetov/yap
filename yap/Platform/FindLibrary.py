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

# class FindLibrary
class FindLibrary:
	# ctor
	def __init__( self, headers = [], libraries = [], defines = []):
		self._headers   = headers
		self._libraries = libraries
		self._defines   = defines

	# exists
	@staticmethod
	def exists( filename, paths ):
		for path in paths:
			if os.path.exists( os.path.join( path, filename ) ):
				return path

		return None

	# find
	def find( self, platform ):
		# Locate header search path
		for header in self._headers:
			FindLibrary.exists( header, platform.headers )

		# Locate library search path
		for library in self._libraries:
			for filename in platform.library_file_names( library ):
				FindLibrary.exists( filename, platform.libraries )