import os, shutil

from ..Generator import Generator
from PBX         import Project
from Template    import Template

# class Xcode5
class Xcode5( Generator ):
	# ctor
	def __init__( self ):
		Generator.__init__( self )

		self.project  = None
		self.projects = {}

	# generate
	def generate( self ):
		Generator.generate( self )

		# Create project for each target
		self.forEachTarget( self.createProjects )

		# Setup projects
		for name, project in self.projects.items():
			target = project['target']
			pbx    = project['pbx']

			self.addTargetSources( target.name, target, pbx )
			self.addTargetLibraries( target.name, target, pbx )
			self.addTargetFrameworks( target.name, target, pbx )
			self.addTargetCommands( target.name, target, pbx )
			self.saveProject( project['project'], target )

		# Create workspace
		self.generateWorkspace()

	# generateWorkspace
	def generateWorkspace( self ):
		# Create the workspace folder
		workspace = os.path.join( self.binaryDir, self.sourceProject.name + '.xcworkspace' )

		# Create folder
		if not os.path.exists( workspace ):
			os.mkdir( workspace )

		# Generate project list
		projects = ''

		for name, project in self.projects.items():
			folder    = self.getPathForTarget( project['target'] )
			projects += "<FileRef location='group:{0}'/>\n".format( os.path.join( folder, name + '.xcodeproj') )

		# Dump workspace to file
		Template( Xcode5.Workspace ).compileToFile( os.path.join( workspace, 'contents.xcworkspacedata' ), { 'projects': projects } )

	# saveProject
	def saveProject( self, project, target ):
		# Create project folder
		folder = os.path.join( self.getPathForTarget( target ), target.name + '.xcodeproj' )

		if not os.path.exists( folder ):
			os.mkdir( folder )

		# Dump project to disk
		file = open( os.path.join( folder, 'project.pbxproj' ), 'wt' )
		file.write( project.generate() )
		file.close()

	# createProjects
	def createProjects( self, name, target ):
		settings = {
			'Debug':    self.generateConfiguration( target, 'Debug' ),
		    'Release':  self.generateConfiguration( target, 'Release' )
		}

		# Create project
		project = Project( target.name, self.getProjectSettings() )
		pbx     = None

		# Create target
		if target.type == 'executable':
			pbx = project.addApplicationBundle( name, name + '.app', settings, 'Debug', self.makefile.get( 'DEVELOPMENT_TEAM' ) )
			self.addInfoPlist( target, pbx )
			if target.resources:
				self.addResources( target, pbx )
		else:
			pbx = project.addStaticLibrary( name, 'lib' + name + '.a', settings, 'Debug' )

		self.projects[name] = { 'project': project, 'target': target, 'pbx': pbx }

	# getProjectSettings
	def getProjectSettings( self ):
		return None

	# getPlatformId
	def getPlatformId( self ):
		return None

	# addInfoPlist
	def addInfoPlist( self, target, pbx ):
		pbx.addPlist( 'Info.plist' )
		Template( Xcode5.Plist ).compileToFile( os.path.join( self.getPathForTarget( target ), 'Info.plist' ), {
																										'identifier':       self.makefile.get( 'IDENTIFIER' ),
																										'version':          self.makefile.get( 'VERSION' ),
																										'short.version':    self.makefile.get( 'SHORT_VERSION' ),
		                                                                                                'facebook.app.id':  self.makefile.get( 'FACEBOOK_APP_ID' )
																									} )

	# addResources
	def addResources( self, target, pbx ):
		icons  = os.path.join( target.sourcePath, target.resources, 'images', 'icons.'  + self.getPlatformId() )
		launch = os.path.join( target.sourcePath, target.resources, 'images', 'launch.' + self.getPlatformId() )
		assets = os.path.join( target.sourcePath, target.resources, 'assets', 'assets.dpk' )

		# Icons
		if os.path.exists( icons ):
			dst = os.path.join( self.getPathForTarget( target ), 'icons.xcassets' )
			if os.path.exists( dst ):
				shutil.rmtree( dst )

			shutil.copytree( icons, dst )

			pbx.addAssetCatalog( 'icons.xcassets' )
			pbx.setAppIcon( 'Icon' )

		# Launch images
		if os.path.exists( launch ):
			dst = os.path.join( self.getPathForTarget( target ), 'launch.xcassets' )
			if os.path.exists( dst ):
				shutil.rmtree( dst )

			shutil.copytree( launch, dst )

			pbx.addAssetCatalog( 'launch.xcassets' )
			pbx.setLaunchImage( 'Launch' )

		# Assets
		if os.path.exists( assets ):
			dst = os.path.join( self.getPathForTarget( target ), 'assets.dpk' )

			shutil.copyfile( assets, dst )

			pbx.addResourceFile( 'assets.dpk' )

	# addTargetCommands
	def addTargetCommands( self, name, target, pbx ):
		# No commands for target
		if len( target.commands ) == 0:
			return

		# Add shell script
		pbx.addShellScript( 'make -C {0} -f {1}.commands'.format( self.getPathForTarget( target ), name ) )

		# Generate makefile
		commands = self.processEachTargetCommand( target, self.compileCommand )
		depends  = self.processEachTargetCommand( target, self.compileDependency )
		Template( Xcode5.CodegenScript ).compileToFile( os.path.join( self.getPathForTarget( target ), name + '.commands' ), { 'depends': depends, 'commands': commands } )

	# addTargetSources
	def addTargetSources( self, name, target, pbx ):

		# addSourceFile
		def addSourceFile( filePath, baseName, ext ):
			fullPath   = os.path.normpath( os.path.join( target.binaryPath, filePath ) )
			sourcePath = os.path.normpath( target.sourcePath )

			if not fullPath.startswith( sourcePath ):
				groupPath = os.path.join( 'GeneratedFiles', os.path.dirname( filePath ) )
				addSourceFile.target.addGeneratedFile( filePath )
			else:
				groupPath = os.path.dirname( os.path.relpath( fullPath, sourcePath ) )
				addSourceFile.target.addSourceFile( filePath, groupPath )

		# Add source files to target
		addSourceFile.target = pbx
		self.forEachTargetSource( target, addSourceFile )

	# addTargetFrameworks
	def addTargetFrameworks( self, name, target, pbx ):

		# addFramework
		def addFramework( target, name, library ):
			if name.endswith( '.framework' ) and not os.path.isabs( name ):
				name = os.path.join( self.sourceDir, name )

			addFramework.target.addFramework( name )

		# Add global frameworks
		addFramework.target = pbx
		self.forEachTargetFramework( target, addFramework )
		
	# addTargetLibraries
	def addTargetLibraries( self, name, target, pbx ):

		# addLibrary
		def addLibrary( target, name, library ):
			if not name in self.projects.keys():
				folder = os.path.dirname( name )
				name   = 'lib' + os.path.basename( name ) + '.a'
				addLibrary.target.addLibrary( os.path.join( self.sourceDir, os.path.join( folder, name ) ) )
			else:
				addLibrary.target.addProjectLibrary( self.projects[name]['pbx'] )

		# Add linked libraries
		addLibrary.target = pbx
		self.forEachTargetLibrary( target, addLibrary )

	# compileCommand
	def compileCommand( self, target, cmd ):
		output = ''
		for ext in cmd.generatedExtensions:
			output += cmd.output + ext + ' '

		input = ''
		for fileName in cmd.input:
			input += fileName + ' '

		return Template( Xcode5.CodegenCommand ).compile( { 'output': output, 'input': input, 'command': cmd.command, 'message': cmd.message } )

	# compileDependency
	def compileDependency( self, target, cmd ):
		result = ''

		for ext in cmd.generatedExtensions:
			result += '\\\n\t' + cmd.output + ext

		return result

	# generateConfiguration
	def generateConfiguration( self, target, name ):
		# generateHeaderIncludePaths
		def generateHeaderIncludePaths( target, path ):
			return ' ' + path + ' '

		# generateDefines
		def generateDefines( target, define ):
			return ' ' + define + ' '

		paths   = self.processEachTargetInclude( target, generateHeaderIncludePaths ).split( ' ' )
		defines = self.processEachTargetDefine( target, generateDefines ).split( ' ' )
		paths   = set( paths )
		paths   = list( paths )
		paths.append( '$(inherited)' )

		return { 'PRODUCT_NAME': '"$(TARGET_NAME)"', 'HEADER_SEARCH_PATHS': paths, 'GCC_PREPROCESSOR_DEFINITIONS': defines }

	CodegenCommand = """
{output}: {input}
	@echo '{message}'
	@{command}
	"""

	CodegenScript = """
all: {depends}

{commands}
"""

	Plist = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>{identifier}</string>
	<key>CFBundleShortVersionString</key>
	<string>{short.version}</string>
	<key>CFBundleVersion</key>
	<string>{version}</string>
	<key>CFBundleVersion</key>
	<string>{version}</string>
	<key>CFBundleExecutable</key>
	<string>${PRODUCT_NAME}</string>
	<key>FacebookAppID</key>
	<string>{facebook.app.id}</string>
</dict>
</plist>
"""

	Workspace = """<?xml version='1.0' encoding='UTF-8'?>
<Workspace version='1.0'>
{projects}
</Workspace>
"""