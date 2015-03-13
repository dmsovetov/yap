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

from collections    import namedtuple
from Unix           import Unix
#from ..Library      import Library

# class Xcode
class Xcode(Unix):
	# ctor
	def __init__(self, sdk):
		Unix.__init__(self)

		self._sdk       = sdk
		self._aliases   = {}

	# _find_library_by_name
	def _find_library_by_name(self, library):
		# Do an alias lookup
		if library in self._aliases.keys():
			library = self._aliases[library]

		# Find a framework by name
		name       = library
		library    = library + '.framework'
		frameworks = os.path.join( self._sdk, 'System/Library/Frameworks' )
		path       = Unix.exists(library, [frameworks])

		if not path:
			return None

		return namedtuple('Framework', 'type, name, path')(type='framework', name=name, path=frameworks)

	# add_library_alias
	def add_library_alias(self, identifier, alias):
		self._aliases[identifier] = alias

	# library_file_names
	def library_file_names(self, name):
		return [name + '.framework'] + Unix.library_file_names(self, name)

	# header_file_names
	def header_file_names(self, name, filename):
		return [name + '.framework/Headers/' + os.path.basename(filename)] + Unix.header_file_names(self, name, filename)