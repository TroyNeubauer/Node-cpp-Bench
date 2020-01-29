
#include <TUtil/TUtil.h>

#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/basic_file_sink.h>

#undef min
#undef max
#define CATCH_CONFIG_RUNNER
#define CATCH_CONFIG_ENABLE_BENCHMARKING
#include <catch2/catch.hpp>


spdlog::logger* logger;

int main(int argc, char* const argv[])
{
	std::string consolePattern = "%^[%T] %n: %$%v", filePattern = "%n-%t:[%D %H:%M %S.%e] %l: %v";

	auto coreStdOut = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
	coreStdOut->set_pattern(consolePattern);

	logger = new spdlog::logger("CPP", { coreStdOut });

	int result = Catch::Session().run(argc, argv);

#ifdef _MSC_VER
	system("PAUSE");
#endif

	return result;
}

TEST_CASE()
{
	BENCHMARK("Read and Print File")
	{

	};
	BENCHMARK("Parse Json")
	{

	};

	BENCHMARK("Parse and Re-Stringify Json")
	{

	};

}



