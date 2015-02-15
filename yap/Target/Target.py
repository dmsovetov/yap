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

from Library    import LocalLibrary
from Library    import ExternalLibrary
from Framework  import Framework
from Folder     import Folder
from Path       import Path
from ..Makefile import Makefile

# class Target
class Target:
	Ident           = 0
	StaticLibrary   = 'static'
	SharedLibrary   = 'shared'
	Executable      = 'executable'

	# ctor
	def __init__( self, name, sources = None, paths = None, defines = None, linkTo = None, link = None ):
		self.message( 'Configure ' + name + '...' )

		self._project       = Makefile.getProject()
		self.name           = name
		self._defines       = []
		self._root          = Folder( self )
		self.resources      = []
		self.commands       = []
		self._libraries     = []
		self._frameworks    = []
		self._paths         = []
		self.type           = linkTo

		self._currentSourceDir = Makefile.getCurrentSourceDir()
		self._currentBinaryDir = Makefile.getCurrentBinaryDir()

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
			for lib in link:
				if isinstance( lib, Framework ):
					self.frameworks( lib )
				if isinstance( lib, Target ):
					self.link( lib.name )
				else:
					self.link( lib )

		# Add default defines
		if defines:
			for define in defines:
				self.define( define )

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

	# projectPath
	@property
	def projectPath( self ):
		return (self.project.generator.getPathForTarget( self ) if self.project else self._currentBinaryDir).replace( '\\', '/' )

	# sourcePath
	@property
	def sourcePath( self ):
		return self._currentSourceDir

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
		return os.path.join( self.sourcePath, Makefile.substituteVars( path ) ).replace( '\\', '/' )

	# toSourcePath
	def toSourcePath( self, path ):
		return os.path.relpath( path, self.sourcePath ).replace( '\\', '/' )

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
		[self._libraries.append( item if isinstance( item, ExternalLibrary ) else LocalLibrary( self, item ) ) for item in list]

	# frameworks
	def frameworks( self, *list ):
		[self._frameworks.append( Framework( self, item ) if isinstance( item, str ) else item ) for item in list]

	# include
	def include( self, *list ):
		[self._paths.append( Path( self, Path.Headers, self.toFullPath( path ) ) ) for path in list]

	# librarySearchPaths
	def librarySearchPaths( self, *list ):
		[self._paths.append( Path( self, Path.Libraries, self.toFullPath( path ) ) ) for path in list]

	# assets
	def assets( self, *list ):
		[self.resources.append( path ) for path in list]

	# filterSourceFiles
	def filterSourceFiles( self, filter = None ):
		return self._root.filterFiles( filter )

	# filterFrameworks
	def filterFrameworks( self, filter = None ):
		return [framework for framework in self._frameworks if filter == None or filter( framework )]

	# filterLibraries
	def filterLibraries( self, filter = None ):
		return [library for library in self._libraries if filter == None or filter( library )]

	# filterLocalLibraries
	def filterLocalLibraries( self, filter = None ):
		return [library for library in self.filterLibraries( lambda library: library.type == 'local' ) if filter == None or filter( library )]

	# filterPaths
	def filterPaths( self, filter = None ):
		return [path for path in self._paths if filter == None or filter( path )]

	# _configure
	def _configure( self, type ):
		Target.Ident = Target.Ident - 1
		self.type    = type

		'''
		# Add local libraries path
		if type in [Target.Executable, Target.SharedLibrary]:
			for library in self.filterLibraries( lambda library: library.type == 'local' ):
				target = self.project.findTarget( library.name )
				if target == None:
					print 'Warning: no local library {0}'.format( library.name )
					continue

				self.librarySearchPaths( target.projectPath )
		'''

	# sharedLibrary
	def sharedLibrary( self ):
		self.message( 'Configured as shared library' )
		self._configure( Target.SharedLibrary )

	# staticLibrary
	def staticLibrary( self ):
		self.message( 'Configured as static library' )
		self._configure( Target.StaticLibrary )

	# executable
	def executable( self, **params ):
		self.message( 'Configured as executable' )
		self.params = params

		self._configure( Target.Executable )

	# message
	@classmethod
	def message( self, text ):
		msg = ''
		for i in range( 0, Target.Ident * 4 ):
			msg += ' '
		print( msg + text )