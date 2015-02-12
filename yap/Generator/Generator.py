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
			callback.result += processor( target, path )

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
	#	path = self.getPathForTarget( target )

	#	for source in target.sources:
		#	fileName		= os.path.basename( source )
		#	baseName, ext 	= os.path.splitext( fileName )
		#	filePath		= string.replace( os.path.relpath( source, path ), '\\', '/' )
	#		name, ext = source.nameAndExtension

	#		if filter == None or ext in filter:
	#			callback( source.relativePath( path ), name, ext )

	# forEachTarget
	def forEachTarget( self, callback, filter = None ):
		for target in self.sourceProject.filterTargets( filter ):
			callback( target.name, target )
	#	for name, target in self.sourceProject.targets.items():
	#		if filter == None or filter == target.type:
	#			callback( name, target )

	# forEachTargetLibrary
	def forEachTargetLibrary( self, target, callback ):
		for lib in target.filterLibraries():
			callback( lib )
		# Get libs
	#	libs = []
	#	for lib in self.getLibsForTarget( target ):
	#		if not lib in libs:
	#			libs.append( lib )

	#	for name in libs:
	#		callback( target, name, self.sourceProject.findTarget( name, [Target.StaticLibrary, Target.SharedLibrary] ) )

	# forEachTargetFramework
	def forEachTargetFramework( self, target, callback ):
		for framework in target.filterFrameworks():
			callback( target, framework.name, None )
		#	if lib['framework']:
		#		callback( target, lib['name'], None )

	# findTargetByName
	def findTargetByName( self, name ):
		if name in self.sourceProject.targets.keys():
			return self.sourceProject.targets[name]

		return None

	# getLibsForTarget
	def getLibsForTarget( self, target ):
		result = []

		for library in target.libraries:
			result.append( library )
		#	name = lib['name']

		#	if not lib['framework']:
		#		result.append( name )

		#	if not name in self.sourceProject.targets.keys():
		#		continue

		#	lib = self.sourceProject.targets[name]

		#	if lib.type == 'static':
		#		libs = self.getLibsForTarget( lib )
		#		for name in libs:
		#			result.append( name )

		return result

	# forEachTargetInclude
	def forEachTargetInclude( self, target, callback ):
		path = self.getPathForTarget( target )

		# Project include paths
		if target != self.sourceProject:
			self.forEachTargetInclude( self.sourceProject, callback )

		# Target
		for include in target.filterPaths( lambda path: path.isHeaders ):
			if os.path.isabs( path ):
				include = string.replace( include.path, '\\', '/' )
			else:
				include = string.replace( os.path.relpath( include.path, path ), '\\', '/' )

			callback( include )

		# Libraries
		for library in target.filterLibraries( lambda lib: lib.type == 'external' ):
			callback( library.headers )

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
