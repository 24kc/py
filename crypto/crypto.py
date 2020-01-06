#!/usr/bin/env python3

import sys, hashlib, base64, random
from Crypto.Cipher import AES

__key = None
__cipher = None
__cipher_status = False


def generate_key(password='', key_file_name=''):
	ha = hashlib.md5()
	if not password:
		i = random.randint(0xffffffffffffffff, 0xffffffffffffffffffffffffffffffff)
		password = f'{i}'
	ha.update(f'{password} akm 24k '.encode())
	key = ha.digest()
	if key_file_name:
		with open(key_file_name, 'wb') as key_file:
			key_file.write(base64.b64encode(key))
	return key


def load_key(key_file_name):
	key = None
	with open(key_file_name, 'rb') as key_file:
		s = key_file.read()
		key = base64.b64decode(s)
	return key


def fernet(key):
	global __key, __cipher, __cipher_status
	if (__key != key) or not __cipher_status:
		__cipher = AES.new(key, AES.MODE_CBC, b' iv - akm24k-abc')
		__cipher_status = True
		__key = key


def encrypt(b):
	global __cipher_status
	if __cipher == None:
		raise Exception('no key is set')
	n = 16 - len(b) % 16
	b = b + bytes([n]) * n
	fernet(__key)
	b = __cipher.encrypt(b)
	__cipher_status = False
	return b


def decrypt(b):
	global __cipher_status
	if __cipher == None:
		raise Exception('no key is set')
	fernet(__key)
	b = __cipher.decrypt(b)
	__cipher_status = False
	n = b[-1]
	if not (0 < n and n <= 16):
		raise Exception(f'Padding error {n}')
	b = b[:-n]
	return b


#####################   main():   #######################


_ENCRYPT = 0
_DECRYPT = 1

_e = _ENCRYPT
_d = _DECRYPT
_in = 0x2411
_out = 0x2412
_stdio = 0x2421
_key = 0x2431
_password = 0x2432
_keygen = 0x2441
_help = 0x2451

options = {
	'-e': _e,
	'-d': _d,
	'-in': _in,
	'-out': _out,
	'-stdio': _stdio,
	'-k': _key,
	'-key': _key,
	'-p': _password,
	'-password': _password,
	'-keygen': _keygen,
	'-h': _help,
	'-help': _help
}


def main(argv):
	argc = len(argv); optind = 0
	mode = _ENCRYPT
	keygen = None
	is_stdio = False
	in_file = None; out_file = None; key_file = None
	password = None

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
		elif arg == _password:
			optind += 1
			if optind < argc:
				password = argv[optind]
			else:
				arg = -1
		elif arg == _keygen:
			optind += 1
			if optind < argc:
				keygen = argv[optind]
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
		generate_key(password or '', keygen)
		sys.exit()

	if not in_file and not out_file:
		is_stdio = True

	if is_stdio:
		s = input('Please enter the text: ')
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

	if key_file:
		kbs = load_key(key_file)
	else:
		if not password:
			password = input('Please enter the password: ')
		if not len(password):
			password = '\n'
		kbs = generate_key(password)

	fernet(kbs)

	if mode == _ENCRYPT:
		obs = encrypt(ibs)
	else:
		obs = decrypt(ibs)

	if is_stdio:
		print('Output:')
		if mode == _ENCRYPT:
			obs = base64.b64encode(obs)
		print(obs.decode())
	else:
		with open(out_file, 'wb') as out_file:
			out_file.write(obs)

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
	print(' -p/-password ***  Specifying the password')
	print(' -keygen           Generate key')
	print(' -h/-help          Display this message')


if __name__ == '__main__':
	main(sys.argv)

