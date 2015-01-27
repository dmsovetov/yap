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

import string, os, glob, Makefile, Extensions

# class Target
class Target:
	Ident = 0

	Extensions = {
		'RTTI': Extensions.RTTI,
	    'Qt':   Extensions.Qt
	}

	# ctor
	def __init__( self, name, project = None ):
		self.message( 'Configure ' + name + '...' )

		self.project 	= project
		self.name		= name
		self.type		= None
		self.params		= {}
		self.ext        = []
		self.sourcePath	= Makefile.getCurrentSourceDir()

		if project:
			self.binaryPath = project.generator.getPathForTarget( self )
			self.ext.extend( project.ext )
		else:
			self.binaryPath = Makefile.getCurrentBinaryDir()

		self.sources 	    = []
		self.javaPackages   = []
		self.commands 	    = []
		self.libs 		    = []
		self.defines   	    = []
		self.includes 	    = []
		self.groups		    = None
		self.resources      = None

		self.include( self.binaryPath )

		# WORKAROUND
		if project:
			project.include( project.generator.getPathForTarget( self ) )

		# Register this target
		if project:
			project.registerTarget( self )

		Target.Ident = Target.Ident + 1

	# getGenerator
	def getGenerator( self ):
		return self.project.generator if self.project else self.generator

	# registerExtension
	def registerExtension( self, name, ext ):
		Target.Extensions[name] = ext

	# extensions
	def extensions( self, *list ):
		for ext in list:
			if not ext in Target.Extensions.keys():
				raise Exception( 'Unknown extension {0}'.format( ext ) )

			self.message( 'Extension {0} enabled'.format( ext ) )
			self.ext.append( Target.Extensions[ext]( self, Makefile ) )

	# message
	@classmethod
	def message( self, text ):
		msg = ''
		for i in range( 0, Target.Ident * 4 ):
			msg += ' '
		print( msg + text )

	# group
	def group( self, path, files ):
		# class Group
		class Group:
			# ctor
			def __init__( self, target, name, parent = None ):
				self.target     = target
				self.name 		= name
				self.parent  	= parent
				self.path 		= name if parent == None else os.path.join( parent.path, name )
				self.groups		= {}
				self.files 		= []

		if self.groups == None:
			self.groups = Group( self, self.name )

		# getOrCreateGroup
		def getOrCreateGroup( path ):
			group = self.groups

			for name in path.replace( '\\', '/' ).split( '/' ):
				if not name in group.groups.keys():
					group.groups[name] = Group( self, name, group )

				group = group.groups[name]

			return group

		if path == '.':
			path = 'Code'
		elif path != 'GeneratedFiles':
			path = 'Code/' + path

		insertTo = getOrCreateGroup( path )

		for file in files:
			fileName = os.path.relpath( file, self.getGenerator().getPathForTarget( self ) )
			if not fileName in insertTo.files:
				insertTo.files.append( fileName )
			else:
				print 'WARNING: file {0} duplicate found inside group {1}'.format( os.path.basename( fileName ), path )

	# embed
	def embed( self, fileName, identifier ):
		fileName 		= os.path.join( self.sourcePath, fileName )
		name, ext 	 	= os.path.splitext( os.path.basename( fileName ) )
		outputFileName	= os.path.join( self.getGenerator().getPathForTarget( self ), 'embedded' + name.title() )
		cmd 		 	= 'python ' + os.path.join( Makefile.SourceDir, '../tools/scripts/EmbedFile.py' ) + ' ' + fileName + ' ' + outputFileName + '.h' + ' ' + 'embedded' + name.title()

		self.command( [ fileName ], outputFileName, cmd, '(Embedding)...', ['.h'] )

	# java
	def java( self, package ):
		if not package.startswith( self.sourcePath ):
			package = os.path.join( self.sourcePath, package )

		self.javaPackages.append( package )

	# files
	def files( self, *list ):
		# Workaround for self.dirs method
		if type( list[0] ) == tuple:
			list = list[0]
		#################################

		for inputFileName in list:
			fileName  = inputFileName.replace( '\\', '/' )
			extension = os.path.splitext( fileName )[1]

			if not fileName.startswith( self.sourcePath ):
				fileName = os.path.join( self.sourcePath, fileName )

			# Check extensions
			wrapped = False
			for ext in self.ext:
				wrapped = wrapped or ext.wrap( self, self.getGenerator(), fileName, extension )

			if not wrapped and not extension in ['.c', '.cpp', '.h', '.m', '.mm', '.cxx', '.inl', '.plist']:
				continue

			if fileName.find( self.binaryPath ) == -1:
				folder = os.path.relpath( os.path.dirname( fileName ), self.sourcePath )
				self.group( folder, [ fileName ] )
				
			self.sources.append( fileName )

	# command
	def command( self, input, output, command, message, generatedExtensions = None ):
		# class Command
		class Command:
			def __init__( self ):
				self.output  				= output
				self.message 				= message
				self.command 				= command
				self.input	 				= input
				self.generatedExtensions	= generatedExtensions

		self.commands.append( Command() )

		if generatedExtensions != None:
			for ext in generatedExtensions:
				self.sources.append( os.path.join( self.binaryPath, os.path.basename( output ) ) + ext )
				self.group( 'GeneratedFiles', [ output + ext ] )

	# dirs
	def dirs( self, *list ):
		for inputFolder in list:
			path = os.path.join( self.sourcePath, inputFolder )

			# Asterisk folder path
			if path.endswith( '/*' ):
				for folder in glob.glob( path ):
					if os.path.isdir( folder ):
						self.dirs( os.path.relpath( folder, Makefile.getCurrentSourceDir() ) )

				continue

			# Get the file list
			fileList = tuple( glob.glob( path + '/*.*' ) )

			# Add files to project
			self.files( fileList )

	# link
	def link( self, *list ):
		for lib in list:
			self.message( 'Dependent on ' + lib )
			self.libs.append( { 'name': lib, 'framework': False } )

	# frameworks
	def frameworks( self, *list ):
		for framework in list:
			# Check extensions
			for ext in self.ext:
				if hasattr( ext, 'framework' ):
					framework = ext.framework( framework )


			self.message( 'Uses ' + framework )
			self.libs.append( { 'name': framework, 'framework': True } )

	# define
	def define( self, *list ):
		for define in list:
			self.defines.append( define )

	# include
	def include( self, *list ):
		for path in list:
			path = string.replace( path, '\\', '/' )
			if not os.path.isabs( path ):
				self.includes.append( os.path.join( Makefile.getCurrentSourceDir(), path ) )
			else:
				self.includes.append( path )

	# assets
	def assets( self, path ):
		self.message( 'Assets ' + path )
		self.resources = path

	# sharedLibrary
	def sharedLibrary( self ):
		self.message( 'Configured as shared library' )
		self.type = 'shared'

		Target.Ident = Target.Ident - 1

	# staticLibrary
	def staticLibrary( self ):
		self.message( 'Configured as static library' )
		self.type = 'static'

		Target.Ident = Target.Ident - 1

	# executable
	def executable( self, **params ):
		self.message( 'Configured as executable' )
		self.type   = 'executable'
		self.params = params

		Target.Ident = Target.Ident - 1