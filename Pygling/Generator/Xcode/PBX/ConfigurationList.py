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