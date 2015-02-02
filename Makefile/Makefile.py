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

from Eclipse.Android        import Android
from Make.HTML5             import HTML5
from Make.Flash             import Flash
from Target                 import Target, Project
from VisualStudio.Windows 	import Windows
import Env
import Xcode


Generators = {
	'iOS':      Xcode.iOS,
    'Android':  Android,
    'MacOS':    Xcode.MacOS,
    'Windows':  Windows,
    'Flash':    Flash,
	'HTML5':    HTML5,
}

# CreateProject
def CreateProject( name, platform, importer, generator ):
	return Project.Project( name, platform, importer, generator )

# Initialize
def Initialize( name, platform, importer ):
	global _Project, _Generator

	if platform in Generators.keys():
		_Generator = Generators[platform]()
	else:
		raise Exception( 'Unknown target platform {0}'.format( platform ) )

	_Project = CreateProject( name, platform, importer, _Generator )
	_Generator.initialize( SourceDir, BinaryDir, _Project )

# Generate
def Generate():
	_Generator.generate()

# getProject
def getProject():
	return _Project

# getCurrentSourceDir
def getCurrentSourceDir():
	return CurrentSourceDir[-1]

# getSourceDir
def getSourceDir():
	return SourceDir

# getCurrentBinaryDir
def getCurrentBinaryDir():
	return CurrentBinaryDir[-1]

# getBinaryDir
def getBinaryDir():
	return BinaryDir

# setPaths
def setPaths( source, binary ):
	global SourceDir, BinaryDir

	SourceDir = source
	CurrentSourceDir.append( source )

	BinaryDir = binary
	CurrentBinaryDir.append( binary )

# set
def set( name, value ):
	global _Env
	_Env.set( name, value )

	Target.message( "\t{0} = '{1}'".format( name, value ) )

# get
def get( name ):
	global _Env
	return _Env.get( name )

SourceDir 		 = ''
CurrentSourceDir = []

BinaryDir 		 = ''
CurrentBinaryDir = []

FLACC       = ''
Flex        = ''

_Env       = Env.Env()
_Project   = None
_Generator = None