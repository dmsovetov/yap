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

from VCX import Solution
from VCX import WindowsProject
from ..Generator import Generator

# class Windows
class Windows( Generator ):
	SourceFiles = [ '.c', '.cpp', '.cxx']
	HeaderFiles = ['.h', '.hpp']

	# constructor
	def __init__( self ):
		Generator.__init__( self )
		self._solution = Solution()
		self._projects = {}

	# generate
	def generate( self ):
		print( 'Generating Win32 project...' )
		Generator.generate( self )

		# Generate projects
		for target in self.sourceProject.filterTargets():
			project = self._generateProject( target )
			project.serialize( os.path.join( self.binaryDir, target.name + '.dir', target.name + '.vcxproj' ) )
			self._projects[target.name] = project

		# Set project dependencies
		for target in self.sourceProject.filterTargets():
			project = self._projects[target.name]

			for lib in self.listLibraries( target ):
				if lib.name in self._projects.keys():
					project.addDependency( self._projects[lib.name] )

		self._solution.serialize( os.path.join( self.binaryDir, self.sourceProject.name + '.sln' ) )

	# _generateLibrariesForTarget
	def _generateLibrariesForTarget( self, target ):
		result = []

		for library in self.listLibraries( target ):
			name = library.name + '.lib' if library.name.find( '.lib' ) == -1 else library.name

			if self.findTargetByName( library.name ):
				name = os.path.join( self.binaryDir, '$(Configuration)', name )

			result.append( name )

		return result

	# _generateProject
	def _generateProject( self, target ):
		types       = dict( static = WindowsProject.StaticLibrary, executable = WindowsProject.Executable )
		project     = self._solution.addProject( types[target.type], target.name )

		# Filter files
		sourceFiles     = [file for file in target.filterSourceFiles( lambda file: file.ext in Windows.SourceFiles )]
		headerFiles     = [file for file in target.filterSourceFiles( lambda file: file.ext in Windows.HeaderFiles )]
		headers         = self.listHeaderPaths( target )
		link            = self._generateLibrariesForTarget( target )
		libraries       = [path.pathRelativeToProject for path in target.filterPaths( lambda path: path.isLibraries )]
		localLibraries  = self.listLibraryPaths( target )

		# Add project source files
		project.addSourceFiles( [file.projectPath for file in sourceFiles] )
		[project.filters.addSourceFile( file ) for file in sourceFiles]

		# Add project header files
		project.addHeaderFiles( [file.projectPath for file in headerFiles] )
		[project.filters.addHeaderFile( file ) for file in headerFiles]

		# Add configurations
		project.setConfigurations( [
			project.createConfiguration( 'Debug', dict(
				ClCompile = dict(
					WarningLevel                    = 'Level3',
				    Optimization                    = 'Disabled',
				    MultiProcessorCompilation       = True,
				    MinimalRebuild                  = False,
				    PreprocessorDefinitions         = ';'.join( target.project.defines + target.defines + ['WIN32', '_DEBUG', '%(PreprocessorDefinitions)'] ),
				    AdditionalIncludeDirectories    = ';'.join( headers )
				),
			    Link = dict(
				    SubSystem                       = 'Console',
			        GenerateDebugInformation        = True,
			        AdditionalLibraryDirectories    = ';'.join( libraries + localLibraries ),
			        AdditionalDependencies          = ';'.join( link )
			    )
			) ),
		    project.createConfiguration( 'Release', dict(
			    ClCompile = dict(
				    WarningLevel                    = 'Level3',
			        Optimization                    = 'MaxSpeed',
			        MultiProcessorCompilation       = True,
			        MinimalRebuild                  = False,
			        FunctionLevelLinking            = True,
			        IntrinsicFunctions              = True,
			        AdditionalDependencies          = ';'.join( link ),
			        PreprocessorDefinitions         = ';'.join( target.project.defines + target.defines + ['WIN32', 'NDEBUG', '%(PreprocessorDefinitions)'] ),
			        AdditionalIncludeDirectories    = ';'.join( headers )
			    ),
		        Link = dict(
				    SubSystem                       = 'Console',
			        GenerateDebugInformation        = True,
		            EnableCOMDATFolding             = True,
		            OptimizeReferences              = True,
		            AdditionalLibraryDirectories    = ';'.join( libraries + localLibraries ),
		            AdditionalDependencies          = ';'.join( link )
		        )
		    ) )
		] )

		return project