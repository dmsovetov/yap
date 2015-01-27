from Template import Template

# class ObjectList
class ObjectList:
	# ctor
	def __init__( self, isa = None ):
		self.isa    = isa
		self.items  = []

	# add
	def add( self, item ):
		self.items.append( item )

	# compile
	def compile( self ):
		result = ''

		for i in self.items:
			result += i.compile()

		return result

	# compileList
	def compileList( self ):
		result = ''

		for i in self.items:
			result += Template( ObjectList.Item ).compile( { 'id': i.id, 'name': i.name } )

		return result

	Item = "\t\t\t\t{id} /* {name} */,\n"