
# Project
project = Makefile.getProject()

# Minizip library
ignore = [ 'jmemansi.c', 'jmemdos.c', 'jmemmac.c' ]
StaticLibrary( 'jpeg', project, sources = ['src/' + file.name for file in Files( 'src/*.c' ) if not file.name in ignore] )

# Platform specific settings
if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
elif platform == 'iOS':
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )