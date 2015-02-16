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

# class Library
class Library:
	# HeaderSearchPaths
	HeaderSearchPaths       = [ '/usr/local/include' ]
	LibrarySearchPaths      = [ '/usr/local/lib'     ]
	FrameworkSearchPaths    = [ '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.10.sdk/System/Library/Frameworks' ]

	# ctor
	def __init__( self, name, headers, libraries, shared = False ):
		self._name                  = name
		self._headers               = headers
		self._libraries             = libraries
		self._shared                = shared
		self._headersSearchPaths    = None
		self._librarySearchPaths    = None
		self._linkTo                = []
		self._isFramework           = False

	# name
	@property
	def name( self ):
		return self._name

	# isFramework
	@property
	def isFramework( self ):
		return self._isFramework

	# isFound
	@property
	def isFound( self ):
		return self._librarySearchPaths != None and self._headersSearchPaths != None

	# linkTo
	@property
	def linkTo( self ):
		return self._linkTo

	# headersSearchPaths
	@property
	def headersSearchPaths( self ):
		return self._headersSearchPaths

	# librarySearchPaths
	@property
	def librarySearchPaths( self ):
		return self._librarySearchPaths

	# findFilePath
	def findFilePath( self, fileName, paths ):
		for path in paths:
			if os.path.exists( os.path.join( path, fileName ) ):
				return path

		return None

	# locate
	def locate( self ):
		headerSearchPath    = None
		librarySearchPath   = None

		# Locate header search path
		for header in self._headers:
			path = self.findFilePath( header, Library.HeaderSearchPaths )

			if path:
				headerSearchPath = path
				break

		# Locate library search path
		for library in self._libraries:
			path = self.findFilePath( self.formatLibraryName( library, self._shared ), Library.LibrarySearchPaths )

			if path:
				librarySearchPath = path
				break

		if not headerSearchPath or not librarySearchPath:
			return self.locateFramework()

		self._headersSearchPaths = [ headerSearchPath ]
		self._librarySearchPaths = [ librarySearchPath ]
		self._linkTo             = [self.formatLinkName( name, self._shared ) for name in self._libraries]

		return self.isFound

	# locateFramework
	def locateFramework( self ):
		for path in Library.FrameworkSearchPaths:
			if os.path.exists( os.path.join( path, self._name + '.framework' ) ):
				self._headersSearchPaths = []
				self._librarySearchPaths = []
				self._isFramework        = True
				self._linkTo             = [ self._name ]
				break

		return self.isFound

	# formatLibraryName
	def formatLibraryName( self, name, shared ):
		return 'lib' + name + '.a' if not shared else 'lib' + name + '.dlyb'

	# formatLinkName
	def formatLinkName( self, name, shared ):
		return 'lib' + name + '.a' if not shared else 'lib' + name + '.dlyb'

	# find
	@staticmethod
	def find( name, required = False ):
		libraries = dict(
				vorbis = dict( name = 'Vorbis', headers = [ 'vorbis/codec.h', 'vorbis/vorbisfile.h' ],  libraries = [ 'vorbis', 'vorbisfile', 'ogg' ] )
			,   OpenAL = dict( name = 'OpenAL', headers = [ 'OpenAL/al.h', 'OpenAL/alc.h' ],            libraries = [ 'OpenAL' ] )
		)

		library = None

		if name in libraries.keys():
			library = Library( **libraries[name] )
			if not library.locate():
				library = None

		if not library and required:
			print 'Error: library {0} is required'.format( name )
			exit(1)

		return library