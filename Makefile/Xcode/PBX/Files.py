import os

from Resource import Resource
from Template import Template

# class FileReference
class FileReference( Resource ):
	# ctor
	def __init__( self, type, path, dir ):
		Resource.__init__( self, 'PBXFileReference', os.path.basename( path ) )
		self.type = type
		self.path = path
		self.dir  = dir

		# static library - archive.ar

	# compile
	def compile( self ):
		return Template( FileReference.Root ).compile( { 'id': self.id, 'isa': self.isa, 'name': self.name, 'type': self.type, 'path': self.path, 'dir': self.dir } )

	# Root
	Root = "\t\t{id} /* {name} */ = {isa = {isa}; explicitFileType = {type}; includeInIndex = 0; name = {name}; path = {path}; sourceTree = {dir}; };\n"

# class BuildFile
class BuildFile( Resource ):
	# ctor
	def __init__( self, owner, file ):
		Resource.__init__( self, 'PBXBuildFile', file.name )
		self.file  = file
		self.owner = owner

	# compile
	def compile( self ):
		return Template( BuildFile.Root ).compile( { 'id': self.id, 'isa': self.isa, 'owner': self.owner.name, 'file.name': self.file.name, 'file.reference': self.file.id } )

	# Root
	Root = "\t\t{id} /* {file.name} in {owner} */ = {isa = {isa}; fileRef = {file.reference} /* {file.name} */; };\n"