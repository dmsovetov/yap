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

import glob, os

from File import File

# class Folder
class Folder:
	# ctor
	def __init__( self, target, name = '', parent = None ):
		self._name      = name
		self._parent    = parent
		self._target    = target
		self._files     = []
		self._folders   = {}

	# sourcePath
	@property
	def sourcePath( self ):
		return os.path.join( self._parent.sourcePath, self._name ) if self._parent else self._name

	# addFile
	def addFile( self, fileName ):
		self._files.append( File( self._target, self, fileName ) )

	# addFileAtPath
	def addFileAtPath( self, path ):
		self.resolve( path ).addFile( os.path.basename( path ) )

	# addFilesFromDirectory
	def addFilesFromDirectory( self, path ):
		if path.endswith( '/*' ):
			return self.addFilesFromDirectoryRecursive( path )

		for fileName in glob.glob( os.path.join( path, '*.*' ) ):
			self.addFileAtPath( os.path.relpath( fileName, self._target.sourcePath ) )

	# addFilesFromDirectoryRecursive
	def addFilesFromDirectoryRecursive( self, path ):
		self.addFilesFromDirectory( path.replace( '/*', '/' ) )

		# Recursively add all nested folders
		for folder in glob.glob( path ):
			if os.path.isdir( folder ):
				# Continue recursive add
				self.addFilesFromDirectoryRecursive( os.path.join( folder, '*' ) )

	# resolve
	def resolve( self, path ):
		items = path.split( '/' )
		name  = items[0]

		if len( items ) == 1:
			return self

		if not name in self._folders.keys():
			self._folders[name] = Folder( self._target, name, self )

		return self._folders[name].resolve( '/'.join( items[1:] ) )

	# filterFiles
	def filterFiles( self, filter ):
		result = [file for file in self._files if filter == None or filter( file )]

		for name, folder in self._folders.items():
			result = result + folder.filterFiles( filter )

		return result