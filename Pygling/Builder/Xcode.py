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

import os, glob, subprocess

# class Xcode
class Xcode:
	# build
	@staticmethod
	def build(source, configuration):
		# Check source path exists.
		if not os.path.exists(source):
			raise Exception('Source folder does not exist: ' + source)

		# Get all workspaces
		workspaces = glob.glob(os.path.join(source, '*.xcworkspace'))

		if len(workspaces) == 0:
			raise Exception('No workspaces found in folder ' + source)

		# Build all workspaces
		for workspace in workspaces:
			schemes = Xcode.schemes(workspace)

			if len(schemes) == 0:
				raise Exception('There are no schemes in workspace ' + workspace)

			for scheme in schemes:
				os.system('xcodebuild -workspace {0} -scheme {1} -configuration {2} CONFIGURATION_BUILD_DIR={3}/{2}'.format(workspace, scheme, configuration, source))

	# schemes
	@staticmethod
	def schemes(workspace):
		try:
			result = subprocess.check_output(['xcodebuild', '-workspace', workspace, '-list'])

			if result.find( 'There are no schemes in workspace' ) != -1:
				return []

			token  = 'Schemes:'
			start  = result.find(token)
			return [item.strip() for item in result[start + len(token):].split( '\n' ) if item != '']
		except:
			raise Exception('Failed to read workspace schemes')
