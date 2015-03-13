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

import os, glob, subprocess, Target

from Location   import PathScope
from Target     import Folder

# create
def create(makefile, platform, project):
	# Include
	def Include( *list ):
		for path in list:
			makefile.project.target( path )

	# Library
	def Library( name, required = False ):
		locations = makefile.platform.find_library( name )

		if not locations and required:
			print 'Error:', name, 'is required'
			exit(1)

		return locations

	# Has
	def Has( name ):
		return makefile.get( name.upper() ) != None

	# Get
	def Get( name ):
		return makefile.get( name.upper() )

	# Set
	def Set( name, value ):
		makefile.set( name.upper(), value )

	# Project
	def Project( externals = None, paths = None ):
		if externals:
			project.add_headers_search_paths(os.path.join(externals, 'include'))
			project.add_library_search_paths(os.path.join(externals, 'lib', platform))
		if paths:
			project.add_headers_search_paths(paths)

	# StaticLibrary
	def StaticLibrary(name, sources=None, paths=None, defines=None, link=None):
		return Target.StaticLibrary(name, sources=sources, paths=paths, defines=defines, link=link)

	# Executable
	def Executable(name, sources=None, paths=None, defines=None, link=None):
		return Target.Executable(name, sources=sources, paths=paths, defines=defines, link=link)

	# Folders
	def Folders( path ):
		# class Folder
		class Folder:
			def __init__( self, path ):
				self.name = os.path.basename( path )
				self.path = path

		return [Folder( path ) for path in glob.glob( os.path.join( PathScope.current.source, path ) ) if os.path.isdir( path )]

	# Files
	def Files( path ):
		# class Folder
		class File:
			def __init__( self, path ):
				self.name = os.path.basename( path )
				self.path = path

		return [File( path ) for path in Folder.glob( os.path.join( PathScope.current.source, path ) ) if os.path.isfile( path )]

	# Module
	def Module(url, makefile = None, folder = None, credentials = None):
		name, ext   = os.path.splitext(os.path.basename(url))
		modules     = PathScope.current.source
		auth        = {}

		if credentials:
			execfile(os.path.join(modules, credentials), {}, auth)

		if folder:
			modules = os.path.join(modules, folder)

		# Create modules folder
		if not os.path.exists(modules):
			os.makedirs(modules)

		# Checkout module
		if not os.path.exists(os.path.join(modules, name)):
			if ext == '.git':
				if credentials:
					index = url.find( '//' )
					url   = url[:index + 2] + auth['username'] + ':' + auth['password'] + '@' + url[index + 2:]

				try:
					subprocess.check_call( [ 'git', 'clone', url, modules + '/' + name ] )
				except:
					print 'Error: failed to checkout Git repository from', url

		# Include it to project
		if makefile:
			Include(os.path.join(modules, name, makefile))
		else:
			Include(os.path.join(modules, name))

	return dict(
		# Global variables
		Platform        = platform
	,   MacOS           = True if platform == 'MacOS'   else False
	,   iOS             = True if platform == 'iOS'     else False
	,   Windows         = True if platform == 'Windows' else False
	,   Android         = True if platform == 'Android' else False

		# Global functions
	,	Include         = Include
	,   Library         = Library
	,   Has             = Has
	,   Get             = Get
	,   Set             = Set
	,   Project         = Project
	,   Folders         = Folders
	,   Files           = Files
	,   Module          = Module
	,   StaticLibrary   = StaticLibrary
	,   Executable      = Executable
	)