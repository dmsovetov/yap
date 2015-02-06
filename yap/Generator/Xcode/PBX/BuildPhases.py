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

from Resource       import Resource
from ObjectList     import ObjectList
from ...Template    import Template

# class BuildPhase
class BuildPhase( Resource ):
	# ctor
	def __init__( self, isa, target, name ):
		Resource.__init__( self, isa, name )

		self.target = target
		self.isa    = isa
		self.files  = ObjectList()

	# add
	def add( self, item ):
		self.files.add( item )

	# compile
	def compile( self ):
		return Template( SourceBuildPhase.Root ).compile( { 'id': self.id, 'isa': self.isa, 'target': self.target.name, 'files': self.files.compileList() } )

	# Root
	Root = """
		{id} /* {target} */ = {
			isa = {isa};
			buildActionMask = 2147483647;
			files = (
{files}
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
"""

# class SourceBuildPhase
class SourceBuildPhase( BuildPhase ):
	# ctor
	def __init__( self, target ):
		BuildPhase.__init__( self, 'PBXSourcesBuildPhase', target, 'Sources' )

# class FrameworkBuildPhase
class FrameworkBuildPhase( BuildPhase ):
	# ctor
	def __init__( self, target ):
		BuildPhase.__init__( self, 'PBXFrameworksBuildPhase', target, 'Frameworks' )

# class ResourceBuildPhase
class ResourceBuildPhase( BuildPhase ):
	# ctor
	def __init__( self, target ):
		BuildPhase.__init__( self, 'PBXResourcesBuildPhase', target, 'Resources' )

# class ShellScriptPhase
class ShellScriptPhase( BuildPhase ):
	# ctor
	def __init__( self, target, command ):
		BuildPhase.__init__( self, 'PBXShellScriptBuildPhase', target, 'Shell Script' )

		self.command = command

	# compile
	def compile( self ):
		return Template( ShellScriptPhase.Root ).compile( { 'id': self.id, 'isa': self.isa, 'target': self.target.name, 'command': self.command, 'name': self.name } )

	# Root
	Root = """
		{id} /* {target} */ = {
			isa = {isa};
			buildActionMask = 2147483647;
			files = (
			);
			name = "{name}";
			runOnlyForDeploymentPostprocessing = 0;
			shellPath = /bin/sh;
			shellScript = "{command}";
			showEnvVarsInLog = 0;
		};
"""