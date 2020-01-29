var Benchmark = require('benchmark');
var fs = require('fs');
var color = require('color');

var suite = new Benchmark.Suite;

function ReadBench(name)
{
	var contents = fs.readFileSync(name, "utf8");
}

function CopyBench(name)
{
	var contents = fs.readFileSync(name, "utf8");
	fs.writeFileSync("temp.txt", contents);
}

suite.add('read 50k.json', function()
{
	ReadBench("../50k.json");
})
.add('read 500k.json', function()
{
	ReadBench("../500k.json");
})
.add('read 2m.json', function()
{
	ReadBench("../2m.json");
})
.add('read 20m.txt', function()
{
	ReadBench("../20m.txt");
})
.add('read 200m.txt', function()
{
	ReadBench("../200m.txt");
})
//========== COPY ==========
.add('copy 50k.json', function()
{
	CopyBench("../50k.json");
})
.add('copy 500k.json', function()
{
	CopyBench("../500k.json");
})
.add('copy 2m.json', function()
{
	CopyBench("../2m.json");
})
.add('copy 20m.txt', function()
{
	CopyBench("../20m.txt");
})
.add('copy 200m.txt', function()
{
	CopyBench("../200m.txt");
})
suite.on('cycle', function(event) {
	console.log(String(event.target));
})
.on('complete', function() {
	console.log();
	console.log();
	console.log("========== RESULTS ==========");
	for (var i = 0; i < this.length; i++) {
		console.log(this[i].toString() + " | " + new Number(this[i].stats.mean * 1000).toPrecision(4) + "ms");
	    //console.log(this[i].stats);
	}
})
// run async
.run({ 'async': true });

/*
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
	CopyBench("50k.json");
};

BENCHMARK("copy 500k.json")
{
	CopyBench("500k.json");
};

BENCHMARK("copy 2m.json")
{
	CopyBench("2m.json");
};

BENCHMARK("copy 20m.txt")
{
	CopyBench("20m.txt");
};

BENCHMARK("copy 200m.txt")
{
	CopyBench("200m.txt");
};

*/