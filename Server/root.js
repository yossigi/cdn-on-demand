var kCDN = "52.3.156.141/files"

// private keys are set only after the user authenticates
var user_enc_key = ""
var user_auth_key = ""
var MAC_LEN = 20

// signature verification key
var server_rsa_modulus = BigInteger("0x2b79f6e668ccedee8054b2f07c125daab0e071a0f4482a31aa8dac377c9194220b3352c6ceb67e09c0b1d23c10e6a2388aae9a769147865f2a8eccb625875c3be84a25c7b320526c5d3275c773d9d63dd8f43870fda5ed46f9210817096d29ace5d9efef3046cda5c99cc44c455f69cc998e1caf7459dad281e080fb5acd6d459")
var server_rsa_pub_exponenet = BigInteger("0x10001")


var elements_rendered = 0;
var elements_in_page;

DocTypeEnum = {
    HTML : 0
}

function expmod(base, expon, mod) {
  if (expon.isZero()) return 1;
  if (expon.isEven()){
    return Math.pow( expmod( base, (expon / 2), mod), 2) % mod;
  }
  else {
    return (base * expmod( base, (expon - 1), mod)) % mod;
  }
}

// Convert hex string to ASCII.
// See http://stackoverflow.com/questions/11889329/word-array-to-string
function hex2a(hex) {
	var str = '';
	for (var i = 0; i < hex.length; i += 2)
	    str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
	return str;
}

function rc4(key, str) {
	var s = [], j = 0, x, res = '';
	for (var i = 0; i < 256; i++) {
		s[i] = i;
	}
	for (i = 0; i < 256; i++) {
		j = (j + s[i] + key.charCodeAt(i % key.length)) % 256;
		x = s[i];
		s[i] = s[j];
		s[j] = x;
	}
	i = 0;
	j = 0;
	for (var y = 0; y < str.length; y++) {
		i = (i + 1) % 256;
		j = (j + s[i]) % 256;
		x = s[i];
		s[i] = s[j];
		s[j] = x;
		res += String.fromCharCode(str.charCodeAt(y) ^ s[(s[i] + s[j]) % 256]);
	}
	return res;
}

function sym_decrypt(data, key) {
	var rawData = atob(data);
	var nonce = rawData.substring(0,16);
	var ciphertext = rawData.substring(16);
    var decrypted = rc4(nonce + key, ciphertext) //CryptoJS.RC4.decrypt(ciphertext, stringnonce + key).toString(CryptoJS.enc.Hex);
	return decrypted;
}

function Compare(s1, s2, n) {
	for (var i = 0; i < n; i++) {
		if (s1[i] != s2[i]) {
			return false;
		}
	}
	return true;
}

// Firefox splits large text regions into multiple Text objects (4096 chars in
// each). Glue it back together.
function getNodeText(node) {
    var r = "";
    for (var x = 0;x < node.childNodes.length; x++) {
        r = r + node.childNodes[x].nodeValue;
    }
    return r;
}

function GetElement(txt, name) {
	var xmlDoc;
	if (window.DOMParser) {
		parser=new DOMParser();
		xmlDoc=parser.parseFromString(txt,"text/xml");
	} else {  // Internet Explorer
		xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
		xmlDoc.async=false;
		xmlDoc.loadXML(txt);
	}
	
	var element = xmlDoc.getElementsByTagName(name);
	var firstdata = element[0].firstChild.data;
	return getNodeText(element[0])//element[0].firstChild.data;
}

function get_data(data) {
	return GetElement(data, "plain_text_obj")
}

function get_type(data) {
	return GetElement(data, "obj_type")
}

function get_id(data) {
	return GetElement(data, "id")
}

function stateChangeHandler(e){
    if(e.state){
        document.body.innerHTML = e.state.html;
        document.title = e.state.pageTitle;
		LoadSubObjects();
    }
};

function LoadSubObjects() {
	elements = document.getElementsByName("CDN");
	elements_in_page = elements.length;
	for (var i = 0; i < elements_in_page; i++) {
		requestObject(elements[i].id)
	}
	FinishLoad();
}

function render(raw_data, obj_type, obj_id, linked,file_name_to_save) {
	if (obj_type == "text/html") {
		if (linked) {
			window.onpopstate = stateChangeHandler;
			if (history.state == null) {
				history.pushState({"html":document.body.innerHTML,"pageTitle":document.title},"", location.href);
			}
		}
		document.body.innerHTML = raw_data;
		LoadSubObjects();
		if (linked) {
			history.pushState({"html":document.body.innerHTML,"pageTitle":document.title},"", linked);
		}
	}
	else if (obj_type == "text/plain"){
		saveTextAsFile(raw_data,file_name_to_save);
		
	}
	else {
		element = document.getElementById(obj_id);
		element.src = obj_type + "," + raw_data;
		element.name = obj_id;
		elements_rendered++;
	}
}

function asym_decapsulate(data, pub_key) {
	sig = GetElement(data, "sig");
	plain = GetElement(data, "plain_text");
}

function verify_signature(hashed_data, sig) {
	int_sig = BigInteger(sig);
	opened = int_sig.modPow(server_rsa_pub_exponenet, server_rsa_modulus)
	return (opened.compare(BigInteger(hashed_data)) == 0);
}

function compare_hash(data, hashed_data) {
	hash = Crypto.SHA1(data);
	//remove leading zero
	hash = hash.replace(/^0+/, "")
	return "0x" + hash == hashed_data;
}

function public_decapsulate(data, linked,file_name_to_save) {
	sig = GetElement(data, "sig");
	hashed_data = GetElement(data, "hashed_data");
	if (verify_signature(hashed_data, sig)) {
		plain_data = GetElement(data, "plain_text");
		if (compare_hash(plain_data, hashed_data)) {
			raw_data = get_data(plain_data);
			obj_type = get_type(plain_data);
			obj_id = "dummy_id"
			if (obj_type != "text/html") {
				obj_id = get_id(plain_data);
			}
			render(raw_data, obj_type, obj_id, linked,file_name_to_save);
			return true;
		}
	}
	return false;
}

function sym_decapsulate(data, enc_key, auth_key, linked) {
	
	mac = GetElement(data, "mac");
	enc_data = GetElement(data, "cipher_text");

	var hmac = Crypto.HMAC(Crypto.SHA1, enc_data, auth_key);
	var computed_mac = btoa(hex2a(hmac));	
	if (Compare(mac, computed_mac, MAC_LEN)) {
		data = sym_decrypt(enc_data, enc_key);
		raw_data = get_data(data);
		obj_type = get_type(data);
		obj_id = "dummy_id"
		if (obj_type != "text/html") {
			obj_id = get_id(data);
		}
		render(raw_data, obj_type, obj_id, linked);
		return true;
	}
	alert("mac error");
	return false;
}

function isPublic(data) {
	public_obj = GetElement(data, "public");
	return (public_obj == "1");
}

function requestObject(object_name, linked) {
	linked = typeof linked !== 'undefined' ? linked : false;
	//cut the .enc extension
	file_name_to_save = object_name.slice(0,-4);
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (isPublic(xhr.responseText)) {
				public_decapsulate(xhr.responseText, linked,file_name_to_save)
			} else {			
				sym_decapsulate(xhr.responseText, user_enc_key, user_auth_key, linked);
			}
		}
	}
	xhr.open("GET","//" + kCDN + "/" + object_name, true);
	xhr.send();
}

function requestIndexHTML() {
	return requestObject("index.html.enc")
}

function linkHandler(link, pathurl) {
	pathurl = typeof pathurl !== 'undefined' ? pathurl : link;
	return requestObject(link, pathurl)
}

function main() {
	requestIndexHTML();
}

function sleep(millis, callback) {
    setTimeout(function()
            { callback(arg); }
    , millis);
}

function FinishLoad() {	
	return;
	if (elements_rendered == elements_in_page) {
		return;
	}
	sleep(5, FinishLoad);
}

function saveTextAsFile(inputText,fileName)
{
	var plain = window.atob(inputText)
	var textFileAsBlob;

	var bytes = new Uint8Array(plain.length);
	for (var i=0; i<plain.length; i++) {
		bytes[i] = plain.charCodeAt(i)
	};
	textFileAsBlob = new Blob([bytes], {type:"application/octet-stream"});
	

	var downloadLink = document.createElement("a");
	downloadLink.download = fileName;
	downloadLink.innerHTML = "Download File";
	if (window.webkitURL != null)
	{
		// Chrome allows the link to be clicked
		// without actually adding it to the DOM.
		downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
	}
	else
	{
		// Firefox requires the link to be added to the DOM
		// before it can be clicked.
		downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
		downloadLink.onclick = destroyClickedElement;
		downloadLink.style.display = "none";
		document.body.appendChild(downloadLink);
	}

	downloadLink.click();
}

//main();
