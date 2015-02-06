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

from Resource       import Resource
from ObjectList     import ObjectList
from ...Template    import Template

# class Target
class Target( Resource ):
	# ctor
	def __init__( self, objects, group, type, name, path, configurations, defaultConfiguration ):
		Resource.__init__( self, 'PBXNativeTarget', name )

		self.objects            = objects
		self.group              = group
		self.generated          = None
		self.product            = self.objects.createFileReference( type, path, 'BUILT_PRODUCTS_DIR' )
		self.configurationList  = self.objects.createConfigurationList( self, configurations, defaultConfiguration )
		self.sourcePhase        = self.objects.createSourceBuildPhase( self )
		self.frameworkPhase     = self.objects.createFrameworkPhase( self )
		self.dependencies       = ObjectList( 'PBXTargetDependency' )
		self.phases             = ObjectList( 'PBXBuildPhases' )

	# compileAttributes
	def compileAttributes( self ):
		return ''

	# compile
	def compile( self ):
		self.addBuildPhases()

		return Template( Target.Root ).compile( {
													'id':                   self.id,
													'name':                 self.name,
		                                            'isa':                  self.isa,
													'configuration.list':   self.configurationList.id,
													'build.phases':         self.phases.compileList(),
		                                            'dependencies':         self.dependencies.compileList(),
		                                            'product.id':           self.product.id,
		                                            'product.fileName':     self.product.name,
		                                            'product.type':         Target.Types[self.product.type]
												} )

	# addBuildPhases
	def addBuildPhases( self ):
		self.phases.add( self.sourcePhase )
		self.phases.add( self.frameworkPhase )

	# getSourceTypeForExtension
	def getSourceTypeForExtension( self, ext ):
		types = { '.xcassets': 'folder.assetcatalog', '.h': 'sourcecode.c.h', '.c': 'sourcecode.c.c', '.cpp': 'sourcecode.cpp.cpp', '.mm': 'sourcecode.cpp.objcpp', '.plist': 'text.plist' }
		if ext in types.keys():
			return types[ext]

		return 'sourcecode'

	# resolveGroup
	def resolveGroup( self, path ):
		group = self.group

		for name in path.split( '/' ):
			if len( name ):
				group = group.resolveGroup( name )

		return group

	# addProjectLibrary
	def addProjectLibrary( self, target ):
		assert target.product != None

		# Create file reference for a product
		file = self.objects.project.addProjectLibrary( target.name )

		# Add link phase
		self.frameworkPhase.add( self.objects.createBuildFile( self, file ) )

		# Add dependency
		self.dependencies.add( self.objects.createDependency( target ) )

	# addLibrary
	def addLibrary( self, name ):
		# Create file reference for library
		file = self.objects.project.addLibrary( name )

		# Add to a link phase
		self.frameworkPhase.add( self.objects.createBuildFile( self, file ) )

		# Add library search path
		self.configurationList.forEach( lambda c: c.addSetting( 'LIBRARY_SEARCH_PATHS', os.path.dirname( name ) ) )

	# addFramework
	def addFramework( self, name ):
		# Create file reference for framework
		file = self.objects.project.addFramework( name )

		# Add link phase
		self.frameworkPhase.add( self.objects.createBuildFile( self, file ) )

		# Add framework search path for local frameworks
		if name.endswith( '.framework' ):
			self.configurationList.forEach( lambda c: c.addSetting( 'FRAMEWORK_SEARCH_PATHS', os.path.dirname( name ) ) )

	# addShellScript
	def addShellScript( self, command ):
		self.phases.add( self.objects.createShellScriptPhase( self, command ) )

	# addSourceFile
	def addSourceFile( self, fileName, parentGroup ):
		group = self.resolveGroup( parentGroup ) if len( parentGroup ) > 0 else self.group
		self.addFileToGroup( fileName, group )

	# addGeneratedFile
	def addGeneratedFile( self, fileName ):
		if not self.generated:
			self.generated = self.objects.project.addGroup( 'GeneratedFiles' )

		self.addFileToGroup( fileName, self.generated )

	# addFileToGroup
	def addFileToGroup( self, fileName, group ):
		compilable  = ['.c', '.cpp', '.m', '.mm']
		name, ext   = os.path.splitext( fileName )
		type        = self.getSourceTypeForExtension( ext )
		file        = self.objects.createFileReference( type, fileName, '"<group>"' )

		group.add( file )

		# Add a build file to source build phase
		if ext in compilable:
			self.sourcePhase.add( self.objects.createBuildFile( self, file ) )

		return file

	# Types
	Types = { 'archive.ar': 'com.apple.product-type.library.static', 'wrapper.application': 'com.apple.product-type.application', 'compiled.mach-o.executable': 'com.apple.product-type.tool' }

	# Root
	Root = """
		{id} /* {name} */ = {
			isa = {isa};
			buildConfigurationList = {configuration.list} /* Build configuration list for PBXNativeTarget "{name}" */;
			buildPhases = (
{build.phases}
			);
			buildRules = (
			);
			dependencies = (
{dependencies}
			);
			name = {name};
			productName = {name};
			productReference = {product.id} /* {product.fileName} */;
			productType = "{product.type}";
		};
"""

# class Dependency
class Dependency( Resource ):
	# ctor
	def __init__( self, objects, target ):
		Resource.__init__( self, 'PBXTargetDependency', target.name )

		self.proxy  = objects.createContainerItemProxy( target )
		self.target = target

	# compile
	def compile( self ):
		return Template( Dependency.Root ).compile( { 'id': self.id, 'isa': self.isa, 'target.id': self.target.id, 'target.name': self.target.name, 'proxy': self.proxy.id } )

	# Root
	Root = """
		{id} /* {isa} */ = {
			isa = {isa};
			target = {target.id} /* {target.name} */;
			targetProxy = {proxy} /* PBXContainerItemProxy */;
		};
"""

# class ContainerItemProxy
class ContainerItemProxy( Resource ):
	# ctor
	def __init__( self, target, project ):
		Resource.__init__( self, 'PBXContainerItemProxy', target.name )

		self.target  = target
		self.project = project

	# compile
	def compile( self ):
		return Template( ContainerItemProxy.Root ).compile( { 'id': self.id, 'isa': self.isa, 'portal': self.project.id, 'target.id': self.target.id, 'target.name': self.target.name } )

	# Root
	Root = """
		{id} /* {isa} */ = {
			isa = {isa};
			containerPortal = {portal} /* Project object */;
			proxyType = 1;
			remoteGlobalIDString = {target.id};
			remoteInfo = {target.name};
		};
"""

# class StaticLibrary
class StaticLibrary( Target ):
	# ctor
	def __init__( self, objects, group, name, path, configurations, defaultConfiguration ):
		Target.__init__( self, objects, group, 'archive.ar', name, path, configurations, defaultConfiguration )

# class Application
class Application( Target ):
	# ctor
	def __init__( self, objects, group, name, path, configurations, defaultConfiguration ):
		Target.__init__( self, objects, group, 'compiled.mach-o.executable', name, path, configurations, defaultConfiguration )

# class ApplicationBundle
class ApplicationBundle( Target ):
	# ctor
	def __init__( self, objects, group, name, path, configurations, defaultConfiguration, team ):
		Target.__init__( self, objects, group, 'wrapper.application', name, path, configurations, defaultConfiguration )
		self.team           = team
		self.resources      = None
		self.resourcePhase  = self.objects.createResourcePhase( self )

	# compileAttributes
	def compileAttributes( self ):
		return Template( ApplicationBundle.Attributes ).compile( { 'id': self.id, 'team': self.team } )

	# addBuildPhases
	def addBuildPhases( self ):
		Target.addBuildPhases( self )

		self.phases.add( self.resourcePhase )

	# addResource
	def addResource( self, file, copyToBundle ):
		# Create Resources folder
		if not self.resources:
			self.resources = self.objects.project.addGroup( 'Resources' )

		# Add file to the group
		self.resources.add( file )

		# Add file to a build phase
		if copyToBundle:
			self.resourcePhase.add( self.objects.createBuildFile( self, file ) )

	# addResourceFile
	def addResourceFile( self, name ):
		# Create file reference for icon.xcassets
		file = self.objects.createFileReference( 'file', name, '"<group>"' )

		# Add file to a group
		self.addResource( file, True )

	# addPlist
	def addPlist( self, name ):
		# Create file reference for plist
		file = self.objects.createFileReference( 'text.plist.xml', name, '"<group>"' )

		# Add file to a group
		self.addResource( file, False )

		# Set the target plist property
		self.configurationList.forEach( lambda c: c.set( 'INFOPLIST_FILE', '"{0}"'.format( name ) ) )

	# addAssetCatalog
	def addAssetCatalog( self, name ):
		# Create file reference for icon.xcassets
		file = self.objects.createFileReference( 'folder.assetcatalog', name, '"<group>"' )

		# Add file to a group
		self.addResource( file, True )

	# setIcon
	def setAppIcon( self, name ):
		self.configurationList.forEach( lambda c: c.set( 'ASSETCATALOG_COMPILER_APPICON_NAME', name ) )

	# setLaunchImage
	def setLaunchImage( self, name ):
		self.configurationList.forEach( lambda c: c.set( 'ASSETCATALOG_COMPILER_LAUNCHIMAGE_NAME', name ) )

	# Attributes
	Attributes = """
					{id} = {
						DevelopmentTeam = {team};
					};
"""