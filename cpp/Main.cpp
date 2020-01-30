
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

void CopyFile(const char* fileName, int times)
{
	logger->info("Copying file {} {} times", fileName, times);

	std::uint64_t size;
	TUtil::FileError error;
	const char* baseFileName = "2m.json";
	const char* file = reinterpret_cast<const char*>(TUtil::FileSystem::MapFile(baseFileName, TUtil::READ, size, &error));

	if (error != TUtil::FileError::NONE)
	{
		logger->error("Error while reading file {}, Error: {}", baseFileName, TUtil::FileErrorToString(error));
	}

	FILE* out = fopen(fileName, "wb");
	if (!out) logger->error("Cannot open file {}", fileName);
	else
	{
		for (int i = 0; i < times; i++)
		{
			fwrite(file, 1, size, out);
		}
		fclose(out);
	}
}

int main(int argc, char* const argv[])
{
	buf = new char[BUF_SIZE];
	std::string consolePattern = "%^[%T] %n: %$%v", filePattern = "%n-%t:[%D %H:%M %S.%e] %l: %v";

	auto coreStdOut = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
	coreStdOut->set_pattern(consolePattern);

	logger = new spdlog::logger("CPP", { coreStdOut });

	if (TUtil::FileSystem::Exists("20m.txt"))
		logger->info("Using cached 20mb, 60mb and 100mb files");
	else
	{
		logger->info("Creating files:");
		CopyFile("20m.txt", 10);
		CopyFile("60m.txt", 30);
		CopyFile("100m.txt", 50);
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

const char* ReadBenchBufferedC(const char* fileName)
{
	std::uint64_t size = TUtil::FileSystem::FileSize(fileName);

	char* buf = new char[1024 * 1024];
	std::size_t bytesRead;
	FILE* file = fopen(fileName, "rb");
	do
	{
		bytesRead = fread(buf, 1, 1024 * 1024, file);

	} while(bytesRead);

	fclose(file);
	delete[] buf;
	return nullptr;
}

const char* ReadBenchAllC(const char* fileName)
{
	std::uint64_t size = TUtil::FileSystem::FileSize(fileName);
	char* buf = new char[size];

	FILE* file = fopen(fileName, "rb");
	fread(buf, 1, size, file);
	fclose(file);

	delete[] buf;
	return nullptr;
}

const char* CopyBenchBufferedC(const char* fileName)
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

	} while (bytesRead);
	fclose(out);
	fclose(in);
	
	return nullptr;
}

const char* CopyBenchAllC(const char* fileName)
{
	std::size_t bytesRead;
	FILE* in = fopen(fileName, "rb");
	if (!in) logger->error("Cannot open file {}", fileName);

	FILE* out = fopen("temp.txt", "wb");
	if (!out) logger->error("Cannot open file {}", "temp.txt");

	std::uint64_t size = TUtil::FileSystem::FileSize(fileName);
	char* buf = new char[size];

	FILE* file = fopen(fileName, "rb");
	fread(buf, 1, size, in);
	fwrite(buf, 1, size, out);

	fclose(in);
	fclose(out);

	delete[] buf;
	return nullptr;
}

#define TestFunction(name, function, ...)
TEST_CASE(name) {
	BENCHMARK(name)
	{
		return function(name, __VA_ARGS__);
	};
}

template<> void TestFunction<ReadBenchBufferedC>("read C-buffered 5k.json", "5k.json");

//========== COPY ==========


//========== JSON ==========

