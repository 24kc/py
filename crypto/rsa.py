#!/usr/bin/env python3

import sys, base64
from Crypto.PublicKey import RSA


__block_size_decrypt = None # sizeof key
__block_size_encrypt = None # __block_size_decrypt - 2 - sizeof Hash
__cipher = None
all_key_bits = (2048, 3072, 4096, 7680, 10240, 15360, 20480)


# 返回一个密钥对, 请忽略此返回值, 总是使用load_key('f')加载密钥
def generate_key(key_file_name='', key_bits=all_key_bits[0]):
	if key_bits not in all_key_bits:
		raise Exception('key_bits Error')
	rsa = RSA.generate(key_bits)
	if key_file_name:
		with open(key_file_name, 'wb') as f:
			f.write(rsa.exportKey('PEM'))
		with open(key_file_name+'.pub', 'wb') as f:
			f.write(rsa.publickey().exportKey('PEM'))
	return rsa


def load_key(key_file_name):
	with open(key_file_name, 'rb') as f:
		key = RSA.importKey(f.read())
	return key


def fernet(key):
	if True:
		from Crypto.Cipher import PKCS1_OAEP as PKCS1
	else:
		from Crypto.Cipher import PKCS1_v1_5 as PKCS1
	from Crypto.Hash import MD5

	global __cipher
	global __block_size_encrypt, __block_size_decrypt
	hashalgo = MD5
	__cipher = PKCS1.new(key, hashalgo)
	key_bytes = (key.size() + 1) // 8
	__block_size_encrypt = key_bytes - 2 - hashalgo.digest_size * 2
	__block_size_decrypt = key_bytes


def encrypt(b):
	block_size = __block_size_encrypt
	b_len = len(b)
	n = int( b_len / block_size )
	r = b_len % block_size
	ba = bytearray()
	for i in range(0, n*block_size, block_size):
		tb = __cipher.encrypt( b[i:i+block_size] )
		ba.extend(tb)
	if r:
		tb = __cipher.encrypt( b[-r:] )
		ba.extend(tb)
	return bytes(ba)


def decrypt(b):
	block_size = __block_size_decrypt
	b_len = len(b)
	n = int( b_len / block_size )
	r = b_len % block_size
	ba = bytearray()
	for i in range(0, n*block_size, block_size):
		tb = __cipher.decrypt( b[i:i+block_size] )
		ba.extend(tb)
	if r:
		tb = __cipher.decrypt( b[-r:] )
		ba.extend(tb)
	return bytes(ba)


#####################   rsa():    #######################


# return key == public_key ? True : False
def is_public(key):
	return True if not is_private(key) else False


# return key == private_key ? True : False
def is_private(key):
	return True if key.has_private() else False


#####################   main():   #######################


_ENCRYPT = 0
_DECRYPT = 1

_e = _ENCRYPT
_d = _DECRYPT
_in = 0x2411
_out = 0x2412
_stdio = 0x2421
_key = 0x2431
_keygen = 0x2441
_key_bits = 0x2442
_help = 0x2451

options = {
	'-e': _e,
	'-d': _d,
	'-in': _in,
	'-out': _out,
	'-stdio': _stdio,
	'-k': _key,
	'-key': _key,
	'-keygen': _keygen,
	'-kb': _key_bits,
	'-key-bits': _key_bits,
	'-h': _help,
	'-help': _help
}


def main(argv):
	argc = len(argv); optind = 0
	mode = _ENCRYPT
	keygen = None
	is_stdio = False
	in_file = None; out_file = None; key_file = None
	key_bits = all_key_bits[0]
	is_tty = sys.stdout.isatty()

	while optind+1 < argc:
		optind += 1
		argstr = argv[optind]
		arg = options.get(argstr)

		if arg == None:
			print('unrecognized command line option \''+argstr+'\'')
			sys.exit(1)

		if arg in (_e, _d):
			mode = arg
		elif arg == _in:
			optind += 1
			if optind < argc:
				in_file = argv[optind]
			else:
				arg = -1
		elif arg == _out:
			optind += 1
			if optind < argc:
				out_file = argv[optind]
			else:
				arg = -1
		elif arg == _key:
			optind += 1
			if optind < argc:
				key_file = argv[optind]
			else:
				arg = -1
		elif arg == _keygen:
			optind += 1
			if optind < argc:
				keygen = argv[optind]
			else:
				arg = -1
		elif arg == _key_bits:
			optind += 1
			if optind < argc:
				key_bits_error = None
				try:
					key_bits = int(argv[optind])
					if key_bits not in all_key_bits:
						key_bits_error = True
				except ValueError:
					key_bits_error = True
				if key_bits_error:
					print('key-bits must in', all_key_bits)
					sys.exit(1)
			else:
				arg = -1
		elif arg == _stdio:
			is_stdio = True
		elif arg == _help:
			help(argv)
			sys.exit()
		else:
			print('getopt error')
			sys.exit()

		if arg < 0:
			print('missing argument after \''+argstr+'\'')
			sys.exit()

	if keygen:
		generate_key(keygen, key_bits)
		sys.exit()

	if not key_file:
		print('Missing key file.\nSpecifying key file with -k/-key')
		sys.exit(1)

	if not in_file and not out_file:
		is_stdio = True

	if is_stdio:
		s = input('Please enter the text: ' if is_tty else '')
		ibs = s.encode()
		if mode == _DECRYPT:
			ibs = base64.b64decode(ibs)
	else:
		if not in_file:
			print('Missing input file')
			sys.exit(1)
		if not out_file:
			print('Missing output file')
			sys.exit(1)
		with open(in_file, 'rb') as in_file:
			ibs = in_file.read()
	if not len(ibs):
		print('No input data')
		sys.exit()

	key = load_key(key_file)
	fernet(key)

	if mode == _ENCRYPT:
		obs = encrypt(ibs)
	else:
		obs = decrypt(ibs)

	if is_stdio:
		if is_tty:
			print('Output:')
		if mode == _ENCRYPT:
			obs = base64.b64encode(obs)
		print(obs.decode())
	else:
		with open(out_file, 'wb') as out_file:
			out_file.write(obs)

	if is_tty:
		if is_stdio:
			print()
		print(("Encrypt" if mode == _ENCRYPT else "Decrypt"), "OK")


def help(argv):
	print('Usage:    python3', argv[0], '[options] [-in IN_FILE -out OUT_FILE]')
	print('Valid options are:')
	print(' -e                Encrypt')
	print(' -d                Decrypt')
	print(' -in in_file       Input file')
	print(' -out out_file     Output file')
	print(' -stdio            Standard input and output')
	print(' -k/-key key_file  Specifying the key file')
	print(' -keygen           Generate key')
	print(' -kb/-key-bits %d  Specify key length while Generate key, default =', all_key_bits[0])
	print(' -h/-help          Display this message')


if __name__ == '__main__':
	main(sys.argv)

