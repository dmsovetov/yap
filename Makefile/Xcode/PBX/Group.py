from ObjectList import ObjectList
from Resource   import Resource
from Template   import Template
#from Objects  import Objects

# class Group
class Group( Resource ):
	# ctor
	def __init__( self, objects, name ):
		Resource.__init__( self, 'PBXGroup', name )

		self.objects  = objects
		self.children = ObjectList( 'PBXGroup' )

	# add
	def add( self, item ):
		self.children.add( item )

	# resolveGroup
	def resolveGroup( self, name ):
		for group in self.children.items:
			if group.name == name:
				return group

		group = self.objects.createGroup( name, self )
		return group

	# compile
	def compile( self ):
		name = 'name = {0};'.format( self.name ) if self.name else ''
		return Template( Group.Root ).compile( { 'id': self.id, 'isa': self.isa, 'name': self.name, 'name.property': name, 'children': self.children.compileList() } )

	Nested = "\t\t\t\t{id} /* {name} */,\n"

	Root = """
		{id} /* {name} */ = {
			isa = {isa};
			children = (
{children}
			);
			{name.property}
			sourceTree = "<group>";
		};
"""