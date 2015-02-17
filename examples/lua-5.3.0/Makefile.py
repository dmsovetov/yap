# Project
project.define( 'LUA_COMPAT_5_2' )

# Lua library
lua     = StaticLibrary( 'liblua', sources = ['src'] )

# Lua shell
shell   = Executable( 'lua', link = [ 'liblua' ], sources = ['src/lua.c'] )

# Lua compiler
luac    = Executable( 'luac', link = [ 'liblua' ], sources = ['src/luac.c'] )

# Platform specific settings
if platform == 'MacOS':
	project.define( 'LUA_USE_MACOSX' )
	shell.link( 'readline' )
	luac.link( 'readline' )