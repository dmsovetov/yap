import os

from Xcode5 	import Xcode5
from Template   import Template

# class iOS
class iOS( Xcode5 ):
	# ctor
	def __init__( self ):
		Xcode5.__init__( self )

	# getPlatformId
	def getPlatformId( self ):
		return 'ios'

	# getProjectSettings
	def getProjectSettings( self ):
		return {
			'Debug': {
				'ARCHS':                        'armv7',
				'SDKROOT':                      self.makefile.get( 'IOS_SDK' ),
		        'TARGETED_DEVICE_FAMILY':       '"1,2"',
			    'ALWAYS_SEARCH_USER_PATHS':     'NO',
			    'CODE_SIGN_IDENTITY':           '"iPhone Developer"',
		        'IPHONEOS_DEPLOYMENT_TARGET':   '6.0'
			},
		    'Release': {
				'ARCHS':                        'armv7',
				'SDKROOT':                      self.makefile.get( 'IOS_SDK' ),
		        'TARGETED_DEVICE_FAMILY':       '"1,2"',
			    'ALWAYS_SEARCH_USER_PATHS':     'NO',
		        'CODE_SIGN_IDENTITY':           '"iPhone Developer"',
		        'IPHONEOS_DEPLOYMENT_TARGET':   '6.0'
		    }
		}