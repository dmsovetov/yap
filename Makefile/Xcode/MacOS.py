import os

from Xcode5 	import Xcode5
from Template   import Template

# class MacOS
class MacOS( Xcode5 ):
	# ctor
	def __init__( self ):
		Xcode5.__init__( self )

	# getPlatformId
	def getPlatformId( self ):
		return 'osx'


	# getProjectSettings
	def getProjectSettings( self ):
		return {
			'Debug': {
				'ARCHS':                        'i386',
				'SDKROOT':                      self.makefile.get( 'MACOS_SDK' ),
			    'ALWAYS_SEARCH_USER_PATHS':     'NO',
			},
		    'Release': {
				'ARCHS':                        'i386',
				'SDKROOT':                      self.makefile.get( 'MACOS_SDK' ),
			    'ALWAYS_SEARCH_USER_PATHS':     'NO',
		    }
		}