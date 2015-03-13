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

# class RTTI
class RTTI:
	# ctor
	def __init__( self, target, makefile ):
		self.makefile = makefile

	# wrap
	def wrap( self, target, generator, fileName, extension ):
		if not os.path.exists( fileName ) or extension != '.h':
			return False

		# Check if we have RTTI macroses
		fh   = open( fileName )
		data = fh.read()
		fh.close()

		# Search for RTTI macroses
		macroses 	= [ 'dcBeginClass', 'dcBeginNetworkPacket', 'dcBeginSerializable', 'dcBeginSerializableSuper', 'dcBeginEnum' ]
		hasMacroses = False

		for macro in macroses:
			if data.find( macro ) != -1:
				hasMacroses = True

		if not hasMacroses or data.find( '#skip.rtti' ) != -1:
			return

		# Add command
		name, ext 	 	= os.path.splitext( os.path.basename( fileName ) )
		outputFolder	= generator.getPathForTarget( target )
		outputFileName	= os.path.join( outputFolder, 'rtti' + name )
		cmd 			= 'python ' + os.path.join( generator.sourceDir, '../tools/scripts/rtti.py' ) + ' ' + fileName + ' ' + outputFolder + '/rtti' + name + '.cpp'

		target.command( [ fileName ], outputFileName, cmd, 'Generating rtti{0}.cpp...'.format( name ), ['.cpp'] )

		return True

	#	target.message( 'Has RTTI for ' + name )
