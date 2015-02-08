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

import xml.etree.ElementTree as Xml

# class Group
class Group:
	# ctor
	def __init__( self, parent, type, attrib ):
		self._xml = Xml.SubElement( parent, type, attrib = attrib )

	# set
	def set( self, key, value ):
		prop        = Xml.SubElement( self._xml, key )
		prop.text   = str( value )

	# setProperties
	def setProperties( self, properties ):
		for k, v in properties.items():
			if isinstance( v, dict ):
				Group( self._xml, k, {} ).setProperties( v )
				continue

			self.set( k, v )

# class PropertyGroup
class PropertyGroup( Group ):
	# ctor
	def __init__( self, parent, type, **attrib ):
		Group.__init__( self, parent, type if type else 'PropertyGroup', attrib )

# class PropertySheets
class PropertySheets( PropertyGroup ):
	# ctor
	def __init__( self, parent, configuration ):
		PropertyGroup.__init__( self, parent, 'ImportGroup', Label = 'PropertySheets', Condition = configuration.condition )
		Group( self._xml, 'Import', dict(
			Project = '$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props',
			Condition = "exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')",
			Label = 'LocalAppDataPlatform'
		) )

# class ItemGroup
class ItemGroup( Group ):
	# ctor
	def __init__( self, parent ):
		Group.__init__( self, parent, 'ItemGroup', {})

	# addInclude
	def addInclude( self, name ):
		Group( self._xml, 'ClInclude', dict( Include = name ) )

	# addSource
	def addSource( self, name ):
		Group( self._xml, 'ClCompile', dict( Include = name ) )

# class ProjectConfigurations
class ProjectConfigurations( PropertyGroup ):
	# ctor
	def __init__( self, parent ):
		PropertyGroup.__init__( self, parent, 'ItemGroup', Label = 'ProjectConfigurations' )

	# add
	def add( self, configuration ):
		group = PropertyGroup( self._xml, 'ProjectConfiguration', Include = configuration.identifier )
		group.set( 'Configuration', configuration.name )
		group.set( 'Platform', configuration.platform )