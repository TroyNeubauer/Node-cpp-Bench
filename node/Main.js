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

suite.add('read 5k.json', function()
{
	ReadBench("../5k.json");
})
.add('read 50k.json', function()
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
.add('read 60m.txt', function()
{
	ReadBench("../60m.txt");
})
.add('read 100m.txt', function()
{
	ReadBench("../100m.txt");
})
//========== COPY ==========
.add('copy 5k.json', function()
{
	CopyBench("../5k.json");
})
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
.add('copy 60m.txt', function()
{
	CopyBench("../60m.txt");
})
.add('copy 100m.txt', function()
{
	CopyBench("../100m.txt");
})
suite.on('cycle', function(event) {
	console.log(event.target.toString() + " | " + new Number(event.target.stats.mean * 1000).toPrecision(4) + "ms");

})

// run async
.run({ 'async': true });




