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


print('')
print('osName ' + osName)
print('compiler ' + compiler)
print('')
run('ls -la')
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

if compiler == 'emcc':
	env["PATH"] += os.path.join(os.getcwd(), 'Hazel/emsdk-master') + s;
	env["PATH"] += os.path.join(os.getcwd(), 'Hazel/emsdk-master/node/12.9.1_64bit/bin') + s
	env["PATH"] += os.path.join(os.getcwd(), 'Hazel/emsdk-master/fastcomp/emscripten') + s

if osName == 'windows':
	env["PATH"] += "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\MSBuild\\Current\\Bin" + s

env["PATH"] += origionalPath

env.pop("CC", None)
env.pop("CXX", None)
env.pop("AR", None)

print('env: ' + str(env))

#Compile
run(command, env)





#install python dependencies
run("pip install plotly")
