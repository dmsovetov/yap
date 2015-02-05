# Minizip library
unz = StaticLibrary( 'unz', sources = ['ioapi.c', 'mztools.c', 'unzip.c', 'zip.c'] )

# minizip
minizip = Executable( 'minizip', libs = [ unz, 'z' ], sources = ['minizip.c'] )

# miniunz
miniunz = Executable( 'miniunz', libs = [ unz, 'z' ], sources = ['miniunz.c'] )

# Platform specific settings
if platform == 'MacOS':
	project.define( 'unix' )
elif platform == 'iOS':
	project.define( 'unix' )
elif platform == 'Windows':
	unz.files( 'iowin32.c' )