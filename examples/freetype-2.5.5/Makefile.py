# Project
project = Makefile.getProject()

# Freetype library
freetype = StaticLibrary( 'freetype', project, sources = [ 'src/base/*', 'src/gzip/ftgzip.c', 'src/winfonts/winfnt.c', 'src/cid/type1cid.c' ], defines = [ 'FT2_BUILD_LIBRARY', 'FT_CONFIG_OPTION_SYSTEM_ZLIB' ] )
freetype.include( 'include' )

# Add Freetype modules sources
prefix = { 'gzip': 'ft', 'cid': 'type1', 'lzw': 'ft' }

for folder in Folders( 'src/*' ):
	if not folder.name in ['tools', 'base', 'bzip2', 'cache', 'winfonts']:
		fileName = (prefix[folder.name] if folder.name in prefix.keys() else '') + folder.name + '.c'
		freetype.files( folder.path + '/' + fileName )

# Platform specific settings
if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
	freetype.define( 'DARWIN_NO_CARBON' )
elif platform == 'iOS':
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )