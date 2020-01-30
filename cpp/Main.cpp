
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

void CopyFileWithTimes(const char* fileName, int times)
{
	logger->info("Copying file {} {} times", fileName, times);

	std::uint64_t size;
	TUtil::FileError error;
	const char* baseFileName = "samples/2m.json";
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

	if (TUtil::FileSystem::Exists("samples/20m.txt"))
		logger->info("Using cached 20mb and 60mb files");
	else
	{
		logger->info("Creating files:");
		CopyFileWithTimes("samples/20m.txt", 10);
		CopyFileWithTimes("samples/60m.txt", 30);
	}

	int result = Catch::Session().run(argc, argv);

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

const char* ReadBufferedC(const char* fileName)
{
	std::uint64_t size = TUtil::FileSystem::FileSize(fileName);

	char* buf = new char[1024 * 1024];
	std::size_t bytesRead;
	FILE* file = fopen(fileName, "rb");
	if (!file) { logger->error("Cannot open file {}", fileName); return nullptr; }

	do
	{
		bytesRead = fread(buf, 1, 1024 * 1024, file);

	} while(bytesRead);

	fclose(file);
	delete[] buf;
	return nullptr;
}


const char* CopyBufferedC(const char* fileName)
{
	std::size_t bytesRead;
	FILE* in = fopen(fileName, "rb");
	if (!in) { logger->error("Cannot open file {}", fileName); return nullptr; }

	FILE* out = fopen("temp.txt", "wb");
	if (!out) { logger->error("Cannot open file {}", "temp.txt"); return nullptr; }

	do
	{
		bytesRead = fread(buf, 1, BUF_SIZE, in);
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
	char* buf = new char[size];

	FILE* file = fopen(fileName, "rb");
	if (!file) { logger->error("Cannot open file {}", fileName); return nullptr; }

	fread(buf, 1, size, file);
	fclose(file);

	delete[] buf;
	return nullptr;
}

const char* CopyAllC(const char* fileName)
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

TestFunction("read | C-buffered | 5k.json", ReadBufferedC, "samples/5k.json")
TestFunction("read | C-buffered | 50k.json", ReadBufferedC, "samples/50k.json")
TestFunction("read | C-buffered | 500k.json", ReadBufferedC, "samples/500k.json")
TestFunction("read | C-buffered | 2m.json", ReadBufferedC, "samples/2m.json")
TestFunction("read | C-buffered | 20m.txt", ReadBufferedC, "samples/20m.txt")
TestFunction("read | C-buffered | 60m.txt", ReadBufferedC, "samples/60m.txt")

TestFunction("read | C-All | 5k.json", ReadAllC, "samples/5k.json")
TestFunction("read | C-All | 50k.json", ReadAllC, "samples/50k.json")
TestFunction("read | C-All | 500k.json", ReadAllC, "samples/500k.json")
TestFunction("read | C-All | 2m.json", ReadAllC, "samples/2m.json")
TestFunction("read | C-All | 20m.txt", ReadAllC, "samples/20m.txt")
TestFunction("read | C-All | 60m.txt", ReadAllC, "samples/60m.txt")

TestFunction("read | TUtil-Mapped | 5k.json", ReadMappedTUtil, "samples/5k.json")
TestFunction("read | TUtil-Mapped | 50k.json", ReadMappedTUtil, "samples/50k.json")
TestFunction("read | TUtil-Mapped | 500k.json", ReadMappedTUtil, "samples/500k.json")
TestFunction("read | TUtil-Mapped | 2m.json", ReadMappedTUtil, "samples/2m.json")
TestFunction("read | TUtil-Mapped | 20m.txt", ReadMappedTUtil, "samples/20m.txt")
TestFunction("read | TUtil-Mapped | 60m.txt", ReadMappedTUtil, "samples/60m.txt")

//========== COPY ==========

TestFunction("copy | C-buffered | 5k.json", CopyBufferedC, "samples/5k.json")
TestFunction("copy | C-buffered | 50k.json", CopyBufferedC, "samples/50k.json")
TestFunction("copy | C-buffered | 500k.json", CopyBufferedC, "samples/500k.json")
TestFunction("copy | C-buffered | 2m.json", CopyBufferedC, "samples/2m.json")
TestFunction("copy | C-buffered | 20m.txt", CopyBufferedC, "samples/20m.txt")
TestFunction("copy | C-buffered | 60m.txt", CopyBufferedC, "samples/60m.txt")

TestFunction("copy | C-All | 5k.json", CopyAllC, "samples/5k.json")
TestFunction("copy | C-All | 50k.json", CopyAllC, "samples/50k.json")
TestFunction("copy | C-All | 500k.json", CopyAllC, "samples/500k.json")
TestFunction("copy | C-All | 2m.json", CopyAllC, "samples/2m.json")
TestFunction("copy | C-All | 20m.txt", CopyAllC, "samples/20m.txt")
TestFunction("copy | C-All | 60m.txt", CopyAllC, "samples/60m.txt")

TestFunction("copy | TUtil-Mapped | 5k.json", CopyMappedTUtil, "samples/5k.json")
TestFunction("copy | TUtil-Mapped | 50k.json", CopyMappedTUtil, "samples/50k.json")
TestFunction("copy | TUtil-Mapped | 500k.json", CopyMappedTUtil, "samples/500k.json")
TestFunction("copy | TUtil-Mapped | 2m.json", CopyMappedTUtil, "samples/2m.json")
TestFunction("copy | TUtil-Mapped | 20m.txt", CopyMappedTUtil, "samples/20m.txt")
TestFunction("copy | TUtil-Mapped | 60m.txt", CopyMappedTUtil, "samples/60m.txt")

//========== JSON ==========

