
newoption {
	trigger     = "compiler",
	description = "Choose a compiler",
	allowed =
	{
		{ "clang",    "Clang LLVM Compiler" },
		{ "gcc",  "GNU Compiler" },
		{ "msc",  "MSVC (Windows only)" },
		{ "", "Default" }
	}
}


workspace "NodeCppBench"
	if _OPTIONS["compiler"] then
		print("Using compiler ".._OPTIONS["compiler"])
		toolset(_OPTIONS["compiler"])
	end
	architecture "x64"
	startproject "Test"

	configurations
	{
		"Debug",
		"Release",
	}

outputdir = "%{cfg.buildcfg}-%{cfg.system}-%{cfg.architecture}"

include "vendor/TUtil/TUtil_project.lua"

project "Test"
	location "Test"
	kind "ConsoleApp"
	language "C++"
	cppdialect "C++17"
	staticruntime "on"

	targetdir ("bin/" .. outputdir .. "/%{prj.name}")
	objdir ("bin-int/" .. outputdir .. "/%{prj.name}")

	files
	{
		"cpp/**.h",
		"cpp/**.cpp"
	}

	includedirs
	{
		"vendor/TUtil/TUtil/include"
	}

	links 
	{
		"TUtil",
	}

	defines
	{
	}



	filter "configurations:Debug"
		runtime "Debug"
		symbols "on"
		floatingpoint "Strict"

	filter "configurations:Release"
		runtime "Release"
		optimize "speed"
		inlining "auto"
		floatingpoint "Fast"
