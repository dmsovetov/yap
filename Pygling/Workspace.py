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

import platform, os, glob, shutil

import Platform, Target, Globals, Builder

from Location import PathScope
from Makefile import Makefile

# class Workspace
class Workspace:
	# Target platform aliases
	Aliases = dict( macos = 'MacOS', windows = 'Windows', flash = 'Flash', android = 'Android', ios = 'iOS', html5 = 'HTML5' )

	# Available platforms
	Platforms = dict( Windows = Platform.Windows, MacOS = Platform.MacOS, iOS = Platform.iOS, Android = Platform.Android )

	# Available builders
	Builders = dict( MacOS = Builder.Xcode, iOS = Builder.Xcode, Windows = Builder.VisualStudio )

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

	# build
	def build(self, platform):
		# Get list of platforms
		platforms = self._platforms(platform)

		for platform in platforms:
			if not platform in Workspace.Builders.keys():
				raise Exception('Do not known how to build for ' + platform)

			config = self._args.configuration
			source = self._substitute_variables(self._source, platform = platform, configuration = config)

			Workspace.Builders[platform].build(source, config)

	# install
	def install(self, platform):
		# Get list of platforms
		platforms = self._platforms(platform)

		# For each platform install products
		for platform in platforms:
			source   = self._substitute_variables(self._source, platform = platform)
			output   = self._substitute_variables(self._output, platform = platform)
			products = os.path.join(source, 'Release')
			lib      = os.path.join(output, 'lib', platform)
			bin      = os.path.join(output, 'bin', platform)

			if not os.path.exists(products):
				raise Exception('No products built for ' + platform + ' Release configuration')

			# Build libraries list
			libs = []
			for ext in ['.a', '.lib']:
				libs = libs + glob.glob(os.path.join(products, '*' + ext))

			# Build executables list
			bins = []
			for ext in ['.exe', '.app']:
				bins = bins + glob.glob(os.path.join(products, '*' + ext))
			bins = bins + [path for path in glob.glob(os.path.join(products, '*' + ext)) if os.path.split(path)[1] == '']

			# Install libraries
			if len(libs):
				if not os.path.exists(lib):
					os.makedirs(lib)

				for file in libs:
					print 'Installing', os.path.basename(file)
					shutil.copyfile(file, os.path.join(lib, os.path.basename(file)))

			# Install binaries
			if len(bins):
				if not os.path.exists(bin):
					os.makedirs(bin)

				for file in bins:
					print 'Installing', os.path.basename(file)
					shutil.copyfile(file, os.path.join(bin, os.path.basename(file)))


	# _create_makefile
	def _create_makefile(self, platform):
		Makefile.clear()
		Makefile.platform = Workspace.Platforms[platform]()
		Makefile.set( 'PLATFORM', platform )
		Makefile.set( 'ARCH', self._args.arch )
		Makefile.set( 'STD', self._args.std )
		Makefile.set( 'DEVELOPMENT_TEAM', self._args.xcteam )
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
			raise Exception("Unknown target platform")

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

	# _substitute_variables
	def _substitute_variables(self, str, **vars):
		for k, v in vars.items():
			str = str.replace( '[' + k + ']', v )
		return str

	# available_targets
	@staticmethod
	def available_targets():
		platforms = dict(
			Windows = [
				'Windows'
			,   'Android'
			]
		,   Darwin  = [
				'MacOS'
			,   'iOS'
			,   'Android'
			]
		)

		system = platform.system()

		if not system in platforms.keys():
			return None

		return platforms[system]