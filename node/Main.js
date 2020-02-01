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

suite.add('read | 100b.json', function()
{
	ReadBench("samples/100b.json");
})
.add('read | 1k.json', function()
{
	ReadBench("samples/1k.json");
})
.add('read | 5k.json', function()
{
	ReadBench("samples/5k.json");
})
.add('read | 10k.json', function()
{
	ReadBench("samples/10k.json");
})
.add('read | 50k.json', function()
{
	ReadBench("samples/50k.json");
})
.add('read | 100k.json', function()
{
	ReadBench("samples/100k.json");
})
.add('read | 500k.json', function()
{
	ReadBench("samples/500k.json");
})
.add('read | 1m.json', function()
{
	ReadBench("samples/1m.json");
})
.add('read | 5m.txt', function()
{
	ReadBench("samples/5m.txt");
})
.add('read | 10m.txt', function()
{
	ReadBench("samples/10m.txt");
})
.add('read | 20m.txt', function()
{
	ReadBench("samples/20m.txt");
})
.add('read | 40m.txt', function()
{
	ReadBench("samples/40m.txt");
})
.add('read | 60m.txt', function()
{
	ReadBench("samples/60m.txt");
});


//========== COPY ==========

suite.add('copy | 100b.json', function()
{
	CopyBench("samples/100b.json");
})
.add('copy | 1k.json', function()
{
	CopyBench("samples/1k.json");
})
.add('copy | 5k.json', function()
{
	CopyBench("samples/5k.json");
})
.add('copy | 10k.json', function()
{
	CopyBench("samples/10k.json");
})
.add('copy | 50k.json', function()
{
	CopyBench("samples/50k.json");
})
.add('copy | 100k.json', function()
{
	CopyBench("samples/100k.json");
})
.add('copy | 500k.json', function()
{
	CopyBench("samples/500k.json");
})
.add('copy | 1m.json', function()
{
	CopyBench("samples/1m.json");
})
.add('copy | 5m.txt', function()
{
	CopyBench("samples/5m.txt");
})
.add('copy | 10m.txt', function()
{
	CopyBench("samples/10m.txt");
})
.add('copy | 20m.txt', function()
{
	CopyBench("samples/20m.txt");
})
.add('copy | 40m.txt', function()
{
	CopyBench("samples/40m.txt");
})
.add('copy | 60m.txt', function()
{
	CopyBench("samples/60m.txt");
});

suite.on('cycle', function(event) {
	line = event.target.toString();
	name = line.split(" x ")[0];
	console.log(name + "=" + new Number(event.target.stats.mean * 1000000000));

})

// run async
.run({ 'async': true });


