from Resource   import Resource
from ObjectList import ObjectList
from Template   import Template

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