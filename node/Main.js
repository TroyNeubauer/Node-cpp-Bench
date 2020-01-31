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

suite.add('read | 5k.json', function()
{
	ReadBench("samples/5k.json");
})
.add('read | 50k.json', function()
{
	ReadBench("samples/50k.json");
})
.add('read | 500k.json', function()
{
	ReadBench("samples/500k.json");
})
.add('read | 2m.json', function()
{
	ReadBench("samples/2m.json");
})
.add('read | 20m.txt', function()
{
	ReadBench("samples/20m.txt");
})
.add('read | 60m.txt', function()
{
	ReadBench("samples/60m.txt");
})
//========== COPY ==========
.add('copy | 5k.json', function()
{
	CopyBench("samples/5k.json");
})
.add('copy | 50k.json', function()
{
	CopyBench("samples/50k.json");
})
.add('copy | 500k.json', function()
{
	CopyBench("samples/500k.json");
})
.add('copy | 2m.json', function()
{
	CopyBench("samples/2m.json");
})
.add('copy | 20m.txt', function()
{
	CopyBench("samples/20m.txt");
})
.add('copy | 60m.txt', function()
{
	CopyBench("samples/60m.txt");
})
suite.on('cycle', function(event) {
	line = event.target.toString();
	name = line.split(" x ")[0];
	console.log(name + "=" + new Number(event.target.stats.mean * 1000000000));

})

// run async
.run({ 'async': true });




