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
import string

class Generator:
	# ctor
	def __init__( self ):
		self.sourceProject = None
		self.binaryDir     = None
		self.sourceDir     = None
		self.makefile      = None

	# getPathForTarget
	def getPathForTarget( self, target ):
		return os.path.join( self.binaryDir, target.name + '.dir' )

	# initialize
	def initialize( self, makefile, source, binary, project ):
		self.makefile       = makefile
		self.sourceDir      = source
		self.binaryDir      = binary
		self.sourceProject  = project

	# generate
	def generate( self ):
		# Create project folder
		if not os.path.exists( self.binaryDir ):
			os.makedirs( self.binaryDir )

		self.forEachTarget( self.generateTarget )

	# generateTarget
	def generateTarget( self, name, target ):
		path = self.getPathForTarget( target )

		# Create target folder
		if not os.path.exists( path ):
			os.makedirs( path )

		if not os.path.exists( path + '/obj' ):
			os.makedirs( path + '/obj' )

	# processEachTarget
	def processEachTarget( self, processor, filter = None ):
		# callback
		def callback( name, target ):
			callback.result += processor( name, target )

		callback.result = ''
		self.forEachTarget( callback, filter )

		return callback.result

	# processEachTargetSource
	def processEachTargetSource( self, target, filter, processor ):
		# callback
		def callback( filePath, baseName, ext ):
			callback.result += processor( target, filePath, baseName, ext )

		callback.result = ''
		self.forEachTargetSource( target, callback, filter )

		return callback.result

	# processEachGroup
	def processEachGroup( self, target, processor ):
		# callback
		def callback( path, files ):
			callback.result += processor( target, path, files )

		callback.result = ''
		self.forEachGroup( target, callback )

		return callback.result

	# processEachTargetInclude
	def processEachTargetInclude( self, target, processor ):
		# callback
		def callback( path ):
			callback.result += processor( path )

		callback.result = ''
		self.forEachTargetInclude( target, callback )

		return callback.result

	# processEachTargetDefine
	def processEachTargetDefine( self, target, processor ):
		# callback
		def callback( define ):
			callback.result += processor( target, define )

		callback.result = ''
		self.forEachTargetDefine( target, callback )

		return callback.result

	# processEachTargetCommand
	def processEachTargetCommand( self, target, processor ):
		# callback
		def callback( target, command ):
			result = processor( target, command )

			if result != None:
				callback.result += result

		callback.result = ''

		for command in target.commands:
			callback( target, command )

		return callback.result

	# processEachTargetLib
	def processEachTargetLib( self, target, processor ):
		# callback
		def callback( library ):
			result = processor( library )

			if result != None:
				callback.result += result

		callback.result = ''
		self.forEachTargetLibrary( target, callback )

		return callback.result

	# processEachTargetLibrarySearchPath
	def processEachTargetLibrarySearchPath( self, target, processor ):
		# callback
		def callback( library ):
			result = processor( library )

			if result != None:
				callback.result += result

		callback.result = ''
		self.forEachTargetLibrarySearchPath( target, callback )

		return callback.result

	# processEachTargetFramework
	def processEachTargetFramework( self, target, processor ):
		# callback
		def callback( target, name, lib ):
			result = processor( target, name, lib )

			if result != None:
				callback.result += result

		callback.result = ''
		self.forEachTargetFramework( target, callback )

		return callback.result

	# forEachTargetSource
	def forEachTargetSource( self, target, callback, filter = None ):
		for file in target.filterSourceFiles( filter ):
			callback( file )

	# forEachTarget
	def forEachTarget( self, callback, filter = None ):
		for target in self.sourceProject.filterTargets( filter ):
			callback( target.name, target )

	# forEachTargetLibrarySearchPath
	def forEachTargetLibrarySearchPath( self, target, callback ):
		for libraries in target.filterPaths( lambda path: path.isLibraries ):
			callback( libraries )

		# Run a callback for all dependencies
		for library in target.filterLibraries():
			target = self.findTargetByName( library.name )

			if target:
				self.forEachTargetLibrarySearchPath( target, callback )

	# forEachTargetLibrary
	def forEachTargetLibrary( self, target, callback ):
		# Run a callback for all target's libraries
		for lib in target.filterLibraries():
			callback( lib )

		# Run a callback for all dependencies
		for library in target.filterLibraries():
			target = self.findTargetByName( library.name )

			if target:
				self.forEachTargetLibrary( target, callback )

	# forEachTargetFramework
	def forEachTargetFramework( self, target, callback ):
		# Run a callback for all target's frameworks
		for framework in target.filterLibraries( lambda lib: lib.framework ):
			callback( target, framework.name, None )

		# Run a callback for all dependencies
		for library in target.filterLibraries():
			target = self.findTargetByName( library.name )

			if target:
				self.forEachTargetFramework( target, callback )

	# findTargetByName
	def findTargetByName( self, name ):
		for target in self.sourceProject._targets:
			if target.name == name:
				return target

		return None

	# getLibsForTarget
	def getLibsForTarget( self, target ):
		result = []

		for library in target.libraries:
			result.append( library )

		return result

	# forEachTargetInclude
	def forEachTargetInclude( self, target, callback ):
		path = self.getPathForTarget( target )

		# Project include paths
		if target != self.sourceProject:
			self.forEachTargetInclude( self.sourceProject, callback )

		# Target
		for path in target.filterPaths( lambda path: path.isHeaders ):
			callback( path )

	# forEachTargetDefine
	def forEachTargetDefine( self, target, callback ):
		# Project defines
		if target != self.sourceProject:
			self.forEachTargetDefine( self.sourceProject, callback )

		# Target
		for define in target.defines:
			callback( define )

	# forEachCommand
	def forEachCommand( self, target, callback ):
		for cmd in target.commands:
			callback( cmd )

	# forEachGroup
	def forEachGroup( self, target, callback ):
		# iterator
		def iterator( group ):
			for name in group.groups:
				iterator( group.groups[name] )

			path = os.path.relpath( group.path, target.name )
			if path == '.':
				return

			callback( path, group.files )

		iterator( target.groups )

	###

	# listLibraries
	def listLibraries( self, target, filter = None ):
		# List all target's libraries
		libraries = target.filterLibraries( filter )

		# List libraries for all dependencies
		dependencies = []

		for library in libraries:
			target = self.findTargetByName( library.name )

			if target:
				dependencies = dependencies + self.listLibraries( target, filter )

		return list( set( libraries + dependencies ) )

	# listLibraryPaths
	def listLibraryPaths( self, target ):
		# List all target's library paths
		paths = [path.path for path in target.filterPaths( lambda path: path.isLibraries )]

		# List path for project
		project = [path.path for path in target.project.filterPaths( lambda path: path.isLibraries )]

		# List paths for all dependencies
		dependencies = []

		for library in target.filterLibraries():
			target = self.findTargetByName( library.name )

			if target:
				dependencies = dependencies + self.listLibraryPaths( target )

		return list( set( paths + dependencies + project ) )

	# listHeaderPaths
	def listHeaderPaths( self, target ):
		# List all target's header paths
		paths = [path.path for path in target.filterPaths( lambda path: path.isHeaders )]

		# List paths for project
		project = [path.path for path in target.project.filterPaths( lambda path: path.isHeaders )]

		return list( set( paths + project ) )