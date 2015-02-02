
# Project
project = Makefile.getProject()
project.define( 'LUA_COMPAT_5_2' )

# Lua library
lua     = StaticLibrary( 'liblua', project, sources = ['src'] )

# Lua shell
shell   = Executable( 'lua', project, libs = [ lua ], sources = ['src/lua.c'] )

# Lua compiler
luac    = Executable( 'luac', project, libs = [ lua ], sources = ['src/luac.c'] )

# Platform specific settings
if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
	project.define( 'LUA_USE_MACOSX' )
	shell.link( 'readline' )
	luac.link( 'readline' )
elif platform == 'iOS':
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )