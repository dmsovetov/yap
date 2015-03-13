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

import Generator, os

# class Qt
class Qt:
	# ctor
	def __init__( self, target, makefile ):
		self.makefile = makefile

		path = self.getQtPath()
		target.include( os.path.join( self.makefile.get( 'Qt' ), 'include' ) )

	# getQtPath
	def getQtPath( self ):
		path = self.makefile.get( 'Qt' )
		assert path, 'no Qt path set'

		path = os.path.expanduser( path )
		assert os.path.exists( path ), 'Qt path {0} doesnt exist'.format( path )

		return path

	# framework
	def framework( self, name ):
		if not name.startswith( 'Qt' ):
			return name

		return os.path.join( self.getQtPath(), 'lib', name + '.framework' )

	# wrap
	def wrap( self, target, generator, fileName, extension ):
		if not os.path.exists( fileName ):
			return False

		if extension == '.ui':
			self.uic( target, generator, fileName )
			return True
		elif extension == '.qrc':
			self.rcc( target, generator, fileName )
			return True
		elif extension == '.h':
			self.moc( target, generator, fileName )
			return True

		return False

	# moc
	def moc( self, target, generator, fileName ):
		fp = open( fileName )

		if fp.read().find( 'Q_OBJECT' ) != -1:
			name, ext 	 	= os.path.splitext( os.path.basename( fileName ) )
			outputFileName 	= os.path.join( generator.getPathForTarget( target ), 'moc' + name )
			cmd 			= '{0}/bin/moc -o {1}.cpp {2}'.format( self.makefile.get( 'Qt' ), outputFileName, fileName )

			target.command( [ fileName ], outputFileName, cmd, 'Generating moc{0}.cpp...'.format( name ), ['.cpp'] )

		fp.close()

	# uic
	def uic( self, target, generator, fileName ):
		name, ext 	 	= os.path.splitext( os.path.basename( fileName ) )
		outputFileName 	= os.path.join( generator.getPathForTarget( target ), 'ui' + name )
		cmd 			= '{0}/bin/uic -o {1}.h {2}'.format( self.makefile.get( 'Qt' ), outputFileName, fileName )

		target.command( [ fileName ], outputFileName, cmd, 'Generating ui{0}.cpp...'.format( name ), ['.h'] )

	# rcc
	def rcc( self, target, generator, fileName ):
		name, ext 	 	= os.path.splitext( os.path.basename( fileName ) )
		outputFileName 	= os.path.join( generator.getPathForTarget( target ), 'rc' + name )
		cmd 		 	= '{0}/bin/rcc -name {1} -o {2}.cpp {3}'.format( self.makefile.get( 'Qt' ), name, outputFileName, fileName )

		# Extract file names
		fp    = open( fileName )
		data  = fp.read()
		start = 0
		input = []
		while True:
			start = data.find( '<file>', start )
			if start == -1:
				break

			end = data.find( '</file>', start )
			input.append( os.path.join( os.path.dirname( fileName ), data[start + 6:end] ) )
			start = end
		fp.close()

		target.command( [ fileName ] + input, outputFileName, cmd, 'Generating rc{0}.cpp...'.format( name ), ['.cpp'] )