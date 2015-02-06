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

import BuildPhases, Files, Targets

from ...Template        import Template
from ObjectList         import ObjectList
from Group              import Group
from BuildConfiguration import BuildConfiguration
from ConfigurationList  import ConfigurationList

# class Objects
class Objects:
	# ctor
	def __init__( self, project ):
		self.groups             = ObjectList( 'PBXGroup' )
		self.configurations     = ObjectList( 'PBXConfiguration' )
		self.configurationLists = ObjectList( 'PBXConfigurationList' )
		self.buildPhases        = ObjectList( 'PBXBuildPhase' )
		self.targets            = ObjectList( 'PBXNativeTarget' )
		self.buildFiles         = ObjectList( 'PBXBuildFiles' )
		self.fileReferences     = ObjectList( 'PBXFileReference' )
		self.proxies            = ObjectList( 'PBXContainerItemProxy' )
		self.dependencies       = ObjectList( 'PBXTargetDependency' )
		self.project            = project

	# createGroup
	def createGroup( self, name = None, parent = None ):
		group = Group( self, name )

		if parent:
			parent.children.add( group )

		self.groups.add( group )
		return group

	# createFramework
	def createFramework( self, name ):
		if name.endswith( '.framework' ):
			return self.createFileReference( 'wrapper.framework', name, '"<group>"' )
		else:
			return self.createFileReference( 'wrapper.framework', 'System/Library/Frameworks/{0}.framework'.format( name ), 'SDKROOT' )

	# createBuildFile
	def createBuildFile( self, target, file ):
		result = Files.BuildFile( target, file )
		self.buildFiles.add( result )
		return result

	# createFileReference
	def createFileReference( self, type, path, dir ):
		result = Files.FileReference( type, path, dir )
		self.fileReferences.add( result )
		return result

	# createSourceBuildPhase
	def createSourceBuildPhase( self, target ):
		result = BuildPhases.SourceBuildPhase( target )
		self.buildPhases.add( result )
		return result

	# createResourcePhase
	def createResourcePhase( self, target ):
		result = BuildPhases.ResourceBuildPhase( target )
		self.buildPhases.add( result )
		return result

	# createShellScriptPhase
	def createShellScriptPhase( self, target, command ):
		result = BuildPhases.ShellScriptPhase( target, command )
		self.buildPhases.add( result )
		return result

	# createFrameworkPhase
	def createFrameworkPhase( self, target ):
		result = BuildPhases.FrameworkBuildPhase( target )
		self.buildPhases.add( result )
		return result

	# createDependency
	def createDependency( self, target ):
		result = Targets.Dependency( self, target )
		self.dependencies.add( result )
		return result

	# createContainerItemProxy
	def createContainerItemProxy( self, target ):
		result = Targets.ContainerItemProxy( target, self.project )
		self.proxies.add( result )
		return result

	# createConfiguration
	def createConfiguration( self, name, settings ):
		configuration = BuildConfiguration( name, settings )
		self.configurations.add( configuration )

		return configuration

	# createStaticLibrary
	def createStaticLibrary( self, group, name, path, configurations, defaultConfiguration ):
		result = Targets.StaticLibrary( self, group, name, path, configurations, defaultConfiguration )
		self.targets.add( result )

		return result

	# createApplication
	def createApplication( self, group, name, path, configurations, defaultConfiguration ):
		result = Targets.Application( self, group, name, path, configurations, defaultConfiguration )
		self.targets.add( result )

		return result

	# createApplicationBundle
	def createApplicationBundle( self, group, name, path, configurations, defaultConfiguration, teamIdentifier ):
		result = Targets.ApplicationBundle( self, group, name, path, configurations, defaultConfiguration, teamIdentifier )
		self.targets.add( result )

		return result

	# createConfigurationList
	def createConfigurationList( self, target, configurations, default ):
		result = ConfigurationList( default, target )

		for k, v in configurations.items():
			result.add( self.createConfiguration( k, v ) )

		self.configurationLists.add( result )

		return result

	# compile
	def compile( self ):
		items  = [self.buildFiles, self.proxies, self.fileReferences, self.groups, self.targets, self.project, self.buildPhases, self.dependencies, self.configurations, self.configurationLists ]
		result = ''

		for objects in items:
			result += Template( Objects.Section ).compile( { 'name': objects.isa, 'items': objects.compile() } )

		return result

	# Section
	Section = """
/* Begin {name} section */
{items}
/* End {name} section */
"""