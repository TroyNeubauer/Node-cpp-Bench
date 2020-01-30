import sys
import os
import platform
import subprocess
import shutil
from distutils.file_util import copy_file
from distutils.dir_util import mkpath

def run(command, in_env = None):
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=in_env)

	# Poll process for new output until finished
	while True:
		nextline = process.stdout.readline()
		if len(nextline) == 0 and process.poll() is not None:
			break
		sys.stdout.write(nextline.decode("utf-8"))

	exitCode = process.returncode

	if exitCode != 0:
		print('Command \'' + command + '\' failed!')
		print('Expected error code 0, got ' + str(exitCode))
		sys.exit(1)

def copyALlInDir(src, dest):
	for root, dirs, files in os.walk(src, topdown=False):
		for name in files:
			destFile = os.path.join(os.path.join(dest, root[len(src):]), name)
			print('loop file ' + root + ' ' + name + ' cp to ' + destFile)
			mkpath(os.path.abspath(os.path.join(destFile, '..')))
			copy_file(os.path.join(root, name), destFile)


CI = False

if len(sys.argv) != 3:
	print("Command line arguments either incorrect or not specifyed. Reverting to defaults")
	osName = platform.system().lower()
	if osName == "windows":
		compiler = "msvc"
	elif osName == "linux":
		compiler = "gcc"
	elif osName == "darwin":
		osName = "macosx"
		compiler = "clang"
	else:
		osName = "unknown"

else:
	print("Using command line arguments!")
	osName = sys.argv[1]
	compiler = sys.argv[2]
	if "-travis" in osName:
		osName = osName[:-len("-travis")]
		CI = True
		print("Detected CI enviorment")

print('')
print('osName ' + osName)
print('compiler ' + compiler)
print('')


premakeCommand = ''
if osName == 'linux':
	premakeCommand += 'premake5 '

elif osName == 'windows':
	premakeCommand += 'call vendor\\premake\\bin\\premake5.exe '

elif osName == 'macosx':
	print('osx is unsupported for now!')
	sys.exit(1)

else:
	print('Unknown OS! ' + osName)
	sys.exit(1)



if compiler == 'msvc':
	if CI:
		premakeCommand += '--os=windows --compiler=msc vs2017'
	else:
		premakeCommand += '--os=windows --compiler=msc vs2019'

elif compiler == 'gcc':
	premakeCommand += '--os=' + osName + ' --compiler=gcc gmake2'

elif compiler == 'clang':
	premakeCommand += '--os=' + osName + ' --compiler=gcc gmake2'

elif compiler == 'emcc':
	premakeCommand += '--os=emscripten --scripts=Hazel/vendor/premake/scripts gmake2'

else:
	print('Unknown compiler! ' + compiler)
	sys.exit(1)

print('running premake: \"' + premakeCommand + '\"')
run(premakeCommand)

#Project files have been generated compile CPP

if osName == 'windows':
	command = 'MSBuild.exe /m /p:Configuration=release NodeCppBench.sln'
else:
	command = 'make -j2 config=release'

print('running: ' + command)	
print('compiling...')

if osName == 'windows':
	s = ';'
else:
	s = ':'

env = os.environ.copy()
origionalPath = env["PATH"]
env["PATH"] = ''


if osName == 'windows':
	if CI:
		env["PATH"] += "c:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\MSBuild\\15.0\\Bin" + s
	else:
		env["PATH"] += "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\MSBuild\\Current\\Bin" + s

env["PATH"] += origionalPath

env.pop("CC", None)
env.pop("CXX", None)
env.pop("AR", None)

print('env: ' + str(env))

#Compile
run(command, env)

if osName == 'windows':
	s = '\\'
else:
	s = '/'

command = "bin" + s + "Release-" + osName + "-x86_64" + s + "Test" + s + "Test"

run(command)

if osName == "windows":
	sudoPrefix = ""
else:
	sudoPrefix = "sudo "

#install python dependencies
run(sudoPrefix + "pip install plotly")
