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

from FindLibrary import findLibrary

# class Library
class Library:
	# ctor
	def __init__( self, target, name ):
		self._target    = target
		self._name      = name

	# type
	@property
	def type( self ):
		return 'unknown'

	# __str__
	def __str__( self ):
		return "[Library {0}]".format( self._name )

	# name
	@property
	def name( self ):
		return self._name


# class LocalLibrary
class LocalLibrary( Library ):
	# ctor
	def __init__( self, target, name ):
		Library.__init__( self, target, name )

	# type
	@property
	def type( self ):
		return 'local'

	# __str__
	def __str__( self ):
		return "[LocalLibrary {0}]".format( self._name )


# class ExternalLibrary
class ExternalLibrary( Library ):
	# ctor
	def __init__( self, name, headers, libs ):
		Library.__init__( self, None, name )

		self._headers   = headers
		self._libs      = libs

	# headers
	@property
	def headers( self ):
		return self._headers

	# libs
	@property
	def libs( self ):
		return self._libs

	# fileName
	@property
	def fileName( self ):
		return self.getLibraryFileName( self._name )

	# type
	@property
	def type( self ):
		return 'external'

	# __str__
	def __str__( self ):
		return "[{0} headers='{1}' libs={2}]".format( self._name, self._headers, self._libs )

	# getLibraryFileName
	def getLibraryFileName( self, name ):
		staticLibraryPath = os.path.join( self._libs, 'lib' + name + '.a' )
		sharedLibraryPath = os.path.join( self._libs, 'lib' + name + '.dylib' )

		if os.path.exists( sharedLibraryPath ): return sharedLibraryPath

		return staticLibraryPath

	# find
	@staticmethod
	def find( name ):
		info = findLibrary( name )
		if info:
			return ExternalLibrary( info['name'], info['headers'], info['library'] )

		return None

# class ExternalPackage
class ExternalPackage( ExternalLibrary ):
	# ctor
	def __init__( self, name, headers, libs, items ):
		ExternalLibrary.__init__( self, name, headers, libs )

		self._items = items

	# type
	@property
	def type( self ):
		return 'package'

	# items
	@property
	def items( self ):
		return [self.getLibraryFileName( item ) for item in self._items]

	# __str__
	def __str__( self ):
		return "[{0} headers='{1}' libs='{2}' items='{3}']".format( self._name, self._headers, self._libs, self._items )

	# find
	@staticmethod
	def find( name, *items ):
		info = findLibrary( name )
		if info:
			return ExternalPackage( info['name'], info['headers'], info['library'], items )

		return None

# class Framework
class Framework( Library ):
	# ctor
	def __init__( self, target, name ):
		Library.__init__( self, target, name )

	# __str__
	def __str__( self ):
		return "[Framework {0}]".format( self._name )

	# type
	@property
	def type( self ):
		return 'framework'