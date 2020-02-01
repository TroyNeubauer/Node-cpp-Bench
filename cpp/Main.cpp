
#include <malloc.h>

#include <TUtil/TUtil.h>

#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/basic_file_sink.h>

#undef min
#undef max
#define CATCH_CONFIG_RUNNER
#define CATCH_CONFIG_ENABLE_BENCHMARKING
#include <catch2/catch.hpp>


#define ENABLE_LONG_BENCHMARKS 1

spdlog::logger* logger;

void CopyFileWithTimes(const char* fileName, int times)
{
	logger->info("Copying file {} {} times", fileName, times);

	std::uint64_t size;
	TUtil::FileError error;
	const char* baseFileName = "samples/1m.json";
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

char* buf100m;

int main(int argc, char* const argv[])
{
	std::string pattern = "%^[%T] %n: %$%v";
	buf100m = static_cast<char*>(malloc(130 * 1024 * 1024));

	auto coreStdOut = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
	coreStdOut->set_pattern(pattern);

	logger = new spdlog::logger("CPP", { coreStdOut });
#ifdef BENCH_CI_BUILD
	logger->set_level(spdlog::level::level_enum::off);
#else
	logger->info("Beginning C++ Bench program");
#endif

	if (TUtil::FileSystem::Exists("samples/5m.txt"))
		logger->info("Using cached text files");
	else
	{
		logger->info("Creating files:");
		CopyFileWithTimes("samples/5m.txt", 5);
		CopyFileWithTimes("samples/10m.txt", 10);
		CopyFileWithTimes("samples/20m.txt", 20);
		CopyFileWithTimes("samples/40m.txt", 40);
		CopyFileWithTimes("samples/60m.txt", 60);
	}

	int result = Catch::Session().run(argc, argv);

#ifndef BENCH_CI_BUILD
	system("PAUSE");
#endif
	return result;
}

//TUtil Memory Mapped file IO

const char* ReadMappedTUtil(const char* fileName)
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

const char* CopyMappedTUtil(const char* fileName)
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

//C file IO (buffered)

const char* ReadBufferedC(const char* fileName, char* buf, std::size_t bufSize)
{

	std::size_t bytesRead;
	FILE* file = fopen(fileName, "rb");
	if (!file) { logger->error("Cannot open file {}", fileName); return nullptr; }

	do
	{
		bytesRead = fread(buf, 1, bufSize, file);

	} while(bytesRead);

	fclose(file);
	return nullptr;
}


const char* CopyBufferedC(const char* fileName, char* buf, std::size_t bufSize)
{
	std::size_t bytesRead;
	FILE* in = fopen(fileName, "rb");
	if (!in) { logger->error("Cannot open file {}", fileName); return nullptr; }

	FILE* out = fopen("temp.txt", "wb");
	if (!out) { logger->error("Cannot open file {}", "temp.txt"); return nullptr; }

	do
	{
		bytesRead = fread(buf, 1, bufSize, in);
		fwrite(buf, 1, bytesRead, out);

	} while (bytesRead);
	fclose(out);
	fclose(in);
	
	return nullptr;
}

//C file IO (allocates one big buffer the size of the file)

const char* ReadAllC(const char* fileName)
{
	std::uint64_t size = TUtil::FileSystem::FileSize(fileName);
	char* buf = static_cast<char*>(malloc(size));

	FILE* file = fopen(fileName, "rb");
	if (!file) { logger->error("Cannot open file {}", fileName); return nullptr; }

	fread(buf, 1, size, file);
	fclose(file);

	free(buf);
	return nullptr;
}

const char* CopyAllC(const char* fileName)
{
	std::uint64_t size = TUtil::FileSystem::FileSize(fileName);

	FILE* in = fopen(fileName, "rb");
	if (!in) logger->error("Cannot open file {}", fileName);

	FILE* out = fopen("temp.txt", "wb");
	if (!out) logger->error("Cannot open file {}", "temp.txt");


	char* buf = static_cast<char*>(malloc(size));

	FILE* file = fopen(fileName, "rb");
	if (fread(buf, 1, size, in) != size) REQUIRE_FALSE("File was not read fully!");
	if (fwrite(buf, 1, size, out) != size) REQUIRE_FALSE("File was not written fully!");

	fclose(in);
	fclose(out);

	free(buf);
	return nullptr;
}


#define TestFunction(name, function, ...)		\
TEST_CASE(name) {								\
	BENCHMARK(name)								\
	{											\
		function(__VA_ARGS__);					\
	};											\
}												\
												\


//========== READ ==========
//NAME FORMAT: group | strategy | operation

char buf500k[600 * 1024];

//C-Buffered of different sizes
//128 BYTES
TestFunction("read | C-Buffered-128b | 100b.json", ReadBufferedC, "samples/100b.json", buf500k, 128)
TestFunction("read | C-Buffered-128b | 1k.json", ReadBufferedC, "samples/1k.json", buf500k, 128)
TestFunction("read | C-Buffered-128b | 5k.json", ReadBufferedC, "samples/5k.json", buf500k, 128)
TestFunction("read | C-Buffered-128b | 10k.json", ReadBufferedC, "samples/10k.json", buf500k, 128)
TestFunction("read | C-Buffered-128b | 50k.json", ReadBufferedC, "samples/50k.json", buf500k, 128)
TestFunction("read | C-Buffered-128b | 100k.json", ReadBufferedC, "samples/100k.json", buf500k, 128)
TestFunction("read | C-Buffered-128b | 500k.json", ReadBufferedC, "samples/500k.json", buf500k, 128)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | C-Buffered-128b | 1m.json", ReadBufferedC, "samples/1m.json", buf500k, 128)
	TestFunction("read | C-Buffered-128b | 5m.txt", ReadBufferedC, "samples/5m.txt", buf500k, 128)
	TestFunction("read | C-Buffered-128b | 10m.txt", ReadBufferedC, "samples/10m.txt", buf500k, 128)
	TestFunction("read | C-Buffered-128b | 20m.txt", ReadBufferedC, "samples/20m.txt", buf500k, 128)
	TestFunction("read | C-Buffered-128b | 40m.txt", ReadBufferedC, "samples/40m.txt", buf500k, 128)
	TestFunction("read | C-Buffered-128b | 60m.txt", ReadBufferedC, "samples/60m.txt", buf500k, 128)
#endif

//512 BYTES
TestFunction("read | C-Buffered-512b | 100b.json", ReadBufferedC, "samples/100b.json", buf500k, 512)
TestFunction("read | C-Buffered-512b | 1k.json", ReadBufferedC, "samples/1k.json", buf500k, 512)
TestFunction("read | C-Buffered-512b | 5k.json", ReadBufferedC, "samples/5k.json", buf500k, 512)
TestFunction("read | C-Buffered-512b | 10k.json", ReadBufferedC, "samples/10k.json", buf500k, 512)
TestFunction("read | C-Buffered-512b | 50k.json", ReadBufferedC, "samples/50k.json", buf500k, 512)
TestFunction("read | C-Buffered-512b | 100k.json", ReadBufferedC, "samples/100k.json", buf500k, 512)
TestFunction("read | C-Buffered-512b | 500k.json", ReadBufferedC, "samples/500k.json", buf500k, 512)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | C-Buffered-512b | 1m.json", ReadBufferedC, "samples/1m.json", buf500k, 512)
	TestFunction("read | C-Buffered-512b | 5m.txt", ReadBufferedC, "samples/5m.txt", buf500k, 512)
	TestFunction("read | C-Buffered-512b | 10m.txt", ReadBufferedC, "samples/10m.txt", buf500k, 512)
	TestFunction("read | C-Buffered-512b | 20m.txt", ReadBufferedC, "samples/20m.txt", buf500k, 512)
	TestFunction("read | C-Buffered-512b | 40m.txt", ReadBufferedC, "samples/40m.txt", buf500k, 512)
	TestFunction("read | C-Buffered-512b | 60m.txt", ReadBufferedC, "samples/60m.txt", buf500k, 512)
#endif

//4096 BYTES (4k)
TestFunction("read | C-Buffered-4k | 100b.json", ReadBufferedC, "samples/100b.json", buf500k, 4 * 1024)
TestFunction("read | C-Buffered-4k | 1k.json", ReadBufferedC, "samples/1k.json", buf500k, 4 * 1024)
TestFunction("read | C-Buffered-4k | 5k.json", ReadBufferedC, "samples/5k.json", buf500k, 4 * 1024)
TestFunction("read | C-Buffered-4k | 10k.json", ReadBufferedC, "samples/10k.json", buf500k, 4 * 1024)
TestFunction("read | C-Buffered-4k | 50k.json", ReadBufferedC, "samples/50k.json", buf500k, 4 * 1024)
TestFunction("read | C-Buffered-4k | 100k.json", ReadBufferedC, "samples/100k.json", buf500k, 4 * 1024)
TestFunction("read | C-Buffered-4k | 500k.json", ReadBufferedC, "samples/500k.json", buf500k, 4 * 1024)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | C-Buffered-4k | 1m.json", ReadBufferedC, "samples/1m.json", buf500k, 4 * 1024)
	TestFunction("read | C-Buffered-4k | 5m.txt", ReadBufferedC, "samples/5m.txt", buf500k, 4 * 1024)
	TestFunction("read | C-Buffered-4k | 10m.txt", ReadBufferedC, "samples/10m.txt", buf500k, 4 * 1024)
	TestFunction("read | C-Buffered-4k | 20m.txt", ReadBufferedC, "samples/20m.txt", buf500k, 4 * 1024)
	TestFunction("read | C-Buffered-4k | 40m.txt", ReadBufferedC, "samples/40m.txt", buf500k, 4 * 1024)
	TestFunction("read | C-Buffered-4k | 60m.txt", ReadBufferedC, "samples/60m.txt", buf500k, 4 * 1024)
#endif

//64k
TestFunction("read | C-Buffered-64k | 100b.json", ReadBufferedC, "samples/100b.json", buf500k, 64 * 1024)
TestFunction("read | C-Buffered-64k | 1k.json", ReadBufferedC, "samples/1k.json", buf500k, 64 * 1024)
TestFunction("read | C-Buffered-64k | 5k.json", ReadBufferedC, "samples/5k.json", buf500k, 64 * 1024)
TestFunction("read | C-Buffered-64k | 10k.json", ReadBufferedC, "samples/10k.json", buf500k, 64 * 1024)
TestFunction("read | C-Buffered-64k | 50k.json", ReadBufferedC, "samples/50k.json", buf500k, 64 * 1024)
TestFunction("read | C-Buffered-64k | 100k.json", ReadBufferedC, "samples/100k.json", buf500k, 64 * 1024)
TestFunction("read | C-Buffered-64k | 500k.json", ReadBufferedC, "samples/500k.json", buf500k, 64 * 1024)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | C-Buffered-64k | 1m.json", ReadBufferedC, "samples/1m.json", buf500k, 64 * 1024)
	TestFunction("read | C-Buffered-64k | 5m.txt", ReadBufferedC, "samples/5m.txt", buf500k, 64 * 1024)
	TestFunction("read | C-Buffered-64k | 10m.txt", ReadBufferedC, "samples/10m.txt", buf500k, 64 * 1024)
	TestFunction("read | C-Buffered-64k | 20m.txt", ReadBufferedC, "samples/20m.txt", buf500k, 64 * 1024)
	TestFunction("read | C-Buffered-64k | 40m.txt", ReadBufferedC, "samples/40m.txt", buf500k, 64 * 1024)
	TestFunction("read | C-Buffered-64k | 60m.txt", ReadBufferedC, "samples/60m.txt", buf500k, 64 * 1024)
#endif

//1m
TestFunction("read | C-Buffered-1m | 100b.json", ReadBufferedC, "samples/100b.json", buf100m, 1024 * 1024)
TestFunction("read | C-Buffered-1m | 1k.json", ReadBufferedC, "samples/1k.json", buf100m, 1024 * 1024)
TestFunction("read | C-Buffered-1m | 5k.json", ReadBufferedC, "samples/5k.json", buf100m, 1024 * 1024)
TestFunction("read | C-Buffered-1m | 10k.json", ReadBufferedC, "samples/10k.json", buf100m, 1024 * 1024)
TestFunction("read | C-Buffered-1m | 50k.json", ReadBufferedC, "samples/50k.json", buf100m, 1024 * 1024)
TestFunction("read | C-Buffered-1m | 100k.json", ReadBufferedC, "samples/100k.json", buf100m, 1024 * 1024)
TestFunction("read | C-Buffered-1m | 500k.json", ReadBufferedC, "samples/500k.json", buf100m, 1024 * 1024)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | C-Buffered-1m | 1m.json", ReadBufferedC, "samples/1m.json", buf100m, 1024 * 1024)
	TestFunction("read | C-Buffered-1m | 5m.txt", ReadBufferedC, "samples/5m.txt", buf100m, 1024 * 1024)
	TestFunction("read | C-Buffered-1m | 10m.txt", ReadBufferedC, "samples/10m.txt", buf100m, 1024 * 1024)
	TestFunction("read | C-Buffered-1m | 20m.txt", ReadBufferedC, "samples/20m.txt", buf100m, 1024 * 1024)
	TestFunction("read | C-Buffered-1m | 40m.txt", ReadBufferedC, "samples/40m.txt", buf100m, 1024 * 1024)
	TestFunction("read | C-Buffered-1m | 60m.txt", ReadBufferedC, "samples/60m.txt", buf100m, 1024 * 1024)
#endif

//Other strats
TestFunction("read | C-All | 100b.json", ReadAllC, "samples/100b.json")
TestFunction("read | C-All | 1k.json", ReadAllC, "samples/1k.json")
TestFunction("read | C-All | 5k.json", ReadAllC, "samples/5k.json")
TestFunction("read | C-All | 10k.json", ReadAllC, "samples/10k.json")
TestFunction("read | C-All | 50k.json", ReadAllC, "samples/50k.json")
TestFunction("read | C-All | 100k.json", ReadAllC, "samples/100k.json")
TestFunction("read | C-All | 500k.json", ReadAllC, "samples/500k.json")

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | C-All | 1m.json", ReadAllC, "samples/1m.json")
	TestFunction("read | C-All | 5m.txt", ReadAllC, "samples/5m.txt")
	TestFunction("read | C-All | 10m.txt", ReadAllC, "samples/10m.txt")
	TestFunction("read | C-All | 20m.txt", ReadAllC, "samples/20m.txt")
	TestFunction("read | C-All | 40m.txt", ReadAllC, "samples/40m.txt")
	TestFunction("read | C-All | 60m.txt", ReadAllC, "samples/60m.txt")
#endif


TestFunction("read | TUtil-Mapped | 100b.json", ReadMappedTUtil, "samples/100b.json")
TestFunction("read | TUtil-Mapped | 1k.json", ReadMappedTUtil, "samples/1k.json")
TestFunction("read | TUtil-Mapped | 5k.json", ReadMappedTUtil, "samples/5k.json")
TestFunction("read | TUtil-Mapped | 10k.json", ReadMappedTUtil, "samples/10k.json")
TestFunction("read | TUtil-Mapped | 50k.json", ReadMappedTUtil, "samples/50k.json")
TestFunction("read | TUtil-Mapped | 100k.json", ReadMappedTUtil, "samples/100k.json")
TestFunction("read | TUtil-Mapped | 500k.json", ReadMappedTUtil, "samples/500k.json")

#if ENABLE_LONG_BENCHMARKS
	TestFunction("read | TUtil-Mapped | 1m.json", ReadMappedTUtil, "samples/1m.json")
	TestFunction("read | TUtil-Mapped | 5m.txt", ReadMappedTUtil, "samples/5m.txt")
	TestFunction("read | TUtil-Mapped | 10m.txt", ReadMappedTUtil, "samples/10m.txt")
	TestFunction("read | TUtil-Mapped | 20m.txt", ReadMappedTUtil, "samples/20m.txt")
	TestFunction("read | TUtil-Mapped | 40m.txt", ReadMappedTUtil, "samples/40m.txt")
	TestFunction("read | TUtil-Mapped | 60m.txt", ReadMappedTUtil, "samples/60m.txt")
#endif

//========== COPY ==========


//C-Buffered copy of different sizes
//128 BYTES
TestFunction("copy | C-Buffered-128b | 100b.json", CopyBufferedC, "samples/100b.json", buf500k, 128)
TestFunction("copy | C-Buffered-128b | 1k.json", CopyBufferedC, "samples/1k.json", buf500k, 128)
TestFunction("copy | C-Buffered-128b | 5k.json", CopyBufferedC, "samples/5k.json", buf500k, 128)
TestFunction("copy | C-Buffered-128b | 10k.json", CopyBufferedC, "samples/10k.json", buf500k, 128)
TestFunction("copy | C-Buffered-128b | 50k.json", CopyBufferedC, "samples/50k.json", buf500k, 128)
TestFunction("copy | C-Buffered-128b | 100k.json", CopyBufferedC, "samples/100k.json", buf500k, 128)
TestFunction("copy | C-Buffered-128b | 500k.json", CopyBufferedC, "samples/500k.json", buf500k, 128)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | C-Buffered-128b | 1m.json", CopyBufferedC, "samples/1m.json", buf500k, 128)
	TestFunction("copy | C-Buffered-128b | 5m.txt", CopyBufferedC, "samples/5m.txt", buf500k, 128)
	TestFunction("copy | C-Buffered-128b | 10m.txt", CopyBufferedC, "samples/10m.txt", buf500k, 128)
	TestFunction("copy | C-Buffered-128b | 20m.txt", CopyBufferedC, "samples/20m.txt", buf500k, 128)
	TestFunction("copy | C-Buffered-128b | 40m.txt", CopyBufferedC, "samples/40m.txt", buf500k, 128)
	TestFunction("copy | C-Buffered-128b | 60m.txt", CopyBufferedC, "samples/60m.txt", buf500k, 128)
#endif

//512 BYTES
TestFunction("copy | C-Buffered-512b | 100b.json", CopyBufferedC, "samples/100b.json", buf500k, 512)
TestFunction("copy | C-Buffered-512b | 1k.json", CopyBufferedC, "samples/1k.json", buf500k, 512)
TestFunction("copy | C-Buffered-512b | 5k.json", CopyBufferedC, "samples/5k.json", buf500k, 512)
TestFunction("copy | C-Buffered-512b | 10k.json", CopyBufferedC, "samples/10k.json", buf500k, 512)
TestFunction("copy | C-Buffered-512b | 50k.json", CopyBufferedC, "samples/50k.json", buf500k, 512)
TestFunction("copy | C-Buffered-512b | 100k.json", CopyBufferedC, "samples/100k.json", buf500k, 512)
TestFunction("copy | C-Buffered-512b | 500k.json", CopyBufferedC, "samples/500k.json", buf500k, 512)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | C-Buffered-512b | 1m.json", CopyBufferedC, "samples/1m.json", buf500k, 512)
	TestFunction("copy | C-Buffered-512b | 5m.txt", CopyBufferedC, "samples/5m.txt", buf500k, 512)
	TestFunction("copy | C-Buffered-512b | 10m.txt", CopyBufferedC, "samples/10m.txt", buf500k, 512)
	TestFunction("copy | C-Buffered-512b | 20m.txt", CopyBufferedC, "samples/20m.txt", buf500k, 512)
	TestFunction("copy | C-Buffered-512b | 40m.txt", CopyBufferedC, "samples/40m.txt", buf500k, 512)
	TestFunction("copy | C-Buffered-512b | 60m.txt", CopyBufferedC, "samples/60m.txt", buf500k, 512)
#endif

//4096 BYTES (4k)
TestFunction("copy | C-Buffered-4k | 100b.json", CopyBufferedC, "samples/100b.json", buf500k, 4 * 1024)
TestFunction("copy | C-Buffered-4k | 1k.json", CopyBufferedC, "samples/1k.json", buf500k, 4 * 1024)
TestFunction("copy | C-Buffered-4k | 5k.json", CopyBufferedC, "samples/5k.json", buf500k, 4 * 1024)
TestFunction("copy | C-Buffered-4k | 10k.json", CopyBufferedC, "samples/10k.json", buf500k, 4 * 1024)
TestFunction("copy | C-Buffered-4k | 50k.json", CopyBufferedC, "samples/50k.json", buf500k, 4 * 1024)
TestFunction("copy | C-Buffered-4k | 100k.json", CopyBufferedC, "samples/100k.json", buf500k, 4 * 1024)
TestFunction("copy | C-Buffered-4k | 500k.json", CopyBufferedC, "samples/500k.json", buf500k, 4 * 1024)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | C-Buffered-4k | 1m.json", CopyBufferedC, "samples/1m.json", buf500k, 4 * 1024)
	TestFunction("copy | C-Buffered-4k | 5m.txt", CopyBufferedC, "samples/5m.txt", buf500k, 4 * 1024)
	TestFunction("copy | C-Buffered-4k | 10m.txt", CopyBufferedC, "samples/10m.txt", buf500k, 4 * 1024)
	TestFunction("copy | C-Buffered-4k | 20m.txt", CopyBufferedC, "samples/20m.txt", buf500k, 4 * 1024)
	TestFunction("copy | C-Buffered-4k | 40m.txt", CopyBufferedC, "samples/40m.txt", buf500k, 4 * 1024)
	TestFunction("copy | C-Buffered-4k | 60m.txt", CopyBufferedC, "samples/60m.txt", buf500k, 4 * 1024)
#endif

//64k
TestFunction("copy | C-Buffered-64k | 100b.json", CopyBufferedC, "samples/100b.json", buf500k, 64 * 1024)
TestFunction("copy | C-Buffered-64k | 1k.json", CopyBufferedC, "samples/1k.json", buf500k, 64 * 1024)
TestFunction("copy | C-Buffered-64k | 5k.json", CopyBufferedC, "samples/5k.json", buf500k, 64 * 1024)
TestFunction("copy | C-Buffered-64k | 10k.json", CopyBufferedC, "samples/10k.json", buf500k, 64 * 1024)
TestFunction("copy | C-Buffered-64k | 50k.json", CopyBufferedC, "samples/50k.json", buf500k, 64 * 1024)
TestFunction("copy | C-Buffered-64k | 100k.json", CopyBufferedC, "samples/100k.json", buf500k, 64 * 1024)
TestFunction("copy | C-Buffered-64k | 500k.json", CopyBufferedC, "samples/500k.json", buf500k, 64 * 1024)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | C-Buffered-64k | 1m.json", CopyBufferedC, "samples/1m.json", buf500k, 64 * 1024)
	TestFunction("copy | C-Buffered-64k | 5m.txt", CopyBufferedC, "samples/5m.txt", buf500k, 64 * 1024)
	TestFunction("copy | C-Buffered-64k | 10m.txt", CopyBufferedC, "samples/10m.txt", buf500k, 64 * 1024)
	TestFunction("copy | C-Buffered-64k | 20m.txt", CopyBufferedC, "samples/20m.txt", buf500k, 64 * 1024)
	TestFunction("copy | C-Buffered-64k | 40m.txt", CopyBufferedC, "samples/40m.txt", buf500k, 64 * 1024)
	TestFunction("copy | C-Buffered-64k | 60m.txt", CopyBufferedC, "samples/60m.txt", buf500k, 64 * 1024)
#endif

//1m
TestFunction("copy | C-Buffered-1m | 100b.json", CopyBufferedC, "samples/100b.json", buf100m, 1024 * 1024)
TestFunction("copy | C-Buffered-1m | 1k.json", CopyBufferedC, "samples/1k.json", buf100m, 1024 * 1024)
TestFunction("copy | C-Buffered-1m | 5k.json", CopyBufferedC, "samples/5k.json", buf100m, 1024 * 1024)
TestFunction("copy | C-Buffered-1m | 10k.json", CopyBufferedC, "samples/10k.json", buf100m, 1024 * 1024)
TestFunction("copy | C-Buffered-1m | 50k.json", CopyBufferedC, "samples/50k.json", buf100m, 1024 * 1024)
TestFunction("copy | C-Buffered-1m | 100k.json", CopyBufferedC, "samples/100k.json", buf100m, 1024 * 1024)
TestFunction("copy | C-Buffered-1m | 500k.json", CopyBufferedC, "samples/500k.json", buf100m, 1024 * 1024)

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | C-Buffered-1m | 1m.json", CopyBufferedC, "samples/1m.json", buf100m, 1024 * 1024)
	TestFunction("copy | C-Buffered-1m | 5m.txt", CopyBufferedC, "samples/5m.txt", buf100m, 1024 * 1024)
	TestFunction("copy | C-Buffered-1m | 10m.txt", CopyBufferedC, "samples/10m.txt", buf100m, 1024 * 1024)
	TestFunction("copy | C-Buffered-1m | 20m.txt", CopyBufferedC, "samples/20m.txt", buf100m, 1024 * 1024)
	TestFunction("copy | C-Buffered-1m | 40m.txt", CopyBufferedC, "samples/40m.txt", buf100m, 1024 * 1024)
	TestFunction("copy | C-Buffered-1m | 60m.txt", CopyBufferedC, "samples/60m.txt", buf100m, 1024 * 1024)
#endif

//Other strats

TestFunction("copy | C-All | 100b.json", CopyAllC, "samples/100b.json")
TestFunction("copy | C-All | 1k.json", CopyAllC, "samples/1k.json")
TestFunction("copy | C-All | 5k.json", CopyAllC, "samples/5k.json")
TestFunction("copy | C-All | 10k.json", CopyAllC, "samples/10k.json")
TestFunction("copy | C-All | 50k.json", CopyAllC, "samples/50k.json")
TestFunction("copy | C-All | 100k.json", CopyAllC, "samples/100k.json")
TestFunction("copy | C-All | 500k.json", CopyAllC, "samples/500k.json")

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | C-All | 1m.json", CopyAllC, "samples/1m.json")
	TestFunction("copy | C-All | 5m.txt", CopyAllC, "samples/5m.txt")
	TestFunction("copy | C-All | 10m.txt", CopyAllC, "samples/10m.txt")
	TestFunction("copy | C-All | 20m.txt", CopyAllC, "samples/20m.txt")
	TestFunction("copy | C-All | 40m.txt", CopyAllC, "samples/40m.txt")
	TestFunction("copy | C-All | 60m.txt", CopyAllC, "samples/60m.txt")
#endif



TestFunction("copy | TUtil-Mapped | 100b.json", CopyMappedTUtil, "samples/100b.json")
TestFunction("copy | TUtil-Mapped | 1k.json", CopyMappedTUtil, "samples/1k.json")
TestFunction("copy | TUtil-Mapped | 5k.json", CopyMappedTUtil, "samples/5k.json")
TestFunction("copy | TUtil-Mapped | 10k.json", CopyMappedTUtil, "samples/10k.json")
TestFunction("copy | TUtil-Mapped | 50k.json", CopyMappedTUtil, "samples/50k.json")
TestFunction("copy | TUtil-Mapped | 100k.json", CopyMappedTUtil, "samples/100k.json")
TestFunction("copy | TUtil-Mapped | 500k.json", CopyMappedTUtil, "samples/500k.json")

#if ENABLE_LONG_BENCHMARKS
	TestFunction("copy | TUtil-Mapped | 1m.json", CopyMappedTUtil, "samples/1m.json")
	TestFunction("copy | TUtil-Mapped | 5m.txt", CopyMappedTUtil, "samples/5m.txt")
	TestFunction("copy | TUtil-Mapped | 10m.txt", CopyMappedTUtil, "samples/10m.txt")
	TestFunction("copy | TUtil-Mapped | 20m.txt", CopyMappedTUtil, "samples/20m.txt")
	TestFunction("copy | TUtil-Mapped | 40m.txt", CopyMappedTUtil, "samples/40m.txt")
	TestFunction("copy | TUtil-Mapped | 60m.txt", CopyMappedTUtil, "samples/60m.txt")
#endif

//========== JSON ==========

