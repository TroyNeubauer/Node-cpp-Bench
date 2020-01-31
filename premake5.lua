
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


newoption {
	trigger     = "ci",
	description = "Used to indicate that this is a CI build",
}

workspace "NodeCppBench"
	if _OPTIONS["compiler"] then
		print("Using compiler ".._OPTIONS["compiler"])
		toolset(_OPTIONS["compiler"])
	end

	if _OPTIONS["ci"] then
		defines
		{
			"BENCH_CI_BUILD",
		}
	end

	architecture "x64"
	startproject "Test"

	configurations
	{
		"Debug",
		"Release",
	}

	staticruntime "On"

outputdir = "%{cfg.buildcfg}-%{cfg.system}-%{cfg.architecture}"

include "vendor/TUtil/TUtil_project.lua"

project "Test"
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
		"vendor/TUtil/TUtil/include",
		"vendor/spdlog/include",
		"vendor/catch2",
	}

	links 
	{
		"TUtil",
	}

	defines
	{
	}

	filter "system:windows"
		links
		{
			"Pdh.lib",
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
