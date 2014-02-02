var express = require('express');
var routes = require('./routes');
var http = require('http');
var crypto = require('crypto');

var app = express();
var server = app.listen(4000);

var io = require('socket.io').listen(server);

global.has_socket = false;
global.door_key = 'your_secret_key';

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.favicon());
  app.use(express.logger('dev'));
  app.use(express.static(__dirname + '/public'));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
});

app.configure('development', function(){
  app.use(express.errorHandler());
});

create_random_text = function(n, a) {
  var index = (Math.random() * (a.length - 1)).toFixed(0);
  return n > 0 ? a[index] + create_random_text(n - 1, a) : '';
};

//check is valid user, continue route if true
app.param('hash', function(req,res,next,id){
	console.log('validating user');
	var message = req.params.message;
	var hash = req.params.hash;
	var door_hash = crypto.createHash('sha256').update(message+global.door_key, 'utf8').digest('hex');
	if (door_hash == hash) {
		next();
	}else{
		res.send({status:false});
	};
});


app.get('/', routes.index);
app.get('/status/:message/:hash', routes.status);
app.get('/open/:message/:hash', routes.open);
app.get('/refresh/:message/:hash', routes.refresh);

console.log("Express server listening on port 4000");




io.sockets.on('connection', function (socket) {

	console.log('new io user');

	socket.on('complete_validation', function(data){

		var message = data.message;
		var hash = data.hash;

		var door_hash = crypto.createHash('sha256').update(message+global.door_key, 'utf8').digest('hex');

		//verified
		if (hash == door_hash) {
			console.log('verified door');
			global.has_socket = 'active';
			global.door = socket;


			socket.on('disconnect', function(data){
				global.has_socket = false;
			})

		}



	});



	var message = create_random_text(13, 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890');
	var hash = crypto.createHash('sha256').update(message+global.door_key).digest('hex');
	socket.emit('begin_validation', {message:message, hash:hash});

 	//io.sockets.emit('entrance', {message: 'A new chatter is online.'});

});

// io.sockets.on('share', function (socket) {  
//   io.sockets.emit('share', {message: 'hello'});
// });
