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

from ObjectList     import ObjectList
from Resource       import Resource
from ...Template    import Template

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