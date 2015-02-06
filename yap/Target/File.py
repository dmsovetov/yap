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

# class File
class File:
	# ctor
	def __init__( self, target, folder, fileName ):
		self._target    = target
		self._folder    = folder
		self._fileName  = fileName

	# sourcePath
	@property
	def sourcePath( self ):
		return os.path.join( self._folder.sourcePath, self._fileName )

	# fullPath
	@property
	def fullPath( self ):
		return os.path.abspath( os.path.join( self._target.sourcePath, self.sourcePath ) )

	# sourceFolder
	@property
	def sourceFolder( self ):
		return self._folder.sourcePath

	# fileName
	@property
	def fileName( self ):
		return os.path.basename( self.localPath )

	# name
	@property
	def name( self ):
		return self.nameAndExtension[0]

	# ext
	@property
	def ext( self ):
		return self.nameAndExtension[1]

	# nameAndExtension
	@property
	def nameAndExtension( self ):
		return os.path.splitext( self.fileName )

	# relativePath
	def relativePath( self, base ):
		return os.path.join( os.path.relpath( self._target.sourcePath, base ), self.localPath )