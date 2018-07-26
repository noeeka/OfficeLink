<?php
require 'flight/autoload.php';
require 'flight/Flight.php';

use Firebase\JWT\JWT;
use flight\Engine;

Flight::register('db', 'PDO', array('mysql:host=192.168.1.220;dbname=officelink;charset=utf8', 'systec', '123456'));

$app = new Engine();

$app->route('/api/phpinfo', function(){
	phpinfo();
});

$app->route('/api/login', function(){
	$config = array(
		"private_key_bits" => 512,
		"private_key_type" => OPENSSL_KEYTYPE_RSA,
	);
	$res = openssl_pkey_new($config);  
	openssl_pkey_export($res, $privKey);
	$pubKey = openssl_pkey_get_details($res);  
	$pubKey = $pubKey["key"];
	$key = "example_key";
	$token = array(
		"iss" => "http://example.org",
		"aud" => "http://example.com",
		"iat" => 1356999524,
		"nbf" => 1357000000
	);

	$jwt = JWT::encode($token, $privKey, 'RS256');

	$token = JWT::decode($jwt, $pubKey, array('RS256'));

	//$jwt = JWT::encode($token, $privKey);
	//$token = JWT::decode($jwt, $privKey, array('HS256'));

	Flight::json(array("jwt"=>$jwt, "token"=>$token, 'privKey'=>$privKey,'pubKey'=>$pubKey));
});

$app->route('/api', function(){
	echo 'Hello World!';
});

$app->route('/api/users', function(){
	$db = Flight::db();
	$sth = $db->prepare("SELECT name FROM users;");
	$sth->execute();
	$result = $sth->fetchAll();
	print_r($result);
});

$app->start();

?>

