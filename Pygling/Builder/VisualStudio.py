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

# class VisualStudio
class VisualStudio:
	# build
	@staticmethod
	def build(source, configuration):
		vs = VisualStudio.tools()

		if len(vs) == 0:
			raise Exception('No VisualStudio installation found')

		commonTools = os.environ[vs[0]]

		sln = VisualStudio.solutions(source)
		if len(sln) == 0:
			raise Exception('No solutions found at path ' + source)

		for solution in sln:
			os.system('call "{0}/VsDevCmd.bat" && devenv {1} /BUILD {2}'.format(commonTools, solution, configuration))

	# tools
	@staticmethod
	def tools():
		return [k for k, v in os.environ.items() if k.startswith('VS') and k.endswith('COMNTOOLS')]

	# solutions
	@staticmethod
	def solutions(path):
		return glob.glob(os.path.join(path, '*.sln'))