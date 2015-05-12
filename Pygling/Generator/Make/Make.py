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
    Separator   = ' \\\n                        '

    # ctor
    def __init__( self, platform ):
        Generator.__init__( self )

        self.extensions  = { 'shared': 'so', 'static': 'a', 'executable': '' }
        self.toolchain   = { 'cc': 'gcc', 'cxx': 'g++', 'ar': 'ar' }

    # generateIncludePath
    def generateIncludePath( self, target, path ):
        basePath = self.getPathForTarget( target )
        return string.replace( os.path.relpath( path, basePath ), '\\', '/' )

    # generate
    def generate( self ):
        Generator.generate( self )
        self.generateProjectMakefile()

    # generateProjectMakefile
    def generateProjectMakefile( self ):
        clean          = ''
        compileTargets = ''
        targets        = ''

        for target in self.sourceProject.filterTargets():
            name = target.name

            # Clean
            clean   += Template( Make.CleanTarget ).compile( { 'name': name } )
            targets += name + ' '

            # Compile
            dependencies    = ' '.join([lib.name for lib in self.list_libraries(target, lambda lib: lib.type == 'local' )])
            compileTargets += Template( Make.CompileTarget ).compile( { 'name': name, 'dependencies': dependencies } )

        file = open( self.projectpath + '/Makefile', 'w' )
        file.write( Template( Make.Makefile ).compile( { 'clean': clean, 'compileTargets': compileTargets, 'targets': targets } ) )
        file.close()

    # generateTarget
    def generateTarget( self, name, target ):
        Generator.generateTarget( self, name, target )
        
        makefile = '{0}/{1}.dir/Makefile'.format( self.projectpath, target.name )

        product     = self.getProductForTarget( target )
        linkflags   = Make.Separator.join(self.list_link_flags(target))
        cxxflags    = Make.Separator.join(self.list_cflags(target))
        linker      = self.getLinkerForTarget( target )
        rules       = self.generate_compile_rules(target)
        cxxo        = self.generate_link_rule(target)

        if cxxo == '':
            Template( Make.Empty ).compileToFile(makefile)
            return

        codegenout  = self.processEachTargetCommand( target, self.generateCodegenOutput )
        gencxxo     = self.processEachTargetCommand( target, self.generateCodegenObject )
        commands    = self.processEachTargetCommand( target, self.generateCommandRule )

        Template( Make.Target ).compileToFile( makefile, { 'product': product, 'target': target.name, 'linker.flags': linkflags, 'cxx.flags': cxxflags,
                                                                      'gencxx.o': gencxxo, 'commands': commands, 'codegen.output': codegenout,
                                                                      'cxx.o': cxxo, 'rules': rules, 'linker': linker,
                                                                      'tool.cc': self.toolchain['cc'], 'tool.cxx': self.toolchain['cxx'], 'tool.ar': self.toolchain['ar'] } )

    # generate_compile_rules
    def generate_compile_rules(self, target):
        source = self.list_source_files(target, lambda file: file.ext in ['.c', '.cpp'])
        result = ''

        for item in source:
            name, ext = os.path.splitext(item)
            basename  = os.path.basename(name)
            result += Template( Make.CxxRule ).compile( { 'compiler': '$(CXX)' if ext == '.cpp' else '$(CC)', 'filePath': item, 'baseName': basename, 'target': target.name } )

        return result

    # generate_link_rule
    def generate_link_rule(self, target):
        source = self.list_source_files(target, lambda file: file.ext in ['.c', '.cpp'])
        result = ''

        for item in source:
            name, ext = os.path.splitext(item)
            basename  = os.path.basename(name)
            result += Make.Separator + ' $(OBJ_DIR)/' + basename + '.o '

        return result

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
                                                                    'message':     cmd.message,
                                                                    'input':     input,
                                                                    'output':     output,
                                                                    'command':     cmd.command.replace( '\\', '/' ),
                                                                    'target':     target.name,
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
        result         = ''
        currentPath    = self.getPathForTarget( target )
        
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

    # convertPath
    def convertPath( self, path, base = None ):
        if base == None:
            base = os.getcwd()

        return string.replace( os.path.relpath( path, base ), '\\', '/' )

    # prepend_to
    def prepend_to(self, prefix, items):
        return [prefix + item for item in items]

    # list_cflags
    def list_cflags(self, target):
        return ['-std=c++11'] + ['-D' + define for define in self.list_defines(target)] + self.prepend_to('-I', self.list_header_paths(target))

    # list_link_flags
    def list_link_flags(self, target, filter = None):
        if not target.type in ['executable', 'shared']:
            return []

        return ['-l' + lib.name for lib in self.list_libraries(target, filter)] + self.prepend_to('-L', self.list_library_paths(target) + self.list_local_libs_paths(target))

    # list_local_libs_paths
    def list_local_libs_paths(self, target):
        result = []
        for lib in self.list_libraries(target, lambda lib: lib.type == 'local' ):
            local = self.sourceProject.findTarget(lib.name)
            if local == None:
                print 'Error: unknown local library', lib.name
                continue

            result.append(self.getPathForTarget(local))
        return list(set(result))

    ############################### TEMPLATES

    Makefile = """
# Autogenerated by Pygling

all: folders {targets}
	@echo "Done"

folders:
	mkdir -p Debug Release

{compileTargets}

clean:
{clean}
"""
    Empty = """
# Autogenerated by Pygling
all:
	@true
"""

    Target = """
# Autogenerated by Pygling

CC  = {tool.cc}
CXX = {tool.cxx}
AR  = {tool.ar}

############################## TARGET

PRODUCT = {product}
OBJ_DIR = obj

LINK_FLAGS = {linker.flags}
CXX_FLAGS = {cxx.flags}
CXX_OBJ = {cxx.o}

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

    CleanTarget = "	@cd {name}.dir && make clean\n"

    CompileTarget = """
{name}: {dependencies}
	@echo "Compiling {name}..."
	@cd {name}.dir && make -f Makefile
    """
