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

from collections import namedtuple
from Folder     import Folder
from ..Makefile import Makefile
from ..Location import Path, PathScope

# class Target
class Target:
	Ident           = 0
	StaticLibrary   = 'static'
	SharedLibrary   = 'shared'
	Executable      = 'executable'

	# ctor
	def __init__( self, name, sources = None, paths = None, defines = None, linkTo = None, link = None ):
		self.message( 'Configure ' + name + '...' )

		self._project       = Makefile.project
		self.name           = name
		self._defines       = []
		self._root          = Folder( self )
		self.resources      = []
		self.commands       = []
		self._linkWith      = []
		self._paths         = []
		self.type           = linkTo
		self._pathScope     = PathScope.current

		# Register this target
		if self.project:
			self.project.registerTarget( self )

		# Add default include folders
		if paths:
			for path in paths:
				if path.startswith( 'L:' ):
					self.librarySearchPaths( path.split( ':' )[1] )
				else:
					self.include( path )

		# Add default libs
		if link:
			self.link( *link )

		# Add default defines
		if defines:
			self.define( *defines )

		# Add default sources
		if sources:
			for source in sources:
				fullPath = self.toFullPath( source )

				if os.path.isfile( fullPath ):
					self.files( source )
				else:
					self.dirs( source )

		Target.Ident = Target.Ident + 1

		# Link to
		if linkTo == Target.Executable:
			self.executable()
		elif linkTo == Target.StaticLibrary:
			self.staticLibrary()
		elif linkTo == Target.SharedLibrary:
			self.sharedLibrary()

	# projectpath
	@property
	def projectpath(self):
		return (self.project.generator.getPathForTarget(self) if self.project else self._currentBinaryDir).replace( '\\', '/' )

	# sourcePath
	@property
	def sourcePath( self ):
		return self._pathScope.source

	# project
	@property
	def project( self ):
		return self._project

	# defines
	@property
	def defines( self ):
		return self._defines

	# toFullPath
	def toFullPath( self, path ):
		return os.path.join( self._pathScope.source, Makefile.substituteVars( path ) ).replace( '\\', '/' )

	# toSourcePath
	def toSourcePath( self, path ):
		return os.path.relpath( path, self._pathScope.source ).replace( '\\', '/' )

	# define
	def define( self, *list ):
		[self.defines.append( define ) for define in list]

	# dirs
	def dirs( self, *list ):
		[self._root.addFilesFromDirectory( self.toFullPath( path ) ) for path in list]

	# files
	def files( self, *list ):
		[self._root.addFileAtPath( self.toSourcePath( self.toFullPath( path ) ) ) for path in list]

	# link
	def link( self, *list ):
		[self._linkWith.append(namedtuple('LocalLibrary', 'type, name')(type='local', name=item)) for item in list]

	# linkExternal
	def linkExternal( self, *list ):
		allLinked = True

		for location in list:
			if not location:
				allLinked = False
				continue

			self._linkWith.append(location)

		return allLinked

	# include
	def include( self, *paths ):
		[self._paths.append( Path( Path.Headers, path ) ) for path in paths]

	# add_library_search_paths
	def add_library_search_paths( self, *paths ):
		[self._paths.append( Path( Path.Libraries, path ) ) for path in paths]

	# add_headers_search_paths
	def add_headers_search_paths( self, *paths ):
		[self._paths.append( Path( Path.Headers, path ) ) for path in paths]

	# assets
	def assets( self, *list ):
		[self.resources.append( path ) for path in list]

	# filterSourceFiles
	def filterSourceFiles( self, filter = None ):
		return self._root.filterFiles( filter )

	# filterLibraries
	def filterLibraries( self, filter = None ):
		return [library for library in self._linkWith if filter == None or filter( library )]

	# filterPaths
	def filterPaths( self, filter = None ):
		return [path for path in self._paths if filter == None or filter( path )]

	# sharedLibrary
	def sharedLibrary( self ):
		self.message( 'Configured as shared library' )

		Target.Ident = Target.Ident - 1
		self.type    = Target.SharedLibrary

	# staticLibrary
	def staticLibrary( self ):
		self.message( 'Configured as static library' )

		Target.Ident = Target.Ident - 1
		self.type    = Target.StaticLibrary

	# executable
	def executable( self, **params ):
		self.message( 'Configured as executable' )
		self.params = params

		Target.Ident = Target.Ident - 1
		self.type    = Target.Executable

	# message
	@classmethod
	def message( self, text ):
		msg = ''
		for i in range( 0, Target.Ident * 4 ):
			msg += ' '
		print( msg + text )