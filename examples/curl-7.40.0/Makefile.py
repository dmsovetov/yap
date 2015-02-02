# Project
project = Makefile.getProject()

# Freetype library
curl = StaticLibrary( 'curl', project, sources = [ 'src/*' ], defines = [ 'HAVE_CONFIG_H' ], include = [ 'src', 'include' ] )

# Platform specific settings
if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
elif platform == 'iOS':
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )