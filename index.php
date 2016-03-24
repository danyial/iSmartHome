<?php
	if (!function_exists('curl_version')) {
		echo "Auf dem Webserver ist curl nicht aktiviert/installiert. Login nicht möglich!";
		return;
	}

	function guidv4($data) {
		assert(strlen($data) == 16);

		$data[6] = chr(ord($data[6]) & 0x0f | 0x40);
		$data[8] = chr(ord($data[8]) & 0x3f | 0x80);

		return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
	}

	// Test des Login-Scripts
	$test = $_GET["test"];
	
	if ($test !== null) {		
		$body = '<BaseRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="1.70" xsi:type="ProbeShcRequest" RequestId="'.guidv4(openssl_random_pseudo_bytes(16)).'" />';
		
		// Request zur Zentrale (nicht verändern)
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, 'https://' . $test . '/cmd');
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_POST, true);
		curl_setopt($ch, CURLOPT_HEADER, true);
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
		curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
		curl_setopt($ch, CURLOPT_SSLVERSION, 3);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
		curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
		list($header, $response) = explode("\r\n\r\n", curl_exec($ch), 2);
		
		$error = curl_error($ch);
		
		// Verbindung schliessen
		curl_close($ch);
		
		if ($error) {
			echo 'Curl-Fehler: ' . $error;
			return;
		}
		
		
		
		// Response der Zentrale zurückgeben
		echo '<pre>'.$response.'</pre>';
		//echo htmlentities($response, ENT_COMPAT, 'UTF-8');
	} else {
		// Übernehmen der Aktion (nicht verändern)
		$cmd = $_GET["cmd"];

		// Übernehmen der SHC IP
		$shcip = $_GET["shcip"];
		
		// ClientId
		$clientId = $_GET["clientid"];

		// Übernehmen des Bodys (nicht verändern)
		$body = @file_get_contents('php://input');

		// Request zur Zentrale (nicht verändern)
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, 'https://' . $shcip . '/' . $cmd);
		
		if($clientId !== null)
		{
			curl_setopt($ch, CURLOPT_HTTPHEADER, array('ClientId: ' . $clientId));
		}
		
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_POST, true);
		curl_setopt($ch, CURLOPT_HEADER, true);
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
		curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
		curl_setopt($ch, CURLOPT_SSLVERSION, 3);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $cmd === 'upd' ? 'upd' : $body);
		curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
		list($header, $response) = explode("\r\n\r\n", curl_exec($ch), 2);
		
		$error = curl_error($ch);
		
		// Verbindung schliessen
		curl_close($ch);
		
		if ($error) {
			echo 'Curl-Fehler: ' . $error;
			return;
		}
		// Response der Zentrale zurückgeben
		echo $response;
	}	
?>