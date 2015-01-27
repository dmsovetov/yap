import random

# class Resource
class Resource:
	# ctor
	def __init__( self, isa, name ):
		self.isa    = isa
		self.name   = name
		self.id     = Resource.generateId()

	# generateId
	@classmethod
	def generateId( cls ):
		chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
		id    = ''

		for i in range(1,25):
			id += chars[random.randrange( 0, 16 )]

		return id