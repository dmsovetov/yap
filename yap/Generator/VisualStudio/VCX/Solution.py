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

import ID, codecs, os
from ...Template    import Template
from WindowsProject import WindowsProject

# class Solution
class Solution:
	# ctor
	def __init__( self ):
		self._id       = ID.generate()
		self._projects = []

	# addProject
	def addProject( self, type, name ):
		project = WindowsProject( type, name )
		self._projects.append( project )
		return project

	# serialize
	def serialize( self, fileName ):
		file = codecs.open( fileName, "w", "utf-8-sig" )
		file.write( Template( Solution.Root ).compile( 	{
															'projects':			self._compileProjects(),
															'configurations':	self._compileConfigurations(),
														}, True ) )
		file.close()


	# _compileProjects
	def _compileProjects( self ):
		result = ''
		dependencies = ''

		for project in self._projects:
			for dep in project.dependencies:
				dependencies += Template( Solution.Dependency ).compile( { 'uuid': dep.uid }, True )

			result += Template( Solution.Project ).compile( {
																 			'solution.id': 	self._id,
																 			'name': 		project.name,
																 			'id':			project.uid,
																 			'fileName':		os.path.join( project.name + '.dir', project.name + '.vcxproj' ),
																			'dependencies':	dependencies,
																		}, True )

		return result

	# _compileConfigurations
	def _compileConfigurations( self ):
		result = ''

		for project in self._projects:
			result += Template( Solution.ProjectConfigurations ).compile( { 'id': project.uid }, True )

		return result

	################################### TEMPLATES

	Root = """
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

	Project = """
Project("{solution.id}") = "{name}", "{fileName}", "{id}"
{dependencies}
EndProject"""

	Dependency = """
	ProjectSection(ProjectDependencies) = postProject
		{uuid} = {uuid}
	EndProjectSection
"""

	ProjectConfigurations = """
		{id}.Debug|Win32.ActiveCfg = Debug|Win32
		{id}.Debug|Win32.Build.0 = Debug|Win32
		{id}.Release|Win32.ActiveCfg = Release|Win32
		{id}.Release|Win32.Build.0 = Release|Win32"""
