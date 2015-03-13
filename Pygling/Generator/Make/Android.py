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

import os, string

from Make       import Make
from ..Template import Template

# class Android
class Android( Make ):
	# constructor
	def __init__( self ):
		Make.__init__( self )
		self.targetType = { 'static': 'BUILD_STATIC_LIBRARY', 'shared': 'BUILD_SHARED_LIBRARY', 'executable': 'BUILD_SHARED_LIBRARY'  }

	# getPathForTarget
	def getPathForTarget( self, target ):
		return self.binaryDir + '/jni/' + target.name + '.dir'

	# generateIncludePath
	def generateIncludePath( self, target, path ):
		return string.replace( os.path.relpath( path, self.binaryDir ), '\\', '/' )
		
	# generate
	def generate( self ):
		print( 'Generating Android NDK project...' )
	
		# JNI folder
		if not os.path.exists( self.projectpath + '/jni' ):
			os.makedirs( self.projectpath + '/jni' )

		# Generate targets
		self.forEachTarget( self.generateTarget )

		# Generate root makefile
		self.generateProjectMakefile()

	# generateTarget
	def generateTarget( self, name, target ):
		# generateLibDependency
		def generateLibDependecy( target, name, lib ):
			return name + ' '

		#Create folder
		path 		= '{0}/jni/{1}.dir'.format( self.projectpath, target.name )
		fileName 	= os.path.join( path, 'Android.mk' )

		if not os.path.exists( path ):
			os.makedirs( path )

		libs 			= self.processEachTargetLib( target, generateLibDependecy )
		sources 		= 'Autogenerated.c ' + self.processEachTargetSource( target, ['.c', '.cpp'], self.generateFileName )
		flags 			= self.getCompilerFlagsForTarget( self.sourceProject ) + ' ' + self.getCompilerFlagsForTarget( target )
		shared  		= self.processEachTargetFramework( target, self.generateFramework )
		commandRules 	= self.processEachTargetCommand( target, self.generateCommandRule )
		commands 		= self.processEachTargetCommand( target, self.generateCommand )

		# Write Android.mk
		Template( Android.Target ).compileToFile( fileName, {
																'name': 			target.name,
																'touch':			'echo // Autogenerated  >' if os.name == 'nt' else 'touch',
																'libs': 			libs,
																'sources': 			sources,
																'type': 			self.targetType[target.type],
																'flags': 			flags,
																'shared': 			shared,
																'command.rules':	commandRules,
																'commands':			commands,
																'command.proxy':	os.path.join( self.getPathForTarget( target ), 'Autogenerated.c' ),
															} )

	# generateFramework
	def generateFramework( self, target, name, lib ):
		return '-l' + name + ' '

	# generateCommand
	def generateCommand( self, target, cmd ):
		output = ''
		for ext in cmd.generatedExtensions:
			output += '$(LOCAL_PATH)/' + self.convertPath( cmd.output, self.getPathForTarget( target ) ) + ext + ' '

		return output

	# generateCommandRule
	def generateCommandRule( self, target, cmd ):
		targetPath = self.getPathForTarget( target )
		baseName   = os.path.basename( cmd.input[0] )

		input = ''
		for fileName in cmd.input:
			input += self.convertPath( fileName, self.binaryDir ) + ' '

		output = ''
		for ext in cmd.generatedExtensions:
			output += '$(LOCAL_PATH)/' + self.convertPath( cmd.output, targetPath ) + ext + ' '

		return Template( Android.Command ).compile( {
														'message': 	cmd.message,
														'input': 	input,
														'output': 	output,
														'command': 	cmd.command,
														'target': 	target.name,
														'baseName': baseName,
														'proxy':	os.path.join( targetPath, output ),
													} )

	# generateFileName
	def generateFileName( self, target, filePath, baseName, ext ):
		return filePath + ' '

	# generateProjectMakefile
	def generateProjectMakefile( self ):
		# addTarget
		def addTarget( name, target ):
			return 'include $(TOP_PATH)/{0}.dir/Android.mk\n'.format( name )

		# Generate targets
		targets = self.processEachTarget( addTarget )

		# Write root Android.mk & Application.mk
		Template( Android.Makefile ).compileToFile( '{0}/jni/Android.mk'.format( self.binaryDir ), { 'targets': targets } )
		Template( Android.Application ).compileToFile( '{0}/jni/Application.mk'.format( self.binaryDir ) )

	# Project makefile
	Makefile = """
# Autogenerated by YAP

TOP_PATH:=$(call my-dir)
{targets}

$(call import-module,android/native_app_glue)
	"""

	# Application.mk
	Application = """
# Autogenerated by YAP

APP_STL 		:= gnustl_static
APP_PLATFORM 	:= android-9
APP_ABI 		:= armeabi
APP_CFLAGS		:= -O3 -w -fno-exceptions -fno-rtti
	"""

	# Target makefile
	Target = """
# Autogenerated by YAP

LOCAL_PATH:= $(call my-dir)

include $(CLEAR_VARS)

LOCAL_SHORT_COMMANDS	:= false
LOCAL_MODULE    		:= {name}
LOCAL_SRC_FILES 		:= {sources}
LOCAL_CFLAGS			+= {flags}
LOCAL_STATIC_LIBRARIES	:= android_native_app_glue {libs}
LOCAL_ARM_MODE 			:= arm
LOCAL_LDLIBS			:= {shared}

$(LOCAL_PATH)/Autogenerated.c: {commands}
	@{touch} {command.proxy}

{command.rules}

include $({type})
"""

	Command = """
{output}: {input}
	$(info Shell    : {target} <= {message})
	@{command}
"""