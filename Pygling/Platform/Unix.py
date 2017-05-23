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

import os

from .Platform import Platform

# class Unix
class Unix(Platform):
	# ctor
	def __init__(self):
		Platform.__init__(self)

		headers = ['/usr/local/include', '/usr/include']
		libs	= ['/usr/local/lib', '/usr/lib', '/lib/i386-linux-gnu']

		for path in headers:
			if os.path.exists(path):
				self.add_header_search_paths(path)

		for path in libs:
			if os.path.exists(path):
				self.add_library_search_paths(path)

	# userpaths
	@property
	def userpaths(self):
		return os.environ['PATH'].split( ':' )

	# library_file_names
	def library_file_names(self, name):
		return ['lib' + name + '.a', 'lib' + name + '.dylib', 'lib' + name + '.so']

	# header_file_names
	def header_file_names(self, name, filename):
		return [filename]

	# _find_library_by_name
	def _find_library_by_name(self, library):
		return Unix.ExternalLibrary(type='external', name=library, locations=[])