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
from Objects        import Objects
from ObjectList     import ObjectList
from ...Template    import Template

# class Project
class Project( Resource ):
	# ctor
	def __init__( self, name, settings ):
		Resource.__init__( self, 'PBXProject', name )

		self.organization       = 'YAP'
		self.archiveVersion     = 1
		self.objectVersion      = 46
		self.objects            = Objects( self )
		self.targets            = ObjectList()
		self.configurationList  = self.objects.createConfigurationList( self, settings, 'Debug' )
		self.mainGroup          = self.objects.createGroup()
		self.sourcesGroup       = self.addGroup( 'Sources' )
		self.frameworksGroup    = self.addGroup( 'Frameworks' )
		self.productsGroup      = self.addGroup( 'Products' )

	# addGroup
	def addGroup( self, name ):
		return self.objects.createGroup( name, self.mainGroup )

	# addStaticLibrary
	def addStaticLibrary( self, name, path, settings, defaultConfiguration ):
		target = self.objects.createStaticLibrary( self.sourcesGroup, name, path, settings, defaultConfiguration )
		self.targets.add( target )
		self.productsGroup.add( target.product )

		return target

	# addApplication
	def addApplication( self, name, path, settings, defaultConfiguration ):
		target = self.objects.createApplication( self.sourcesGroup, name, path, settings, defaultConfiguration )
		self.targets.add( target )
		self.productsGroup.add( target.product )

		return target

	# addApplicationBundle
	def addApplicationBundle( self, name, path, settings, defaultConfiguration, teamIdentifier ):
		target = self.objects.createApplicationBundle( self.sourcesGroup, name, path, settings, defaultConfiguration, teamIdentifier )
		self.targets.add( target )
		self.productsGroup.add( target.product )

		return target

	# addFramework
	def addFramework( self, name ):
		framework = self.objects.createFramework( name )
		self.frameworksGroup.add( framework )
		return framework

	# addProjectLibrary
	def addProjectLibrary( self, name ):
		library = self.objects.createFileReference( 'archive.ar', 'lib' + name + '.a', 'BUILT_PRODUCTS_DIR' )
		self.frameworksGroup.add( library )
		return library

	# addLibrary
	def addLibrary( self, name ):
		library = self.objects.createFileReference( 'archive.ar', name, '"<group>"' )
		self.frameworksGroup.add( library )
		return library

	# compileTargetAttributes
	def compileTargetAttributes( self ):
		result = ''
		for target in self.targets.items:
			result += target.compileAttributes()
		return result

	# generate
	def generate( self ):
		return Template( Project.Root ).compile( { 'id': self.id, 'archive.version': self.archiveVersion, 'object.version': self.objectVersion, 'objects': self.objects.compile() } )

	# compile
	def compile( self ):
		return Template( Project.Project ).compile( {
														'id':                   self.id,
														'name':                 self.name,
		                                                'isa':                  self.isa,
		                                                'organization':         self.organization,
		                                                'target.attributes':    self.compileTargetAttributes(),
		                                                'main.group.id':        self.mainGroup.id,
		                                                'configuraion.list.id': self.configurationList.id,
		                                                'products.group.id':    self.productsGroup.id,
		                                                'project.targets':      self.targets.compileList()
													} )

	# Project
	Project = """
		{id} /* Project object */ = {
			isa = {isa};
			attributes = {
				LastUpgradeCheck = 0510;
				ORGANIZATIONNAME = {organization};
				TargetAttributes = {
{target.attributes}
				};
			};
			buildConfigurationList = {configuraion.list.id} /* Build configuration list for PBXProject "{name}" */;
			compatibilityVersion = "Xcode 3.2";
			developmentRegion = English;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
			);
			mainGroup = {main.group.id};
			productRefGroup = {products.group.id} /* Products */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
{project.targets}
			);
		};
"""

	# Root
	Root = """// !$*UTF8*$!
{
	archiveVersion = {archive.version};
	classes = {
	};
	objectVersion = {object.version};
	objects = {
{objects}
	};
	rootObject = {id} /* Project object */;
}
"""
