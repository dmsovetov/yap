#
# The MIT License (MIT)
#
# Copyright (c) 2015 Dmitry Sovetov
#
# https://github.com/dmsovetov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os, subprocess, distutils.version, glob

from collections    import namedtuple
from Unix           import Unix

# class Xcode
class Xcode(Unix):
	# ctor
	def __init__(self, sdk):
		Unix.__init__(self)

		self._sdk       = sdk
		self._aliases   = {}

	# _find_library_by_name
	def _find_library_by_name(self, library):
		# Do an alias lookup
		if library in self._aliases.keys():
			library = self._aliases[library]

		# Find a framework by name
		name       = library
		library    = library + '.framework'
		frameworks = os.path.join( self._sdk, 'System/Library/Frameworks' )
		path       = Unix.exists(library, [frameworks])

		if not path:
			return None

		return namedtuple('Framework', 'type, name, path')(type='framework', name=name, path=frameworks)

	# add_library_alias
	def add_library_alias(self, identifier, alias):
		self._aliases[identifier] = alias

	# library_file_names
	def library_file_names(self, name):
		return [name + '.framework'] + Unix.library_file_names(self, name)

	# header_file_names
	def header_file_names(self, name, filename):
		return [name + '.framework/Headers/' + os.path.basename(filename)] + Unix.header_file_names(self, name, filename)

	# list_sdks
	@staticmethod
	def list_sdks(platform):
		# parseProperty
		def parseProperty( path, key ):
			try:
				return subprocess.check_output( '/usr/libexec/PlistBuddy -c "Print :{1}" "{0}"'.format( path, key ), shell=True ).strip()
			except:
				print 'Error: failed to parse property from', path
				return None

		# read_app_version
		def read_app_version(path):
			return parseProperty(os.path.join(path, 'Contents/Info.plist'), 'CFBundleShortVersionString')

		# findXcode
		def findXcode():
			try:
				value = subprocess.check_output( ['xcode-select', '-p'] ).strip()
			except:
				print 'Error: xcode-select failed'
				return None

			return value

		xcode       = findXcode()
		result      = []
		path        = '{0}/Platforms/{1}.platform/Developer/SDKs/'.format( xcode, platform )
		XcodeSDK    = namedtuple('XcodeSDK', 'path, name')

		# No SDK path found
		if not os.path.exists(path):
			print 'Warning: no {0} SDK found, Xcode path {1}, SDK path {2}'.format( platform, xcode, path )
			return [ XcodeSDK(path=path, name=platform) ]

		# List SDKs
		for sdk in os.listdir( path ):
			pathToSdk = os.path.join(path, sdk)
			sdkName   = parseProperty( os.path.join( pathToSdk, 'SDKSettings.plist' ), 'CanonicalName' )
			result.append( XcodeSDK(path=pathToSdk, name=sdkName) )

		return result