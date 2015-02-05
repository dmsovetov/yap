ignore = [ 'jmemansi.c', 'jmemdos.c', 'jmemmac.c' ]
StaticLibrary( 'jpeg', sources = ['src/' + file.name for file in Files( 'src/*.c' ) if not file.name in ignore] )