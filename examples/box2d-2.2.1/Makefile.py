X11     = findPackage( 'X11', 'GL', 'GLU', 'glut' )

# Box2D
box2d = StaticLibrary( 'Box2D', sources = ['src/Box2D/*'], include = ['src'] )

# HelloWorld
helloworld = Executable( 'helloworld', sources = ['src/HelloWorld/HelloWorld.cpp'], include = ['src'], libs = [box2d] )

# Freeglut
freeglut = StaticLibrary( 'freeglut', sources = ['src/freeglut'], include = [X11.headers], defines = ['FREEGLUT_EXPORTS', 'FREEGLUT_STATIC', '_CRT_SECURE_NO_WARNINGS'] )

# GLUI
glui = StaticLibrary( 'glui', sources = ['src/glui'], defines = ['FREEGLUT_STATIC', '_CRT_SECURE_NO_WARNINGS'] )

# Testbed
testbed = Executable( 'Testbed', sources = ['src/Testbed/*'], defines = ['FREEGLUT_EXPORTS', 'FREEGLUT_STATIC', '_CRT_SECURE_NO_WARNINGS'], include = ['src'], libs = [box2d, freeglut, glui, X11] )