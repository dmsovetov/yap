#################################################################################
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
#################################################################################

import platform, os

import Platform, Target, Globals

from Location import PathScope
from Makefile import Makefile

# class Workspace
class Workspace:
	# Target platform aliases
	Aliases = dict( macos = 'MacOS', windows = 'Windows', flash = 'Flash', android = 'Android', ios = 'iOS', html5 = 'HTML5' )

	# Available platforms
	Platforms = dict( Windows = Platform.Windows, MacOS = Platform.MacOS, iOS = Platform.iOS, Android = Platform.Android )

	# ctor
	def __init__(self, name, source, output, args, params):
		self._name   = name
		self._source = os.path.abspath(source)
		self._output = os.path.abspath(output)
		self._args   = args
		self._params = params

	# configure
	def configure(self, platform):
		# Get list of platforms
		platforms = self._platforms(platform)

		# Invalid platform specified
		if not platforms:
			return False

		# Generate a workspace for each platform
		for platform in platforms:
			# Push path scope
			PathScope.push(self._source, os.path.join(self._output, platform))

			# Create makefile
			self._create_makefile(platform)

			print platform, PathScope.current.source, PathScope.current.project

			# Read workspace
			execfile( PathScope.current.source + '/Makefile.py', Globals.create(Makefile, platform, Makefile.project) )

			# Generate project
			Makefile.generate()

			# Pop path scope
			PathScope.pop()

		return True

	# build
	def build(self, platform):
		pass

	# install
	def install(self, platform):
		pass

	# _create_makefile
	def _create_makefile(self, platform):
		Makefile.clear()
		Makefile.platform = Workspace.Platforms[platform]()
		Makefile.set( 'PLATFORM', platform )
		Makefile.set( 'ARCH', self._args.arch )
		Makefile.set( 'STD', self._args.std )
		Makefile.initialize( Target.Project, self._name, platform, lambda fileName: execfile( fileName, Globals.create(Makefile, platform, Makefile.project) ) )
		Makefile.project.define( 'DC_PLATFORM_' + platform.upper() )
		Makefile.project.define( 'DC_PLATFORM=' + platform )

	# _platforms
	def _platforms(self, platform):
		# Resolve alias
		if platform != 'all' and platform in Workspace.Aliases.keys():
			platform = Workspace.Aliases[platform]

		# Check target platform name
		available = Workspace.available_targets()

		if platform != 'all' and not platform in available:
			return None

		return available if platform == 'all' else [ platform ]

	# _parse_arguments
	def _parse_arguments(self):
		for arg in self._args:
			if not arg.startswith( '--' ):
				continue

			items = arg.split( '=' )
			name  = items[0][2:].upper()

			if len( items ) == 1 or items[1].lower() == 'yes':
				Makefile.project.define( 'DC_' + name + '_ENABLED' )
				Makefile.set( name, True )
			else:
				Makefile.project.define( 'DC_' + name + '=' + items[1] )
				Makefile.project.define( 'DC_' + name + '_' + items[1].upper() )
				Makefile.set( name, items[1] )

	# available_targets
	@staticmethod
	def available_targets():
		platforms = dict(
			Windows = [
				'Windows'
		#	,   'Android'
			]
		,   Darwin  = [
				'MacOS'
			,   'iOS'
		#	,   'Android'
			]
		)

		system = platform.system()

		if not system in platforms.keys():
			return None

		return platforms[system]