from Resource   import Resource
from ObjectList import ObjectList
from Template   import Template

# class ConfigurationList
class ConfigurationList( Resource ):
	# ctor
	def __init__( self, default, owner ):
		Resource.__init__( self, 'XCConfigurationList', None )

		self.default = default
		self.owner   = owner
		self.items   = ObjectList()

	# add
	def add( self, item ):
		self.items.add( item )

	# forEach
	def forEach( self, callback ):
		for item in self.items.items:
			callback( item )

	# compile
	def compile( self ):
		return Template( ConfigurationList.Root ).compile( { 'id': self.id, 'isa': self.isa, 'items': self.items.compileList(), 'default': self.default, 'owner': self.owner.name, 'owner.isa': self.owner.isa } )

	# Root
	Root = """
		{id} /* Build configuration list for {owner.isa} {owner} */ = {
			isa = {isa};
			buildConfigurations = (
{items}
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = {default};
		};
"""