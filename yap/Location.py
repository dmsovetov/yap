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

import os

class classproperty(object):
	def __init__(self, getter):
		self.getter= getter
	def __get__(self, instance, owner):
		return self.getter(owner)

# class PathScope
class PathScope:
	_Stack = []

	# ctor
	def __init__(self, source, project):
		self._project = project
		self._source  = source

	# source
	@property
	def source(self):
		return self._source

	# project
	@property
	def project(self):
		return self._project

	@classproperty
	def current(cls):
		return cls._Stack[-1]

	# push
	@staticmethod
	def push(source, project):
		PathScope._Stack.append(PathScope(source, project))

	# pop
	@staticmethod
	def pop():
		PathScope._Stack.pop()

# class Path
class Path:
	Headers     = 'Headers'
	Libraries   = 'Libraries'
	Frameworks  = 'Frameworks'

	# ctor
	def __init__( self, type, path ):
		assert isinstance(path, str)

		self._scope = PathScope.current
		self._path  = path
		self._type  = type

	# type
	@property
	def type( self ):
		return self._type

	# path
	@property
	def path( self ):
		return self._path

	# full
	@property
	def full(self):
		return os.path.normpath(os.path.join(self._scope.source, self.path))

	# relativeToProject
	@property
	def pathRelativeToProject( self ):
		if self.path.startswith( self._scope.source ):
			return Folder.relativeTo( self.path, self._scope.project )

		return self.path

	# isheaders
	@property
	def isheaders( self ):
		return self._type == Path.Headers

	# islibraries
	@property
	def islibraries( self ):
		return self._type == Path.Libraries