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



# <?xml version="1.0" encoding="UTF-8"?>
# <Catch name="Test">
#   <Group name="Test">
#     <TestCase name="read | C-buffered | 5k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="209">
#       <BenchmarkResults name="read | C-buffered | 5k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="39510700">
#         <!--All values in nano seconds-->
#         <mean value="445059" lowerBound="431008" upperBound="464146" ci="0.95"/>
#         <standardDeviation value="83000.9" lowerBound="65483.3" upperBound="108780" ci="0.95"/>
#         <outliers variance="0.93603" lowMild="0" lowSevere="0" highMild="3" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-buffered | 50k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="210">
#       <BenchmarkResults name="read | C-buffered | 50k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="39703000">
#         <!--All values in nano seconds-->
#         <mean value="386936" lowerBound="380752" upperBound="394018" ci="0.95"/>
#         <standardDeviation value="33745.4" lowerBound="28884.4" upperBound="41110.1" ci="0.95"/>
#         <outliers variance="0.738444" lowMild="0" lowSevere="0" highMild="3" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-buffered | 500k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="211">
#       <BenchmarkResults name="read | C-buffered | 500k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="46067400">
#         <!--All values in nano seconds-->
#         <mean value="435717" lowerBound="425258" upperBound="449996" ci="0.95"/>
#         <standardDeviation value="61591.4" lowerBound="47995.8" upperBound="84350.5" ci="0.95"/>
#         <outliers variance="0.883806" lowMild="0" lowSevere="0" highMild="2" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-buffered | 2m.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="212">
#       <BenchmarkResults name="read | C-buffered | 2m.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="57202800">
#         <!--All values in nano seconds-->
#         <mean value="528079" lowerBound="518669" upperBound="540051" ci="0.95"/>
#         <standardDeviation value="53820.7" lowerBound="43923.4" upperBound="69496.2" ci="0.95"/>
#         <outliers variance="0.800131" lowMild="0" lowSevere="0" highMild="5" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-buffered | 20m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="213">
#       <BenchmarkResults name="read | C-buffered | 20m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="475449600">
#         <!--All values in nano seconds-->
#         <mean value="4207434" lowerBound="4149309" upperBound="4282975" ci="0.95"/>
#         <standardDeviation value="337200" lowerBound="274514" upperBound="423733" ci="0.95"/>
#         <outliers variance="0.707389" lowMild="0" lowSevere="0" highMild="6" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-buffered | 60m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="214">
#       <BenchmarkResults name="read | C-buffered | 60m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="1216430600">
#         <!--All values in nano seconds-->
#         <mean value="12257451" lowerBound="12182453" upperBound="12354707" ci="0.95"/>
#         <standardDeviation value="432945" lowerBound="347901" upperBound="558093" ci="0.95"/>
#         <outliers variance="0.316361" lowMild="0" lowSevere="0" highMild="4" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-All | 5k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="216">
#       <BenchmarkResults name="read | C-All | 5k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="7211600">
#         <!--All values in nano seconds-->
#         <mean value="71067" lowerBound="68703" upperBound="75030" ci="0.95"/>
#         <standardDeviation value="15279" lowerBound="10531.4" upperBound="22199.2" ci="0.95"/>
#         <outliers variance="0.946949" lowMild="0" lowSevere="0" highMild="0" highSevere="17"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-All | 50k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="217">
#       <BenchmarkResults name="read | C-All | 50k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="7147500">
#         <!--All values in nano seconds-->
#         <mean value="73231" lowerBound="70606" upperBound="77357" ci="0.95"/>
#         <standardDeviation value="16506.1" lowerBound="11932.1" upperBound="23660.5" ci="0.95"/>
#         <outliers variance="0.957166" lowMild="0" lowSevere="0" highMild="0" highSevere="19"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-All | 500k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="218">
#       <BenchmarkResults name="read | C-All | 500k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="12213900">
#         <!--All values in nano seconds-->
#         <mean value="130319" lowerBound="127627" upperBound="137490" ci="0.95"/>
#         <standardDeviation value="20573.6" lowerBound="8989.68" upperBound="42061.9" ci="0.95"/>
#         <outliers variance="0.904808" lowMild="0" lowSevere="0" highMild="1" highSevere="5"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-All | 2m.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="219">
#       <BenchmarkResults name="read | C-All | 2m.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="102603400">
#         <!--All values in nano seconds-->
#         <mean value="1058507" lowerBound="1045930" upperBound="1073754" ci="0.95"/>
#         <standardDeviation value="70700.7" lowerBound="59946.6" upperBound="85470.8" ci="0.95"/>
#         <outliers variance="0.625654" lowMild="0" lowSevere="0" highMild="4" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-All | 20m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="220">
#       <BenchmarkResults name="read | C-All | 20m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="1419386200">
#         <!--All values in nano seconds-->
#         <mean value="13472606" lowerBound="13255600" upperBound="13974010" ci="0.95"/>
#         <standardDeviation value="1.59272e+06" lowerBound="876993" upperBound="3.25505e+06" ci="0.95"/>
#         <outliers variance="0.841922" lowMild="0" lowSevere="0" highMild="0" highSevere="1"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | C-All | 60m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="221">
#       <BenchmarkResults name="read | C-All | 60m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="3794157500">
#         <!--All values in nano seconds-->
#         <mean value="39025735" lowerBound="38813877" upperBound="39416644" ci="0.95"/>
#         <standardDeviation value="1.41823e+06" lowerBound="935697" upperBound="2.5399e+06" ci="0.95"/>
#         <outliers variance="0.326323" lowMild="0" lowSevere="0" highMild="4" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | TUtil-Mapped | 5k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="223">
#       <BenchmarkResults name="read | TUtil-Mapped | 5k.json" samples="100" resamples="100000" iterations="2" clockResolution="49" estimatedDuration="9241400">
#         <!--All values in nano seconds-->
#         <mean value="46937" lowerBound="45594" upperBound="49011" ci="0.95"/>
#         <standardDeviation value="8387.28" lowerBound="6009.52" upperBound="11217" ci="0.95"/>
#         <outliers variance="0.925768" lowMild="0" lowSevere="0" highMild="1" highSevere="15"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | TUtil-Mapped | 50k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="224">
#       <BenchmarkResults name="read | TUtil-Mapped | 50k.json" samples="100" resamples="100000" iterations="2" clockResolution="49" estimatedDuration="9219200">
#         <!--All values in nano seconds-->
#         <mean value="45772" lowerBound="44209" upperBound="48735" ci="0.95"/>
#         <standardDeviation value="10560.4" lowerBound="6801.43" upperBound="18072" ci="0.95"/>
#         <outliers variance="0.957295" lowMild="0" lowSevere="0" highMild="3" highSevere="16"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | TUtil-Mapped | 500k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="225">
#       <BenchmarkResults name="read | TUtil-Mapped | 500k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="6562700">
#         <!--All values in nano seconds-->
#         <mean value="70246" lowerBound="68620" upperBound="73692" ci="0.95"/>
#         <standardDeviation value="11562.2" lowerBound="6211.56" upperBound="19384" ci="0.95"/>
#         <outliers variance="0.915118" lowMild="0" lowSevere="0" highMild="3" highSevere="6"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | TUtil-Mapped | 2m.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="226">
#       <BenchmarkResults name="read | TUtil-Mapped | 2m.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="5936700">
#         <!--All values in nano seconds-->
#         <mean value="64758" lowerBound="62868" upperBound="68767" ci="0.95"/>
#         <standardDeviation value="13440.9" lowerBound="7447.53" upperBound="23347.9" ci="0.95"/>
#         <outliers variance="0.946727" lowMild="0" lowSevere="0" highMild="2" highSevere="9"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | TUtil-Mapped | 20m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="227">
#       <BenchmarkResults name="read | TUtil-Mapped | 20m.txt" samples="100" resamples="100000" iterations="2" clockResolution="49" estimatedDuration="9365800">
#         <!--All values in nano seconds-->
#         <mean value="48220" lowerBound="46780" upperBound="51108" ci="0.95"/>
#         <standardDeviation value="9959.91" lowerBound="6200.97" upperBound="17951.6" ci="0.95"/>
#         <outliers variance="0.946695" lowMild="0" lowSevere="0" highMild="4" highSevere="14"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="read | TUtil-Mapped | 60m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="228">
#       <BenchmarkResults name="read | TUtil-Mapped | 60m.txt" samples="100" resamples="100000" iterations="2" clockResolution="49" estimatedDuration="9507800">
#         <!--All values in nano seconds-->
#         <mean value="48029" lowerBound="46198" upperBound="50876" ci="0.95"/>
#         <standardDeviation value="11500.4" lowerBound="8343.55" upperBound="15410.4" ci="0.95"/>
#         <outliers variance="0.957488" lowMild="0" lowSevere="0" highMild="3" highSevere="12"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-buffered | 5k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="232">
#       <BenchmarkResults name="copy | C-buffered | 5k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="181814000">
#         <!--All values in nano seconds-->
#         <mean value="1728217" lowerBound="1699445" upperBound="1761001" ci="0.95"/>
#         <standardDeviation value="156914" lowerBound="137542" upperBound="181721" ci="0.95"/>
#         <outliers variance="0.758762" lowMild="0" lowSevere="0" highMild="1" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-buffered | 50k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="233">
#       <BenchmarkResults name="copy | C-buffered | 50k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="606039600">
#         <!--All values in nano seconds-->
#         <mean value="6138374" lowerBound="6082654" upperBound="6200357" ci="0.95"/>
#         <standardDeviation value="299556" lowerBound="264422" upperBound="352213" ci="0.95"/>
#         <outliers variance="0.464883" lowMild="0" lowSevere="0" highMild="1" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-buffered | 500k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="234">
#       <BenchmarkResults name="copy | C-buffered | 500k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="622644000">
#         <!--All values in nano seconds-->
#         <mean value="6186454" lowerBound="6134295" upperBound="6248191" ci="0.95"/>
#         <standardDeviation value="289846" lowerBound="246801" upperBound="365077" ci="0.95"/>
#         <outliers variance="0.444938" lowMild="0" lowSevere="0" highMild="3" highSevere="1"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-buffered | 2m.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="235">
#       <BenchmarkResults name="copy | C-buffered | 2m.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="670703100">
#         <!--All values in nano seconds-->
#         <mean value="6725360" lowerBound="6673413" upperBound="6785251" ci="0.95"/>
#         <standardDeviation value="285354" lowerBound="241983" upperBound="346008" ci="0.95"/>
#         <outliers variance="0.39541" lowMild="0" lowSevere="0" highMild="4" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-buffered | 20m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="236">
#       <BenchmarkResults name="copy | C-buffered | 20m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="1790356200">
#         <!--All values in nano seconds-->
#         <mean value="18246089" lowerBound="17944479" upperBound="18651267" ci="0.95"/>
#         <standardDeviation value="1.77369e+06" lowerBound="1.41656e+06" upperBound="2.24988e+06" ci="0.95"/>
#         <outliers variance="0.779681" lowMild="0" lowSevere="0" highMild="8" highSevere="3"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-buffered | 60m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="237">
#       <BenchmarkResults name="copy | C-buffered | 60m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="4285375000">
#         <!--All values in nano seconds-->
#         <mean value="43122555" lowerBound="42746487" upperBound="43719715" ci="0.95"/>
#         <standardDeviation value="2.37286e+06" lowerBound="1.64241e+06" upperBound="3.46205e+06" ci="0.95"/>
#         <outliers variance="0.53439" lowMild="0" lowSevere="0" highMild="0" highSevere="3"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-All | 5k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="239">
#       <BenchmarkResults name="copy | C-All | 5k.json">
#         <failed message="bad array new length"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-All | 50k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="240">
#       <BenchmarkResults name="copy | C-All | 50k.json">
#         <failed message="bad array new length"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-All | 500k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="241">
#       <BenchmarkResults name="copy | C-All | 500k.json">
#         <failed message="bad array new length"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-All | 2m.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="242">
#       <BenchmarkResults name="copy | C-All | 2m.json">
#         <failed message="bad array new length"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-All | 20m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="243">
#       <BenchmarkResults name="copy | C-All | 20m.txt">
#         <failed message="bad array new length"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | C-All | 60m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="244">
#       <BenchmarkResults name="copy | C-All | 60m.txt">
#         <failed message="bad array new length"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | TUtil-Mapped | 5k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="246">
#       <BenchmarkResults name="copy | TUtil-Mapped | 5k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="156386400">
#         <!--All values in nano seconds-->
#         <mean value="1783051" lowerBound="1751560" upperBound="1821092" ci="0.95"/>
#         <standardDeviation value="176114" lowerBound="147963" upperBound="215208" ci="0.95"/>
#         <outliers variance="0.78975" lowMild="0" lowSevere="0" highMild="6" highSevere="0"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | TUtil-Mapped | 50k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="247">
#       <BenchmarkResults name="copy | TUtil-Mapped | 50k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="711381800">
#         <!--All values in nano seconds-->
#         <mean value="7012267" lowerBound="6957321" upperBound="7106969" ci="0.95"/>
#         <standardDeviation value="357169" lowerBound="228585" upperBound="565999" ci="0.95"/>
#         <outliers variance="0.494335" lowMild="0" lowSevere="0" highMild="5" highSevere="3"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | TUtil-Mapped | 500k.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="248">
#       <BenchmarkResults name="copy | TUtil-Mapped | 500k.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="744478700">
#         <!--All values in nano seconds-->
#         <mean value="6588212" lowerBound="6525352" upperBound="6674520" ci="0.95"/>
#         <standardDeviation value="372438" lowerBound="293518" upperBound="520280" ci="0.95"/>
#         <outliers variance="0.544667" lowMild="0" lowSevere="0" highMild="4" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | TUtil-Mapped | 2m.json" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="249">
#       <BenchmarkResults name="copy | TUtil-Mapped | 2m.json" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="739113700">
#         <!--All values in nano seconds-->
#         <mean value="7302179" lowerBound="7221961" upperBound="7496795" ci="0.95"/>
#         <standardDeviation value="601398" lowerBound="315186" upperBound="1.23507e+06" ci="0.95"/>
#         <outliers variance="0.717724" lowMild="0" lowSevere="0" highMild="1" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | TUtil-Mapped | 20m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="250">
#       <BenchmarkResults name="copy | TUtil-Mapped | 20m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="2605515000">
#         <!--All values in nano seconds-->
#         <mean value="26271210" lowerBound="25931980" upperBound="27032356" ci="0.95"/>
#         <standardDeviation value="2.47125e+06" lowerBound="1.32877e+06" upperBound="4.98078e+06" ci="0.95"/>
#         <outliers variance="0.769257" lowMild="0" lowSevere="0" highMild="0" highSevere="2"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <TestCase name="copy | TUtil-Mapped | 60m.txt" filename="C:\C++\Node-cpp-Bench\cpp\Main.cpp" line="251">
#       <BenchmarkResults name="copy | TUtil-Mapped | 60m.txt" samples="100" resamples="100000" iterations="1" clockResolution="49" estimatedDuration="14473920000">
#         <!--All values in nano seconds-->
#         <mean value="185527891" lowerBound="139151093" upperBound="310149374" ci="0.95"/>
#         <standardDeviation value="3.49436e+08" lowerBound="1.01181e+08" upperBound="6.96674e+08" ci="0.95"/>
#         <outliers variance="0.989957" lowMild="0" lowSevere="0" highMild="0" highSevere="9"/>
#       </BenchmarkResults>
#       <OverallResult success="true"/>
#     </TestCase>
#     <OverallResults successes="0" failures="0" expectedFailures="0"/>
#   </Group>
#   <OverallResults successes="0" failures="0" expectedFailures="0"/>
# </Catch>

