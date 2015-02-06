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

import os

# class Template
class Template:
	# ctor
	def __init__( self, template ):
		self.template 	= template.encode( 'utf-8' )
		self.result		= ''
		self.isCompiled	= False

	# compile
	def compile( self, args, convertLineEndings = False ):
		self.result 	= self.template
		self.isCompiled = True

		if args == None:
			return self.result
		
		for key, value in args.items():
			self.result = self.result.replace( '{' + key + '}', str( value ) )
		
		if convertLineEndings:
			self.result = self.result.replace( '\r', '' )
			self.result = self.result.replace( '\n', os.linesep )
				
		return self.result

	# compileToFile
	def compileToFile( self, fileName, args = None ):
		compiled = self.compile( args )

		file = open( fileName, 'w' )
		file.write( compiled )
		file.close()

	# output
	def output( self, file, args = None ):
		if not self.isCompiled:
			self.compile( args )

		file.write( self.result )