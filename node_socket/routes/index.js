var crypto = require('crypto');

create_random_text = function(n, a) {
  var index = (Math.random() * (a.length - 1)).toFixed(0);
  return n > 0 ? a[index] + create_random_text(n - 1, a) : '';
};
/*
 * GET home page.
 */

exports.index = function(req, res){
  res.render('index', { title: 'Express' });
};

exports.status = function(req, res){

	res.send({status:global.has_socket});
	console.log('has socket : ' + global.has_socket)
};

exports.refresh = function(req, res){

	if (global.has_socket != false) {
			console.log('opening door');
			var message = create_random_text(13, 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890');
			var hash = crypto.createHash('sha256').update(message+global.door_key).digest('hex');
			global.door.emit('refresh_users_request', {message:message, hash:hash});
	  		res.send({status:true});

	}else{
		res.send({status:false});
	};




};

exports.open = function(req, res){



	if (global.has_socket != false) {

			console.log('opening door');
			var message = create_random_text(13, 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890');		var hash = crypto.createHash('sha256').update(message+global.door_key).digest('hex');
			global.door.emit('open_door_request', {message:message, hash:hash});
	  		res.send({status:true});

	}else{
			res.send({status:false});
	};



	
};