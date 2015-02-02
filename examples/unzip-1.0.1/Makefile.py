
# Project
project = Makefile.getProject()

# Minizip library
unz = StaticLibrary( 'unz', project, sources = ['ioapi.c', 'mztools.c', 'unzip.c', 'zip.c'] )

# minizip
minizip = Executable( 'minizip', project, libs = [ unz, 'z' ], sources = ['minizip.c'] )

# miniunz
miniunz = Executable( 'miniunz', project, libs = [ unz, 'z' ], sources = ['miniunz.c'] )

# Platform specific settings
if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
	project.define( 'unix' )
elif platform == 'iOS':
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )
	project.define( 'unix' )
elif platform == 'Windows':
	unz.files( 'iowin32.c' )