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

import os, glob, shutil

from ..Generator import Generator
from ..Template  import Template
from ..          import Make

# class Android
class Android( Generator ):
	# ctor
	def __init__( self ):
		Generator.__init__( self )

	# getPathForTarget
	def getPathForTarget( self, target ):
		return self.binaryDir + '/jni/' + target.name + '.dir'

	# generate
	def generate( self ):
		ndk = Make.Android()
		ndk.initialize( self.sourceDir, self.binaryDir, self.sourceProject )
		ndk.generate()

		print( 'Generating Android Eclipse project...' )

		# generateJavaSourceLinks
		def generateJavaSourceLinks( name, target ):
			result = ''

			for package in target.javaPackages:
				name    = os.path.basename( package )
				result += Template( Android.JavaSource ).compile( { 'name': name, 'path': package } )

			return result

		# generateJavaSourcesClassPaths
		def generateJavaSourcesClassPaths( name, target ):
			result = ''

			for package in target.javaPackages:
				result += '<classpathentry kind="src" path="{0}"/>'.format( os.path.basename( package ) )

			return result

		minsdk    = 9
		targetsdk = 17
		appname   = 'Player'
		package   = 'com.yam'
		activity  = '.StartupActivity'
		sources   = self.processEachTarget( generateJavaSourceLinks )
		classes   = self.processEachTarget( generateJavaSourcesClassPaths )
		src       = os.path.join( self.binaryDir, 'src' )
		gen       = os.path.join( self.binaryDir, 'gen' )
		resvalues = os.path.join( self.binaryDir, 'res/values' )

		# Create folders
		if not os.path.exists( src ):       os.makedirs( src )
		if not os.path.exists( gen ):       os.makedirs( gen )
		if not os.path.exists( resvalues ): os.makedirs( resvalues )

		# Icons
		self.addIcons( self.sourceProject.targets['Player'] )

		# Assets
		self.addAssets( self.sourceProject.targets['Player'] )

		# Strings
		Template( Android.Strings ).compileToFile( os.path.join( resvalues, 'strings.xml' ), { 'name': appname } )

		# Styles
		Template( Android.Styles ).compileToFile( os.path.join( resvalues, 'styles.xml' ) )

		# Manifest
		Template( Android.Manifest ).compileToFile( os.path.join( self.binaryDir, 'AndroidManifest.xml' ),
		                                            { 'package': package, 'min.sdk': minsdk, 'target.sdk': targetsdk, 'activity': activity, 'name': appname } )

		# Classpath
		Template( Android.Classpath ).compileToFile( os.path.join( self.binaryDir, '.classpath' ), { 'java.sources': classes } )

		# Properties
		Template( Android.Properties ).compileToFile( os.path.join( self.binaryDir, 'project.properties' ), { 'target.sdk': targetsdk } )

		# Project
		Template( Android.Project ).compileToFile( os.path.join( self.binaryDir, '.project' ), { 'name': appname, 'java.sources': sources } )

		# C Project
		Template( Android.CProject ).compileToFile( os.path.join( self.binaryDir, '.cproject' ), { 'name': appname } )

	# addIcons
	def addIcons( self, target ):
		if not target.resources:
			return

		icons = os.path.join( target.sourcePath, target.resources, 'images', 'icons.android', '*.png' )

		for icon in glob.glob( icons ):
			name, ext = os.path.splitext( os.path.basename( icon ) )
			dst       = os.path.join( self.binaryDir, 'res/drawable-' + name )

			# Remove previous folder
			if os.path.exists( dst ):
				shutil.rmtree( dst )

			# Create folder
			os.makedirs( dst )

			shutil.copyfile( icon, os.path.join( dst, 'icon.png' ) )

	# addAssets
	def addAssets( self, target ):
		if not target.resources:
			return

		assets = os.path.join( target.sourcePath, target.resources, 'assets' )

		if os.path.exists( assets ):
			dst       = os.path.join( self.binaryDir, 'assets' )

			# Remove previous folder
			if os.path.exists( dst ):
				shutil.rmtree( dst )

			shutil.copytree( assets, dst )

	# Manifest
	Manifest = """<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package}"
    android:versionCode="1"
    android:versionName="1.0" >

    <uses-sdk android:minSdkVersion="{min.sdk}" android:targetSdkVersion="{target.sdk}" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>
    <uses-permission android:name="com.android.vending.BILLING" />

    <application android:allowBackup="true" android:icon="@drawable/icon" android:label="@string/AppName" android:theme="@style/AppDefaultTheme" >
		<activity android:name="{activity}" android:label="@string/AppName" android:configChanges="orientation|keyboardHidden" android:screenOrientation="landscape">
            <meta-data android:name="android.app.lib_name" android:value="{name}" />
			<intent-filter>
				<action android:name="android.intent.action.MAIN" />
				<category android:name="android.intent.category.LAUNCHER" />
			</intent-filter>
        </activity>
    </application>
</manifest>"""

	Classpath = """<?xml version="1.0" encoding="UTF-8"?>
<classpath>
{java.sources}
	<classpathentry kind="src" path="gen"/>
	<classpathentry kind="con" path="com.android.ide.eclipse.adt.ANDROID_FRAMEWORK"/>
	<classpathentry exported="true" kind="con" path="com.android.ide.eclipse.adt.LIBRARIES"/>
	<classpathentry kind="con" path="com.android.ide.eclipse.adt.DEPENDENCIES"/>
	<classpathentry kind="output" path="bin/classes"/>
</classpath>"""

	Properties = """# Autogenerated by YAP build tool
target=android-{target.sdk}"""

	Strings = """<resources>
    <string name="AppName">{bundle.name}</string>
</resources>"""

	Styles = """<resources>
    <!--
        Base application theme, dependent on API level. This theme is replaced
        by AppBaseTheme from res/values-vXX/styles.xml on newer devices.
    -->
    <style name="AppBaseTheme" parent="android:Theme.Light">
        <!--
            Theme customizations available in newer API levels can go in
            res/values-vXX/styles.xml, while customizations related to
            backward-compatibility can go here.
        -->
    </style>

    <!-- Application theme. -->
    <style name="AppDefaultTheme" parent="AppBaseTheme">
        <!-- All customizations that are NOT specific to a particular API-level can go here. -->
    </style>
</resources>"""

	Project = """<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
	<name>{name}</name>
	<comment></comment>
	<projects>
	</projects>
	<buildSpec>
		<buildCommand>
			<name>org.eclipse.cdt.managedbuilder.core.genmakebuilder</name>
			<triggers>clean,full,incremental,</triggers>
			<arguments>
				<dictionary>
					<key>?children?</key>
					<value>?name?=outputEntries\|?children?=?name?=entry\\\\\\\|\\\|?name?=entry\\\\\\\|\\\|\||</value>
				</dictionary>
				<dictionary>
					<key>?name?</key>
					<value></value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.append_environment</key>
					<value>true</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.buildArguments</key>
					<value></value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.buildCommand</key>
					<value>ndk-build</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.cleanBuildTarget</key>
					<value>clean</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.contents</key>
					<value>org.eclipse.cdt.make.core.activeConfigSettings</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.enableAutoBuild</key>
					<value>false</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.enableCleanBuild</key>
					<value>true</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.enableFullBuild</key>
					<value>true</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.stopOnError</key>
					<value>true</value>
				</dictionary>
				<dictionary>
					<key>org.eclipse.cdt.make.core.useDefaultBuildCmd</key>
					<value>true</value>
				</dictionary>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>com.android.ide.eclipse.adt.ResourceManagerBuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>com.android.ide.eclipse.adt.PreCompilerBuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>org.eclipse.jdt.core.javabuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>com.android.ide.eclipse.adt.ApkBuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>org.eclipse.cdt.managedbuilder.core.ScannerConfigBuilder</name>
			<triggers>full,incremental,</triggers>
			<arguments>
			</arguments>
		</buildCommand>
	</buildSpec>
	<natures>
		<nature>com.android.ide.eclipse.adt.AndroidNature</nature>
		<nature>org.eclipse.jdt.core.javanature</nature>
		<nature>org.eclipse.cdt.core.cnature</nature>
		<nature>org.eclipse.cdt.core.ccnature</nature>
		<nature>org.eclipse.cdt.managedbuilder.core.managedBuildNature</nature>
		<nature>org.eclipse.cdt.managedbuilder.core.ScannerConfigNature</nature>
	</natures>
	<linkedResources>
		<link>
{java.sources}
		</link>
	</linkedResources>
</projectDescription>"""

	JavaSource = """<name>{name}</name>
			<type>2</type>
			<location>{path}</location>"""

	CProject = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?fileVersion 4.0.0?>

<cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
	<storageModule moduleId="org.eclipse.cdt.core.settings">
		<cconfiguration id="com.android.toolchain.gcc.495145846">
			<storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="com.android.toolchain.gcc.495145846" moduleId="org.eclipse.cdt.core.settings" name="Default">
				<externalSettings/>
				<extensions>
					<extension id="org.eclipse.cdt.core.ELF" point="org.eclipse.cdt.core.BinaryParser"/>
					<extension id="org.eclipse.cdt.core.VCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.CWDLocator" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.MakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GCCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GASErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GLDErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
				</extensions>
			</storageModule>
			<storageModule moduleId="cdtBuildSystem" version="4.0.0">
				<configuration artifactName="${ProjName}" buildProperties="" description="" id="com.android.toolchain.gcc.495145846" name="Default" parent="org.eclipse.cdt.build.core.emptycfg">
					<folderInfo id="com.android.toolchain.gcc.495145846.2099949476" name="/" resourcePath="">
						<toolChain id="com.android.toolchain.gcc.1075852585" name="com.android.toolchain.gcc" superClass="com.android.toolchain.gcc">
							<targetPlatform binaryParser="org.eclipse.cdt.core.ELF" id="com.android.targetPlatform.465101306" isAbstract="false" superClass="com.android.targetPlatform"/>
							<builder arguments="-j8" command="ndk-build" id="com.android.builder.773521748" keepEnvironmentInBuildfile="false" managedBuildOn="false" name="Android Builder" superClass="com.android.builder">
								<outputEntries>
									<entry flags="VALUE_WORKSPACE_PATH|RESOLVED" kind="outputPath" name="obj"/>
									<entry flags="VALUE_WORKSPACE_PATH|RESOLVED" kind="outputPath" name="libs"/>
								</outputEntries>
							</builder>
							<tool id="com.android.gcc.compiler.59181588" name="Android GCC Compiler" superClass="com.android.gcc.compiler">
								<inputType id="com.android.gcc.inputType.933235630" superClass="com.android.gcc.inputType"/>
							</tool>
						</toolChain>
					</folderInfo>
					<sourceEntries>
						<entry flags="VALUE_WORKSPACE_PATH|RESOLVED" kind="sourcePath" name="jni"/>
					</sourceEntries>
				</configuration>
			</storageModule>
			<storageModule moduleId="org.eclipse.cdt.core.externalSettings"/>
		</cconfiguration>
	</storageModule>
	<storageModule moduleId="cdtBuildSystem" version="4.0.0">
		<project id="{name}.null.346381687" name="{name}"/>
	</storageModule>
	<storageModule moduleId="scannerConfiguration">
		<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId=""/>
		<scannerConfigBuildInfo instanceId="com.android.toolchain.gcc.495145846;com.android.toolchain.gcc.495145846.2099949476;com.android.gcc.compiler.59181588;com.android.gcc.inputType.933235630">
			<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId="com.android.AndroidPerProjectProfile"/>
		</scannerConfigBuildInfo>
	</storageModule>
	<storageModule moduleId="refreshScope" versionNumber="1">
		<resource resourceType="PROJECT" workspacePath="/{name}"/>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.make.core.buildtargets"/>
</cproject>"""