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

from Groups         import Group
from Groups         import ItemGroup
from Groups         import ProjectConfigurations
from Groups         import PropertyGroup
from Groups         import PropertySheets
from Configuration  import Configuration
from Filters        import Filters

# class Project
class Project:
	ToolsVersion    = "4.0"
	DefaultTargets  = "Build"
	xmlns           = "http://schemas.microsoft.com/developer/msbuild/2003"

	# ctor
	def __init__( self, type, name, keyword, platform ):
		self._xml           = Xml.Element( 'Project', attrib=dict( DefaultTargets = Project.DefaultTargets, ToolsVersion = Project.ToolsVersion, xmlns = Project.xmlns ) )
		self._id            = ID.generate()
		self._type          = type
		self._name          = name
		self._keyword       = keyword
		self._platform      = platform
		self._dependencies  = []

		self._filters           = Filters( Project )
		self._configurations    = []
		self._sourceFiles       = []
		self._headerFiles       = []

	# name
	@property
	def name( self ):
		return self._name

	# uid
	@property
	def uid( self ):
		return self._id

	# dependencies
	@property
	def dependencies( self ):
		return self._dependencies

	# filters
	@property
	def filters( self ):
		return self._filters

	# addDependency
	def addDependency( self, project ):
		self._dependencies.append( project )

	# createConfiguration
	def createConfiguration( self, name, settings ):
		return Configuration( name, settings, self._platform )

	# setConfigurations
	def setConfigurations( self, configurations ):
		self._configurations = configurations

	# addHeaderFiles
	def addHeaderFiles( self, files ):
		self._headerFiles = self._headerFiles + files

	# addSourceFiles
	def addSourceFiles( self, files ):
		self._sourceFiles = self._sourceFiles + files

	# serialize
	def serialize( self, fileName ):
		self._createXml()

		str      = Xml.tostring( self._xml, 'utf-8' )
		reparsed = minidom.parseString( str )

		with open( fileName, 'wt' ) as fh:
			fh.write( reparsed.toprettyxml( indent = "  ", encoding = 'utf-8') )
			fh.close()

		self._filters.serialize( fileName + '.filters' )

	# _createXml
	def _createXml( self ):
		# Add project configurations group
		configurationsGroup = ProjectConfigurations( self._xml )
		[configurationsGroup.add( cfg ) for cfg in self._configurations]

		# Source files
		group = ItemGroup( self._xml )
		[group.addSource( file ) for file in self._sourceFiles]

		# Header files
		group = ItemGroup( self._xml )
		[group.addInclude( file ) for file in self._headerFiles]

		# Add globals
		globals = PropertyGroup( self._xml, None, Label = 'Globals' )
		globals.set( 'ProjectGuid', self._id )
		globals.set( 'Keyword',self._keyword )
		globals.set( 'RootNamespace', self._name )

		# Add imports
		Group( self._xml, 'Import', dict( Project = '$(VCTargetsPath)\Microsoft.Cpp.Default.props' ) )

		# Add property groups
		for cfg in self._configurations:
			group = PropertyGroup( self._xml, 'PropertyGroup', Condition = cfg.condition, Label = 'Configuration' )
			group.setProperties( dict(
				ConfigurationType = self._type,
			    UseDebugLibraries = True if cfg.name == 'Debug' else False,
			    CharacterSet = 'MultiByte'
			) )

		# Add import properties
		Group( self._xml, 'Import', dict( Project = '$(VCTargetsPath)\Microsoft.Cpp.props' ) )

		# Add property sheets
		for cfg in self._configurations:
			PropertySheets( self._xml, cfg )

		# Add item definition groups
		for cfg in self._configurations:
			definition = PropertyGroup( self._xml, 'ItemDefinitionGroup', Condition = cfg.condition )
			definition.setProperties( cfg.settings )

		# Add import targets
		Group( self._xml, 'Import', dict( Project = '$(VCTargetsPath)\Microsoft.Cpp.targets' ) )