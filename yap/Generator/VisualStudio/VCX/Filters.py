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

import  ID
import  xml.etree.ElementTree as Xml
from    xml.dom import minidom
from    Groups  import ItemGroup

# class Filters
class Filters:
	# ctor
	def __init__( self, project, root = None ):
		self._xml           = Xml.Element( 'Project', attrib = dict( DefaultTargets = project.DefaultTargets, ToolsVersion = project.ToolsVersion, xmlns = project.xmlns ) )
		self._root          = root
		self._folders       = {}
		self._sourceFiles   = ItemGroup( self._xml )
		self._headerFiles   = ItemGroup( self._xml )
		self._filters       = ItemGroup( self._xml )

	# addHeaderFile
	def addHeaderFile( self, file ):
		item = self._headerFiles.addInclude( file.projectPath )

		if file.folder.sourcePath != '':
			item.set( 'Filter', file.folder.sourcePath )
			self._addFolder( file.folder )

	# addSourceFile
	def addSourceFile( self, file ):
		item = self._sourceFiles.addSource( file.projectPath )

		if file.folder.sourcePath != '':
			item.set( 'Filter', file.folder.sourcePath )
			self._addFolder( file.folder )

	# _addFolder
	def _addFolder( self, folder ):
		if folder.sourcePath in self._folders.keys():
			return

		self._filters.addFilter( folder.sourcePath ).set( 'UniqueIdentifier', ID.generate() )
		self._folders[folder.sourcePath] = folder

	# serialize
	def serialize( self, fileName ):
		str      = Xml.tostring( self._xml, 'utf-8' )
		reparsed = minidom.parseString( str )

		with open( fileName, 'wt' ) as fh:
			fh.write( reparsed.toprettyxml( indent = "  ", encoding = 'utf-8') )
			fh.close()