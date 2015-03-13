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

from Resource    import Resource
from ...Template import Template

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
