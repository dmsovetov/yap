from Resource import Resource
from Template import Template

# class BuildConfiguration
class BuildConfiguration( Resource ):
	# ctor
	def __init__( self, name, settings ):
		Resource.__init__( self, 'XCBuildConfiguration', name )
		self.settings = settings

	# addSetting
	def addSetting( self, key, value ):
		# Add the key if doesn't exist
		if not key in self.settings.keys():
			self.settings[key] = []

		# Check for duplicates and add
		if not value in self.settings[key]:
			self.settings[key].append( value )

	# set
	def set( self, key, value ):
		self.settings[key] = value

	# compileSettings
	def compileSettings( self ):
		result = ''

		for k, v in self.settings.items():
			if type( v ) == list:
				value = '(\n'
				for i in v:
					value += '\t\t\t\t\t"' + i + '",\n'
				value += '\t\t\t\t)'
			else:
				value = v

			result += Template( BuildConfiguration.Setting ).compile( { 'key': k, 'value': value } )

		return result

	# compile
	def compile( self ):
		return Template( BuildConfiguration.Root ).compile( { 'id': self.id, 'isa': self.isa, 'name': self.name, 'settings': self.compileSettings() } )

	# Setting
	Setting = "\t\t\t\t{key} = {value};\n"

	# Root
	Root = """
		{id} /* {name} */ = {
			isa = {isa};
			buildSettings = {
{settings}
			};
			name = {name};
		};
"""
