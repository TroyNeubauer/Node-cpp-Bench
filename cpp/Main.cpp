
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
char* buf;
const int BUF_SIZE = 1024 * 1024;

int main(int argc, char* const argv[])
{
	buf = new char[BUF_SIZE];
	std::string consolePattern = "%^[%T] %n: %$%v", filePattern = "%n-%t:[%D %H:%M %S.%e] %l: %v";

	auto coreStdOut = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
	coreStdOut->set_pattern(consolePattern);

	logger = new spdlog::logger("CPP", { coreStdOut });

	if (TUtil::FileSystem::Exists("200m.txt"))
		logger->info("Using cached 200mb file");
	else
	{
		std::uint64_t size;
		TUtil::FileError error;
		const char* fileName = "2m.json";
		const char* file = reinterpret_cast<const char*>(TUtil::FileSystem::MapFile(fileName, TUtil::READ, size, &error));

		if (error != TUtil::FileError::NONE)
		{
			logger->error("Error while reading file {}, Error: {}", fileName, TUtil::FileErrorToString(error));
		}

		TUtil::FileSystem::Delete("temp.txt");
		FILE* out = fopen("200m.txt", "wb");
		if (!out) logger->error("Cannot open file {}", "200m.txt");
		else
		{
			for (int i = 0; i < 100; i++)
			{
				fwrite(file, 1, size, out);
			}
			fclose(out);
		}

		out = fopen("20m.txt", "wb");
		if (!out) logger->error("Cannot open file {}", "20m.txt");
		else
		{
			for (int i = 0; i < 10; i++)
			{
				fwrite(file, 1, size, out);
			}
			fclose(out);
		}

		TUtil::FileSystem::UnmapFile(file);
	}

	int result = Catch::Session().run(argc, argv);

#ifdef _MSC_VER
	system("PAUSE");
#endif

	return result;
}

const char* ReadBenchTUtil(const char* fileName)
{
	std::uint64_t size;
	TUtil::FileError error;
	const char* file = reinterpret_cast<const char*>(TUtil::FileSystem::MapFile(fileName, TUtil::READ, size, &error));

	if (error != TUtil::FileError::NONE)
	{
		logger->error("Error while reading file {}, Error: {}", fileName, TUtil::FileErrorToString(error));
	}

	TUtil::FileSystem::UnmapFile(file);

	return file;
}

const char* CopyBenchTUtil(const char* fileName)
{
	std::uint64_t size;
	TUtil::FileError error;
	const char* file = reinterpret_cast<const char*>(TUtil::FileSystem::MapFile(fileName, TUtil::READ, size, &error));

	if (error != TUtil::FileError::NONE)
	{
		logger->error("Error while reading file {}, Error: {}", fileName, TUtil::FileErrorToString(error));
	}

	FILE* out = fopen("temp.txt", "wb");
	if (!out) logger->error("Cannot open file {}", "temp.txt");
	else
	{
		fwrite(file, 1, size, out);
		fclose(out);
	}

	TUtil::FileSystem::UnmapFile(file);

	return file;
}

//C file IO

const char* ReadBenchC(const char* fileName)
{
	std::uint64_t size;
	TUtil::FileError error;
	const char* file = reinterpret_cast<const char*>(TUtil::FileSystem::MapFile(fileName, TUtil::READ, size, &error));

	if (error != TUtil::FileError::NONE)
	{
		logger->error("Error while reading file {}, Error: {}", fileName, TUtil::FileErrorToString(error));
	}

	TUtil::FileSystem::UnmapFile(file);

	return file;
}

const char* CopyBenchC(const char* fileName)
{
	std::size_t bytesRead;
	FILE* in = fopen(fileName, "rb");
	if (!in) logger->error("Cannot open file {}", fileName);

	FILE* out = fopen("temp.txt", "wb");
	if (!out) logger->error("Cannot open file {}", "temp.txt");

	do
	{
		bytesRead = fread(buf, 1, BUF_SIZE, in);
		fwrite(buf, 1, bytesRead, out);

	} while (bytesRead > 0);
	fclose(out);
	fclose(in);
	
	return nullptr;
}

#define ReadBench(name) ReadBenchTUtil(name);
#define CopyBench(name) CopyBenchC(name);

TEST_CASE()
{
	BENCHMARK("read 50k.json")
	{
		return ReadBench("50k.json");
	};
	
	BENCHMARK("read 500k.json")
	{
		return ReadBench("500k.json");
	};
	
	BENCHMARK("read 2m.json")
	{
		return ReadBench("50k.json");
	};

	BENCHMARK("read 20m.txt")
	{
		return ReadBench("20m.txt");
	};

	BENCHMARK("read 200m.txt")
	{
		return ReadBench("200m.txt");
	};

	//========== COPY ==========
	BENCHMARK("copy 50k.json")
	{
		return CopyBench("50k.json");
	};

	BENCHMARK("copy 500k.json")
	{
		return CopyBench("500k.json");
	};

	BENCHMARK("copy 2m.json")
	{
		return CopyBench("2m.json");
	};

	BENCHMARK("copy 20m.txt")
	{
		return CopyBench("20m.txt");
	};

	BENCHMARK("copy 200m.txt")
	{
		return CopyBench("200m.txt");
	};
	//========== JSON ==========


	BENCHMARK("Parse Json")
	{

	};

	BENCHMARK("Parse and Re-Stringify Json")
	{

	};

}



