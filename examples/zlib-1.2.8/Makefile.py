
# Project
project = Makefile.getProject()

# Minizip library
StaticLibrary( 'z', project, sources = ['src/' + file.name for file in Files( 'src/*.c' )] )

# Platform specific settings
if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
elif platform == 'iOS':
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )