import Crypto
from Crypto.Cipher import AES
from Crypto.Cipher import ARC4
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random
from hashlib import sha1
import hmac
import binascii
import base64
import os
import struct
import xml.etree.cElementTree as ET
from os import listdir
from os.path import isfile, join

LEN_SIZE = 8
AUTH_SIZE = 20

TEST_ENC_KEY = "0123456789ABCDEF"
TEST_AUTH_KEY = "ABCDEF0123456789"

PRIVATE_KEY_FILE = "private.pem"

RSA_MODULUS = 0x2b79f6e668ccedee8054b2f07c125daab0e071a0f4482a31aa8dac377c9194220b3352c6ceb67e09c0b1d23c10e6a2388aae9a769147865f2a8eccb625875c3be84a25c7b320526c5d3275c773d9d63dd8f43870fda5ed46f9210817096d29ace5d9efef3046cda5c99cc44c455f69cc998e1caf7459dad281e080fb5acd6d459
RSA_PUBLIC_EXPONENT = 0x10001
RSA_PRIVATE_EXPONENT = 0x72f916f63c2fb5080457f8ddff3e9275d34bb932eccfeac56d433b2b81417b7c8c222dc592e3086cc2297ecf59e2911cf5a2c8d8c55961004a8b58d2586c9e7d411ed3d6a9325d3d7dfef33f09700e74fa7505119a50f1ffe49409365a85601699f137f0c7bafc8b57a6dcfcde222c506de4214609ecebc6c5b6dffee6194f41

pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
unpad = lambda s : s[0:-ord(s[-1])]


def pkcs1_sign(data):
	key = RSA.importKey(open(PRIVATE_KEY_FILE).read())
	h = SHA.new(data)
	p = PKCS1_v1_5.new(key)
	return p.sign(h)

def rc4crypt(data, key):
    x = 0
    box = range(256)
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = 0
    y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))
    
    return ''.join(out)

def GetType(object_file):
	i = object_file.rfind(".")
	if (i < 0):
		raise EncapsulationError("unknown type")
	raw_type = object_file[object_file.rfind(".") + 1:]

	if (raw_type == "png"):
		return "data:image/png;base64"
	if (raw_type == "jpg"):
		return "data:image/jpg;base64"
	if (raw_type == "js"):
		return "text/javascript"
	if ((raw_type == "html") or (raw_type == "htm")):
		return "text/html"
	raise EncapsulationError("unknown type: " + raw_type)

def IsText(obj_type):
	return obj_type == "text/html"

def GetID(obj_file_name):
	return obj_file_name + ".enc"
	return sha1(obj_file_name).digest().encode("base64")
#	desc = str(len(data)) + data + str(len(my_type)) + my_type
#	return sha1(desc).digest().encode("base64")

def IsPublic(object_file):
	return object_file.startswith("public_")

def CreateObjectXML(object_file):
	my_type = GetType(object_file)

	root = ET.Element("object")
	f = file(object_file, "rb")
	data = f.read()
	f.close()
	if (not IsText(my_type)):
		data = data.encode("base64")
	plain_text = ET.SubElement(root, "plain_text_obj")
	plain_text.set("name", "plain_text_obj")
	plain_text.text = data

	obj_type = ET.SubElement(root, "obj_type")
	obj_type.set("name", "obj_type")
	obj_type.text = my_type

	obj_type = ET.SubElement(root, "id")
	obj_type.set("name", "id")
	obj_type.text = GetID(object_file)

	ET.dump(root)
	return ET.tostring(root)

def HashToString(h):
	s = bytearray(h)
	out = 0
	for x in s:
		out <<= 8
		out += int(x)
	return hex(out).replace("L","")

def EncodePublic(sig, obj):
	root = ET.Element("object")

	obj_type = ET.SubElement(root, "public")
	obj_type.set("name", "public")
	obj_type.text = "1"

	sigfield = ET.SubElement(root, "sig")
	sigfield.set("name", "sig")
	sigfield.text = sig

	sigfield = ET.SubElement(root, "hashed_data")
	sigfield.set("name", "hashed_data")
	sigfield.text = HashToString(sha1(obj).digest())


	txtfield = ET.SubElement(root, "plain_text")
	txtfield.set("name", "plain_text")
	txtfield.text = obj
	ET.dump(root)
	return ET.tostring(root)


def Encode(mac, enc):
	
	root = ET.Element("object")

	obj_type = ET.SubElement(root, "public")
	obj_type.set("name", "public")
	obj_type.text = "0"

	macfield = ET.SubElement(root, "mac")
	macfield.set("name", "mac")
	macfield.text = mac

	encfield = ET.SubElement(root, "cipher_text")
	encfield.set("name", "cipher_text")
	encfield.text = enc
	ET.dump(root)
	return ET.tostring(root)

def Decode(data):
	root = ET.fromstring(data)
	mac = root[0].text
	print "MAC:", mac
	enc = root[1].text
	print "ENC:", enc
	return mac, enc

def DecodeInnerObject(data):
	root = ET.fromstring(data)
	plain_text_obj = root[0].text
	print "plain_text_obj:", plain_text_obj
	obj_type = root[1].text
	print "obj_type:", obj_type
	obj_id = root[2].text
	print "obj_id:", obj_id

	return plain_text_obj, obj_type, obj_id

class DecapsulationError (BaseException):
	def __init__ (self, description):
		self.description = description
	def print_err():
		print self.description
	description = ""

class EncapsulationError (BaseException):
	def __init__ (self, description):
		self.description = description
	def print_err():
		print self.description
	description = ""

class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) ) 

    def decrypt( self, enc ):
		enc = base64.b64decode(enc)
		iv = enc[:16]
		print "IV:", iv.encode("base64")
		cipher = AES.new(self.key, AES.MODE_CBC, iv )
		return unpad(cipher.decrypt( enc[16:] ))

class RC4Cipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
		nonce = Random.new().read(16)
		print "raw nonce:", nonce.encode("base64")
		print "enc key:", self.key
		tmpkey = nonce + self.key #hashf.digest()
		print "temp key: ", tmpkey.encode("base64")
		cipher = ARC4.new(tmpkey)
		return base64.b64encode(nonce + rc4crypt(raw, tmpkey) )

    def decrypt( self, enc ):
		enc = base64.b64decode(enc)
		nonce = enc[:16]
		tmpkey = nonce + self.key
		print "nonce:", nonce.encode("base64")
		print "tmp key:", tmpkey.encode("base64")
		cipher = ARC4.new(tmpkey)
		return cipher.decrypt(enc[16:])

def save(encapsulated, obj_file, out_dir):
	object_type = GetType(obj_file)
	out_file = out_dir + "/"
	if (IsText(object_type)):
		out_file += GetID(obj_file)
	else:
		out_file += GetID(obj_file)

	print "OUTPUT FILE: ", out_file

	enc_f = file(out_file, "wb")
	enc_f.write(encapsulated)
	enc_f.close()
	return encapsulated
	

def EncapsulatePublicObject(obj_file, out_dir):
	obj = CreateObjectXML(obj_file)
	sig = str(RSA_sign(obj))
	encpasulated = EncodePublic(sig, obj)
	return save(encpasulated, obj_file, out_dir)


def EncapsulateObject(obj_file, user_enc_key, user_auth_key, out_dir):
	cipher = RC4Cipher(user_enc_key) #AESCipher(user_enc_key)
	obj = CreateObjectXML(obj_file)
	encrypted = cipher.encrypt(obj)
	mac = base64.b64encode(hmac.new(user_auth_key, encrypted, sha1).digest())

	encpasulated = Encode(mac, encrypted)
	return save(encpasulated, obj_file, out_dir)

def DecapsulateObject(enc_obj, user_enc_key, user_auth_key):
	auth, enc_data = Decode(enc_obj)
	mac = base64.b64encode(hmac.new(user_auth_key, enc_data, sha1).digest())
	if (mac != auth):
		raise DecapsulationError("invalid mac")
	
	cipher = RC4Cipher(user_enc_key)
	data = cipher.decrypt(enc_data)
	obj, obj_type, obj_id = DecodeInnerObject(data)
	return obj, obj_type, obj_id

def GetFiles(mypath):
	return [f for f in os.listdir(mypath) if os.path.isfile(f)]

def EncapsulateDirectory(directory):
	print "Encapsulating Directory", directory
	os.chdir(directory)
	try:
		os.mkdir("../enc")
	except:
		pass
	file_list = GetFiles(directory)
	for f in file_list:
		if ((f.endswith("~")) or (f.startswith("."))):
			continue
		print "Handling:", f
		try:
			if (IsPublic(f)):
				print "public object"
				EncapsulatePublicObject(f, "../enc")
			else:
				print "private object"
				EncapsulateObject(f, TEST_ENC_KEY, TEST_AUTH_KEY, "../enc")
		except:
			raise
			print "skipped", f

def test():
	try:
		os.mkdir("../test")	
	except:
		pass
	data = EncapsulateObject("test.html", TEST_ENC_KEY, TEST_AUTH_KEY, "../test")
	print data[:AUTH_SIZE].encode("hex")
	obj, obj_type, obj_id = DecapsulateObject(data, TEST_ENC_KEY, TEST_AUTH_KEY)
	print obj
	print obj_type
	print obj_id

def RSA_encrypt(data):
	return pow(data, RSA_PUBLIC_EXPONENT, RSA_MODULUS)

def RSA_decrypt(data):
	return pow(data, RSA_PRIVATE_EXPONENT, RSA_MODULUS)

def RSA_sign(data):
	hashed = sha1(data).digest()
	return pow(int(hashed.encode("hex"),16), RSA_PRIVATE_EXPONENT, RSA_MODULUS)

def RSA_verify(data, sig):
	hashed = sha1(data).digest()
	return (int(hashed.encode("hex"),16) == pow(sig, RSA_PUBLIC_EXPONENT, RSA_MODULUS))

def test_rsa():
	return (7 == RSA_decrypt(RSA_encrypt(7)))

if __name__ == "__main__":
	if (len(sys.argv) < 2):
		print "usage:", sys.argv[0], "plain-text-objects-dir"
		return
	EncapsulateDirectory(sys.argv[1])
