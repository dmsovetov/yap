
# Project
project = Makefile.getProject()

X11     = findPackage( 'X11', 'GL', 'GLU', 'glut' )

# Box2D
box2d = StaticLibrary( 'Box2D', project, sources = ['src/Box2D/*'], include = ['src'] )

# HelloWorld
helloworld = Executable( 'helloworld', project, sources = ['src/HelloWorld/HelloWorld.cpp'], include = ['src'], libs = [box2d] )

# Freeglut
freeglut = StaticLibrary( 'freeglut', project, sources = ['src/freeglut'], include = [X11.headers], defines = ['FREEGLUT_EXPORTS', 'FREEGLUT_STATIC', '_CRT_SECURE_NO_WARNINGS'] )

# GLUI
glui = StaticLibrary( 'glui', project, sources = ['src/glui'], defines = ['FREEGLUT_STATIC', '_CRT_SECURE_NO_WARNINGS'] )

# Testbed
testbed = Executable( 'Testbed', project, sources = ['src/Testbed/*'], defines = ['FREEGLUT_EXPORTS', 'FREEGLUT_STATIC', '_CRT_SECURE_NO_WARNINGS'], include = ['src'], libs = [box2d, freeglut, glui, X11] )

if platform == 'MacOS':
	Makefile.set( 'MACOS_SDK', 'macosx10.10' )
else:
	Makefile.set( 'IOS_SDK', 'iphoneos8.0' )