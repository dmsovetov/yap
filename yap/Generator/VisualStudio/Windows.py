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

import os, uuid, codecs

from ..Generator import Generator
from ..Template  import Template

# ID
def ID():
	return '{' + str( uuid.uuid1() ).upper() + '}'

# Open
def Open( fileName ):
	return codecs.open( fileName, "w", "utf-8-sig" )

# class Windows
class Windows( Generator ):
	# constructor
	def __init__( self ):
		Generator.__init__( self )

		self.id 		= ID()
		self.projects 	= {}

	# generate
	def generate( self ):
		print( 'Generating Win32 project...' )
		Generator.generate( self )

		self.generateSolutionProjects()
		self.generateSolution()
		
	# generateSolution
	def generateSolution( self ):
		file = Open( os.path.join( self.binaryDir, self.sourceProject.name + '.sln' ) )
		file.write( Template( Windows.Solution ).compile( 	{
																	'projects':			self.compileSolutionProjects(),
																	'configurations':	self.compileSolutionConfigurations(),
																}, True ) )
		file.close()

	# generateSolutionProjects
	def generateSolutionProjects( self ):
		# Project
		class Project:
			def __init__( self, name, path ):
				self.id   		 = ID()
				self.name 		 = name
				self.files		 = {}
				self.fileName	 = os.path.join( path, name + '.vcxproj' )
				self.filtersFile = self.fileName + '.filters'

		# addTargetProject
		def addTargetProject( name, target ):
			path = self.getPathForTarget( target )
			self.projects[name] = Project( name, os.path.relpath( path, self.binaryDir ) )

		# Generate project list
		self.forEachTarget( addTargetProject )

		# Generate project file
		for name in self.projects:
			project = self.projects[name]
			
			# Add proxy files for commands
			self.generateProxyFiles( project )

			# Generate
			file = Open( os.path.join( self.binaryDir, project.fileName ) )
			file.write( Template( Windows.Project ).compile( 	{
																		'configuration.list': 	Windows.ProjectConfigurationList,
																		'id':					project.id,
																		'name':					project.name,
																		'configurations':		self.generateConfigurations( project ),
																		'settings':				self.generateSettings( project ),
																		'commands':				self.generateCommands( project ),
																		'items':				self.generateItems( project ),
																	}, True ) )
			file.close()

			file = Open( os.path.join( self.binaryDir, project.filtersFile ) )
			file.write( Template( Windows.Filters ).compile( 	{
																		'groups': 	self.generateFilterGroups( project ),
																		'compile':	self.generateFilterFiles( project, Windows.FilterCompileItem, ['.c', '.cpp'] ),
																		'headers':	self.generateFilterFiles( project, Windows.FilterHeaderItem, ['.h'] ),
																		'commands':	self.generateFilterFiles( project, Windows.FilterRuleItem, ['.rule'] ),
																	}, True ) )
			file.close()

	# generateFilterGroups
	def generateFilterGroups( self, project ):
		target = self.findTargetByName( project.name )

		# generateFilterGroup
		def generateFilterGroup( target, path, files ):
			return Template( Windows.FilterGroup ).compile( { 'path': path, 'id': ID() }, True )

		return self.processEachGroup( target, generateFilterGroup )

	# generateFilterFiles
	def generateFilterFiles( self, project, tpl, filter ):
		target = self.findTargetByName( project.name )

		# generateFilterItems
		def generateFilterGroup( target, path, files ):
			result = ''

			for fileName in files:
				name, ext = os.path.splitext( fileName )
				if ext in filter:
					result += Template( tpl ).compile( { 'fileName': fileName, 'path': path }, True )

			return result

		return self.processEachGroup( target, generateFilterGroup )

	# def generateProjectLinker
	def generateProjectLinker( self, project, debug ):
		target  = self.findTargetByName( project.name )

		if target.type != 'executable' and target.type != 'shared':
			return ''

		# generateLibs
		def generateLibs( target, name, lib ):
			return name + '.lib;'

		options  	= ' /machine:X86 ' + ('/debug ' if debug else '')
		output 	 	= os.path.join( self.binaryDir, '$(Configuration)' )
		libs     	= self.processEachTargetLib( target, generateLibs )
		library  	= os.path.join( output, project.name + '.lib' )
		pdb 	 	= os.path.join( output, project.name + '.pdb' )
		subsystem 	= 'Windows'
		
		if 'subsystem' in target.params.keys():
			subsystem = 'Console' if target.params['subsystem'] == 'console' else 'Windows'
		
		# Add Qt to library paths
		if debug:
			libs = libs.replace( 'QtCore', 'QtCored4' ).replace( 'QtGui', 'QtGuid4' ).replace( 'QtOpenGL', 'QtOpenGLd4' )
		else:
			libs = libs.replace( 'QtCore', 'QtCore4' ).replace( 'QtGui', 'QtGui4' ).replace( 'QtOpenGL', 'QtOpenGL4' )

		if libs.find( 'Qt' ) != -1:
			Qt = self.makefile.get( 'Qt' )

			if Qt == None or not os.path.exists( Qt ):
				print 'ERROR: no Qt path set'
			else:
				output += ';' + os.path.join( Qt, 'lib' )

		return Template( Windows.Link ).compile( 	{
															'libs': 			libs,
															'lib.path':			output,
															'options': 			options,
															'is.debug':			'true' if debug else 'false',
															'subsystem':		subsystem,
															'import.library': 	library,
															'pdb':				pdb,
														}, True )

	# generateConfigurations
	def generateConfigurations( self, project ):
		result = ''
		type   = { 'shared': 'DynamicLibrary', 'static': 'StaticLibrary', 'executable': 'Application' }
		target = self.findTargetByName( project.name )

		result += Template( Windows.ConfigurationPropertyGroup ).compile( { 'configuration': 'Debug|Win32', 'type': type[target.type] }, True )
		result += Template( Windows.ConfigurationPropertyGroup ).compile( { 'configuration': 'Release|Win32', 'type': type[target.type] }, True )

		return result

	# generateProxyFiles
	def generateProxyFiles( self, project ):
		target = self.findTargetByName( project.name )

		# generateCommand
		def generateCommand( target, cmd ):
			fileName = os.path.join( self.getPathForTarget( target ), os.path.basename( cmd.output ) + '.rule' )
			
			fp = open( fileName, 'wt' )
			fp.write( '# Generated by YAP' )
			fp.close()
			
			target.files( fileName )
			target.group( 'GeneratedFiles', [fileName] )

		self.processEachTargetCommand( target, generateCommand )		

	# generateCommands
	def generateCommands( self, project ):
		result = ''
		target = self.findTargetByName( project.name )

		# generateCommand
		def generateCommand( target, cmd ):
			input   = ''
			output  = ''
			message = 'Generating'

			for ext in cmd.generatedExtensions:
				output  += cmd.output + ext + ';'
				message += ' ' + os.path.basename( cmd.output + ext )
				
			message += '...'

			path 	 = self.getPathForTarget( target )
			fileName = os.path.join( path, os.path.basename( cmd.output ) )
			input 	 = os.path.relpath( fileName + '.rule', path )
			
			header  = Template( Windows.CommandHeader ).compile( { 'input': input } )
			command = Template( Windows.Command ).compile( { 'command': cmd.command, 'message': message, 'input': input, 'output': output, 'additional.input': cmd.input[0] }, True )
			footer  = Template( Windows.CommandFooter ).compile( {} )

			return header + command + footer

		return self.processEachTargetCommand( target, generateCommand )

	# generateSettings
	def generateSettings( self, project ):
		result = ''

		includes 	 = ''
		preprocessor = ''
		target   	 = self.findTargetByName( project.name )
		path 	 	 = self.getPathForTarget( target )

		def generateInclude( target, path ):
			return path + ';'

		def generateDefine( target, define ):
			return define + ';'

		includes 	 = self.processEachTargetInclude( target, generateInclude )
		preprocessor = self.processEachTargetDefine( target, generateDefine )

		# Debug
		result += Template( Windows.ProjectConfiguration ).compile( {
																			'configuration': 	'Debug|Win32',
																			'inline.function':	'Disabled',
																			'debug.format':		'ProgramDatabase',
																			'optimization': 	'Disabled',
																			'includes':			includes,
																			'preprocessor':		'_DEBUG;' + preprocessor,
																			'runtime.lib':		'MultiThreadedDebugDLL',
																			'link':				self.generateProjectLinker( project, True ),
																		 }, True )

		# Release
		result += Template( Windows.ProjectConfiguration ).compile( {
																			'configuration': 	'Release|Win32',
																			'inline.function':	'AnySuitable',
																			'debug.format':		'',
																			'optimization': 	'MaxSpeed',
																			'includes':			includes,
																			'preprocessor':		preprocessor,
																			'runtime.lib':		'MultiThreadedDLL',
																			'link':				self.generateProjectLinker( project, False ),
																		 }, True )

		return result

	# generateItems
	def generateItems( self, project ):
		result 	= ''
		target 	= self.findTargetByName( project.name )
		path 	= self.getPathForTarget( target )
		files	= project.files

		# Files
		for fileName in target.sources:
			name, ext 	= os.path.splitext( os.path.basename( fileName ) )
			filePath  	= os.path.relpath( fileName, path )
			objFileName = name.upper() + ext + '.obj'
			
			# Generate valid obj file name
			if objFileName in files.keys():
				files[objFileName] = files[objFileName] + 1
				objFileName 	   += str( files[objFileName] )
				objFilePath		   = '<ObjectFileName>$(Configuration)\\{0}</ObjectFileName>'.format( objFileName )
			else:
				objFilePath		   = ''
				files[objFileName] = 1

			if ext == '.h':
				result += Template( Windows.ItemHeader ).compile( { 'fileName': filePath }, True )
			elif ext == '.cpp':
				result += Template( Windows.ItemCpp ).compile( { 'fileName': filePath, 'obj.fileName': objFilePath }, True )
			elif ext == '.c':
				result += Template( Windows.ItemC ).compile( { 'fileName': filePath, 'obj.fileName': objFilePath }, True )

		return result
		
	################################### TEMPLATE COMPILERS
		
	# compileSolutionProjects
	def compileSolutionProjects( self ):
		result 		 = ''

		for name in self.projects:
			project 	 = self.projects[name]
			target 	 	 = self.findTargetByName( name )
			dependencies = ''
			
			for lib in target.libs:
				if lib in self.sourceProject.targets.keys():
					dependencies += Template( Windows.SolutionDependency ).compile( { 'uuid': self.projects[lib].id }, True )
			
			result += Template( Windows.SolutionProject ).compile( {
																 			'solution.id': 	self.id,
																 			'name': 		project.name,
																 			'id':			project.id,
																 			'fileName':		project.fileName,
																			'dependencies':	dependencies,
																		}, True )

		return result
			
	# compileSolutionConfigurations
	def compileSolutionConfigurations( self ):
		result = ''

		for name in self.projects:
			result += Template( Windows.SolutionProjectConfigurations ).compile( { 'id': self.projects[name].id }, True )

		return result
		
	################################### TEMPLATES
	
	Solution = """
Microsoft Visual Studio Solution File, Format Version 11.00
# Visual Studio 2010
{projects}
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Win32 = Debug|Win32
		Release|Win32 = Release|Win32
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution{configurations}
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
"""

	SolutionProject = """
Project("{solution.id}") = "{name}", "{fileName}", "{id}"
{dependencies}
EndProject"""

	SolutionDependency = """
	ProjectSection(ProjectDependencies) = postProject
		{uuid} = {uuid}
	EndProjectSection
"""

	SolutionProjectConfigurations = """
		{id}.Debug|Win32.ActiveCfg = Debug|Win32
		{id}.Debug|Win32.Build.0 = Debug|Win32
		{id}.Release|Win32.ActiveCfg = Release|Win32
		{id}.Release|Win32.Build.0 = Release|Win32"""

	ProjectProperty = """
<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='{configuration}'" Label="Configuration">
    <ConfigurationType>{type}</ConfigurationType>
    <UseOfMfc>false</UseOfMfc>
    <CharacterSet>MultiByte</CharacterSet>
</PropertyGroup>
"""

	ProjectConfiguration = """
<ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='{configuration}'">
  <ClCompile>
    <AdditionalOptions>/MP8 /Zm1000 %(AdditionalOptions)</AdditionalOptions>
    <AdditionalIncludeDirectories>{includes}%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>
    <CompileAs>CompileAsCpp</CompileAs>
    <ExceptionHandling>Sync</ExceptionHandling>
    <InlineFunctionExpansion>{inline.function}</InlineFunctionExpansion>
    <Optimization>{optimization}</Optimization>
    <RuntimeLibrary>{runtime.lib}</RuntimeLibrary>
    <RuntimeTypeInfo>true</RuntimeTypeInfo>
    <WarningLevel>Level3</WarningLevel>
    <DebugInformationFormat>{debug.format}</DebugInformationFormat>
    <PreprocessorDefinitions>WIN32;_WINDOWS;_CRT_SECURE_NO_WARNINGS;{preprocessor}%(PreprocessorDefinitions)</PreprocessorDefinitions>
    <AssemblerListingLocation>Release</AssemblerListingLocation>
    <ObjectFileName>$(IntDir)</ObjectFileName>
  </ClCompile>
  <ResourceCompile>
    <PreprocessorDefinitions>WIN32;_WINDOWS;_CRT_SECURE_NO_WARNINGS;{preprocessor}%(PreprocessorDefinitions)</PreprocessorDefinitions>
    <AdditionalIncludeDirectories>{includes}%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>
  </ResourceCompile>
  <Midl>
    <AdditionalIncludeDirectories>{includes}%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>
    <OutputDirectory>$(IntDir)</OutputDirectory>
    <HeaderFileName>%(Filename).h</HeaderFileName>
    <TypeLibraryName>%(Filename).tlb</TypeLibraryName>
    <InterfaceIdentifierFileName>%(Filename)_i.c</InterfaceIdentifierFileName>
    <ProxyFileName>%(Filename)_p.c</ProxyFileName>
  </Midl>
  {link}
</ItemDefinitionGroup>
"""

	Link = """
  <Link>
    <AdditionalLibraryDirectories>{lib.path};%(AdditionalLibraryDirectories)</AdditionalLibraryDirectories>
    <AdditionalOptions>{options} %(AdditionalOptions)</AdditionalOptions>
    <AdditionalDependencies>kernel32.lib;user32.lib;gdi32.lib;winspool.lib;shell32.lib;ole32.lib;oleaut32.lib;uuid.lib;comdlg32.lib;advapi32.lib;{libs}</AdditionalDependencies>
    <GenerateDebugInformation>{is.debug}</GenerateDebugInformation>
    <ImportLibrary>{import.library}</ImportLibrary>
    <LinkIncremental>{is.debug}</LinkIncremental>
    <ProgramDataBaseFileName>{pdb}</ProgramDataBaseFileName>
    <StackReserveSize>10000000</StackReserveSize>
    <SubSystem>{subsystem}</SubSystem>
    <Version></Version>
  </Link>
	"""

	Project = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    {configuration.list}
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <ProjectGuid>{id}</ProjectGuid>
    <Platform>Win32</Platform>
    <ProjectName>{name}</ProjectName>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  {configurations}
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>

  {settings}

  {commands}

  <ItemGroup>
  	{items}
  </ItemGroup>

  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>
"""

	Filters = """<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    {compile}
  </ItemGroup>
  <ItemGroup>
    {headers}
  </ItemGroup>
  <ItemGroup>
	{commands}
  </ItemGroup>
  <ItemGroup>
    {groups}
  </ItemGroup>
</Project>
"""

	ProjectConfigurationList = """
<ProjectConfiguration Include="Debug|Win32">
  <Configuration>Debug</Configuration>
  <Platform>Win32</Platform>
</ProjectConfiguration>
<ProjectConfiguration Include="Release|Win32">
  <Configuration>Release</Configuration>
  <Platform>Win32</Platform>
</ProjectConfiguration>
"""

	ConfigurationPropertyGroup = """
<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='{configuration}'" Label="Configuration">
  <ConfigurationType>{type}</ConfigurationType>
  <UseOfMfc>false</UseOfMfc>
  <CharacterSet>MultiByte</CharacterSet>
</PropertyGroup>
"""

	ItemHeader = '<ClInclude Include="{fileName}" />\n'
	ItemCpp    = """<ClCompile Include="{fileName}" >
		{obj.fileName}
	</ClCompile>"""
	ItemC 	   = """<ClCompile Include="{fileName}">
	  {obj.fileName}
      <CompileAs Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">CompileAsC</CompileAs>
      <CompileAs Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">CompileAsC</CompileAs>
    </ClCompile>"""

	FilterGroup = """<Filter Include="{path}">
  <UniqueIdentifier>{id}</UniqueIdentifier>
</Filter>
    """

	FilterCompileItem = """<ClCompile Include="{fileName}">
  <Filter>{path}</Filter>
</ClCompile>
    """

	FilterHeaderItem = """<ClInclude Include="{fileName}">
  <Filter>{path}</Filter>
</ClInclude>
    """
	
	FilterRuleItem = """<CustomBuild Include="{fileName}">
  <Filter>{path}</Filter>
</CustomBuild>
    """
	
	CommandHeader = """
	<ItemGroup>
	<CustomBuild Include="{input}">
"""

	CommandFooter = """
	</CustomBuild>
	</ItemGroup>
"""

	Command = """
    <Message>{message}</Message>
    <Command>{command}</Command>
    <AdditionalInputs>{additional.input};%(AdditionalInputs)</AdditionalInputs>
    <Outputs>{output}</Outputs>
"""