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

import string, os

from ..Generator import Generator
from ..Template  import Template

# class Make
class Make( Generator ):
	# ctor
	def __init__( self ):
		Generator.__init__( self )

		self.globalFlags = ''
		self.extensions  = { 'shared': 'so', 'static': 'a', 'executable': '' }
		self.toolchain   = { 'cc': 'gcc', 'cxx': 'g++', 'ar': 'ar' }

	# generateTargetDependencies
	def generateTargetDependencies( self, target ):
		result = ''
		
		for name in target.libs:
			result += name + ' '
			
		return result

	# generateIncludePath
	def generateIncludePath( self, target, path ):
		basePath = self.getPathForTarget( target )
		return string.replace( os.path.relpath( path, basePath ), '\\', '/' )

	# generate
	def generate( self ):
		self.globalFlags = self.getCompilerFlagsForTarget( self ) + ' -w '
		
		Project.generate( self )
		self.generateProjectMakefile()

	# generateProjectMakefile
	def generateProjectMakefile( self ):
		clean 			= ''
		compileTargets 	= ''
		targets 		= ''

		# Clean targets
		for name in self.targets:
			target 	=  self.targets[name]
			clean 	+= Template( Make.CleanTarget ).compile( { 'name': name } )
			targets += name + ' '

		# Compile targets
		for name in self.targets:
			target = self.targets[name]
			compileTargets += Template( Make.CompileTarget ).compile( { 'name': name, 'dependencies': self.generateTargetDependencies( target ) } )

		file = open( Makefile.BinaryDir + '/Generator', 'w' )
		file.write( Template( Make.Makefile ).compile( { 'clean': clean, 'compileTargets': compileTargets, 'targets': targets } ) )
		file.close()

	# generateTarget
	def generateTarget( self, target ):
		Project.generateTarget( self, target )
		
		makefile = '{0}/{1}.dir/Generator'.format( Makefile.BinaryDir, target.name )

		product   	= self.getProductForTarget( target )
		linkflags 	= self.getLinkerFlagsForTarget( target )
		cxxflags  	= self.getFlagsForTarget( target )
		linker 	  	= self.getLinkerForTarget( target )

		cxxo 	  	= self.processEachTargetSource( target, ['.c', '.cpp'], self.generateObjectFileList )
		rules 	  	= self.processEachTargetSource( target, ['.c', '.cpp'], self.generateCompilerRule )

		codegenout	= self.processEachTargetCommand( target, self.generateCodegenOutput )
		gencxxo		= self.processEachTargetCommand( target, self.generateCodegenObject )
		commands  	= self.processEachTargetCommand( target, self.generateCommandRule )

		Template( Make.Target ).compileToFile( makefile, { 'product': product, 'target': target.name, 'linker.flags': linkflags, 'cxx.flags': cxxflags,
																	  'gencxx.o': gencxxo, 'commands': commands, 'codegen.output': codegenout,
																	  'cxx.o': cxxo, 'rules': rules, 'linker': linker,
																	  'tool.cc': self.toolchain['cc'], 'tool.cxx': self.toolchain['cxx'], 'tool.ar': self.toolchain['ar'] } )

	# generateObjectFileList
	def generateObjectFileList( self, target, filePath, baseName, ext ):
		return '$(OBJ_DIR)/' + baseName + '.o '

	# generateCompilerRule
	def generateCompilerRule( self, target, filePath, baseName, ext ):
		return Template( Make.CxxRule ).compile( { 'compiler': '$(CXX)' if ext == '.cpp' else '$(CC)', 'filePath': filePath, 'baseName': baseName, 'target': target.name } )

	# generateAutogeneratedCompilerRule
	def generateAutogeneratedCompilerRule( self, target, cmd ):
		targetPath = self.getPathForTarget( target )
		name = self.convertPath( cmd.output, targetPath )
		return self.generateCompilerRule( target, name + '.cpp', name, '.cpp' )

	# generateCommandRule
	def generateCommandRule( self, target, cmd ):
		targetPath = self.getPathForTarget( target )
		baseName   = os.path.basename( cmd.input[0] )

		input = ''
		for fileName in cmd.input:
			input += self.convertPath( fileName, targetPath ) + ' '

		output = ''
		for ext in cmd.generatedExtensions:
			output += self.convertPath( cmd.output, targetPath ) + ext + ' '

		return Template( Make.CxxGenerate ).compile( {
																	'message': 	cmd.message,
																	'input': 	input,
																	'output': 	output,
																	'command': 	cmd.command.replace( '\\', '/' ),
																	'target': 	target.name,
																	'baseName': baseName
																} )

	# generateCodegenOutput
	def generateCodegenOutput( self, target, cmd ):
		result = ''

		for ext in cmd.generatedExtensions:
			result += self.convertPath( cmd.output, self.getPathForTarget( target ) ) + ext + ' '

		return result

	# generateCodegenObject
	def generateCodegenObject( self, target, cmd ):
		return '$(OBJ_DIR)/' + os.path.basename( cmd.output ) + '.o '

	# getProductForTarget
	def getProductForTarget( self, target, forLinker = False ):
		ext  = self.getExtensionForTarget( target )
		name = target.name

		if len( ext ) == 0:
			return name

		if target.type == 'static':
			name = 'lib' + name

		return name + '.' + ext

	# getExtensionForTarget
	def getExtensionForTarget( self, target ):
		if target.type in self.extensions:
			return self.extensions[target.type]

		print "Make::getExtensionForTarget : unknown target type '{0}'".format( target.type )
		return ''

	# getLinkerForTarget
	def getLinkerForTarget( self, target ):
		if target.type == 'shared':
			return '$(CXX) $(CXX_OBJ) -o $(PRODUCT) $(LINK_FLAGS)'
		elif target.type == 'executable':
			return '$(CXX) $(CXX_OBJ) -o $(PRODUCT) $(LINK_FLAGS)'
		else:
			return '$(AR) rs $(PRODUCT) $(LINK_FLAGS) $(CXX_OBJ)'

		print "Make::getLinkerForTarget : unknown target type '{0}'".format( target.type )
		return ''

	# getLibrariesForTarget
	def getLibrariesForTarget( self, target ):
		result 		= ''
		currentPath	= self.getPathForTarget( target )
		
		for name in target.libs:
			lib  = self.targets[name]
			path = self.getPathForTarget( lib )
			name = self.getProductForTarget( lib, True )

			result += self.convertPath( path + '/lib' + name, currentPath ) + ' '
			result += self.getLibrariesForTarget( lib )
			
		return result

	# getLinkerFlagsForTarget
	def getLinkerFlagsForTarget( self, target ):
		if target.type != 'static':
			return self.getLibrariesForTarget( target )

		return ''

	# getCompilerFlagsForTarget
	def getCompilerFlagsForTarget( self, target ):
		result = ' '
		
		# Defines
		for define in target.defines:
			result += '-D' + define + ' '

		# Include paths
		for include in target.includes:
			path    = self.sourcePath if include == '.' else include
			result += '-I' + self.generateIncludePath( target, path ) + ' '
			
		return result

	# getFlagsForTarget
	def getFlagsForTarget( self, target ):
		return self.globalFlags + self.getCompilerFlagsForTarget( target )


	# convertPath
	def convertPath( self, path, base = None ):
		if base == None:
			base = os.getcwd()

		return string.replace( os.path.relpath( path, base ), '\\', '/' )

	# list_cflags
	def list_cflags(self, target):
		return ['-D' + define for define in self.list_defines(target)] + ['-I' + include for include in self.list_header_paths(target)]

	############################### TEMPLATES

	Makefile = """
# Autogenerated by YAP

all: folders {targets}
	@echo "Done"

folders:
	mkdir -p Debug Release

{compileTargets}

clean:
{clean}
"""

	Target = """
# Autogenerated by YAP

CC  = {tool.cc}
CXX = {tool.cxx}
AR  = {tool.ar}

############################## TARGET

PRODUCT		= {product}
OBJ_DIR 	= obj

LINK_FLAGS 	= {linker.flags}
CXX_FLAGS 	= {cxx.flags}
CXX_OBJ 	= {cxx.o}

all: folders commands $(PRODUCT)
	@true

folders:
	@mkdir -p $(OBJ_DIR)
		
clean:
	@echo "Cleaning {target}..."
	@rm -f obj/*.o *.a *.bc *.html *.h *.cpp

$(PRODUCT): $(CXX_OBJ)
	@echo 'Linking...'
	@{linker}
	@cp $(PRODUCT) ../Release/$(PRODUCT)

############################## COMMANDS RULES

commands: {codegen.output}
	@true

{commands}

############################## CXX RULES

{rules}
"""
	CxxRule = """
$(OBJ_DIR)/{baseName}.o: {filePath}
	@echo '{target} <= {baseName}'
	@{compiler} $(CXX_FLAGS) -c $< -o $@
"""

	CxxGenerate = """
{output}: {input}
	@echo '{target} <= {baseName} {message}'
	@{command}
"""

	CleanTarget = "\t@cd {name}.dir && make clean\n"

	CompileTarget = """
{name}: {dependencies}
	@echo "Compiling {name}..."
	@cd {name}.dir && make -f Generator
	"""
