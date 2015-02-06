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

from ..Generator import Generator
from Make        import Make
from ..Template  import Template

# class Flash
class Flash( Make ):
	# constructor
	def __init__( self ):
		Make.__init__( self )
		self.extensions = { 'shared': 'swc', 'static': 'a', 'executable': 'swf' }

	# generate
	def generate( self ):
		self.toolchain  = { 'cc': Generator.FLACC + '/sdk/usr/bin/gcc', 'cxx': Generator.FLACC + '/sdk/usr/bin/g++', 'ar': Generator.FLACC + '/sdk/usr/bin/ar' }
		
		print( 'Generating Flash project...' )
		MakefileProject.generate( self )

		Template( Flash.Exports ).compileToFile( Generator.BinaryDir + '/exports.txt' )

	# getFlagsForTarget
	def getFlagsForTarget( self, target ):
		flags = MakefileProject.getFlagsForTarget( self, target )
		return '-O4 -flto-api=../exports.txt -w -Wno-write-strings -Wno-trigraphs -fno-rtti -jvmopt=-Xmx900M ' + flags

	# getProductForTarget
	def getProductForTarget( self, target, forLinker = False ):
		ext  = self.getExtensionForTarget( target )
		name = target.name

		if len( ext ) == 0:
			return name

		if not forLinker:
			name = 'lib' + name

		return name + '.' + ext

	# getLinkerFlagsForTarget
	def getLinkerFlagsForTarget( self, target ):
		libs = self.getLibrariesForTarget( target )

		if target.type == 'shared':
			return '{0} -O4 -jvmopt=-Xmx1G -flto-api=../exports.txt -lAS3++ -lFlash++ -emit-swc=native.{1}'.format( libs, target.name )
		elif target.type == 'executable':
			return '{0} -O4 -jvmopt=-Xmx1G -flto-api=../exports.txt -lAS3++ -lFlash++ -symbol-abc=Console.abc -emit-swf -swf-size=640x480'.format( libs )

		return ''

	Exports = """
# built in symbols that must always be preserved
_start1
__muldi3
__divdi3
malloc
free
memcpy
memmove
flascc_uiTickProc
_sync_synchronize

# symbols for C++ exception handling
_Unwind_SjLj_Register
_Unwind_SjLj_Resume
_Unwind_SjLj_Unregister
_Unwind_SjLj_RaiseException
"""