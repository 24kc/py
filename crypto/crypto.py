#!/usr/bin/env python3

import sys, base64
from Crypto.Cipher import AES

__key = None
__cipher = None
__cipher_status = False
all_key_bits = (128, 192, 256)

# password: 密码
# key_file_name: 密钥文件保存路径
# key_bits: must in all_key_bits
# return: 始终返回一个密钥
# generate_key() 返回随机密钥
# generate_key('ABCsb') 用密码'ABCsb'生成密钥
# generate_key(None, 'sbc.key') 生成随机密钥, 并保存密钥为sbc.key
# generate_key('ABCsb', 'sbc.key') 用密码'ABCsb'生成密钥, 并保存密钥为sbc.key

def generate_key(password='', key_file_name='', key_bits=all_key_bits[0]):
	if key_bits not in all_key_bits:
		raise Exception('key_bits Error')
	key_bytes = key_bits // 8

	from Crypto.Hash import SHA512
	ha = SHA512.new()

	if not password:
		from Crypto.Random import random
		rand_list = []
		for _ in range(24):
			i = random.randint(0xffff, 0xffffffff)
			rand_list.append(i)
		password = str(rand_list)

	ha.update(f'{password} akm 24k ABC'.encode())
	key = ha.digest()[:key_bytes]

	if key_file_name:
		with open(key_file_name, 'wb') as key_file:
			key_file.write(base64.b64encode(key))
	return key


# key_file_name: 密钥文件保存路径
# load_key('sbc.key') 从文件sbc.key加载密钥, 返回该密钥
def load_key(key_file_name):
	key = None
	with open(key_file_name, 'rb') as key_file:
		s = key_file.read()
		key = base64.b64decode(s)
	return key


# 设置要使用的密钥key, 在下一次调用此函数前,加密解密都使用该密钥
def fernet(key):
	global __key, __cipher, __cipher_status
	if (__key != key) or not __cipher_status:
		__cipher = AES.new(key, AES.MODE_CBC, b'IV - akm 24k ABC')
		__cipher_status = True
		__key = key


# 加密bytes 返回bytes
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


# 解密bytes 返回bytes
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
_key_bits = 0x2442
_help = 0x2451
_check = 0x2461

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
	'-kb': _key_bits,
	'-key-bits': _key_bits,
	'-c': _check,
	'-check': _check,
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
		elif arg == _check:
			optind += 1
			if optind < argc:
				key_file = argv[optind]
				try:
					key = load_key(key_file)
					fernet(key)
					print('key bits =', len(key)*8)
				except:
					print('key format error')
					sys.exit(1)
				sys.exit()
			else:
				arg = -1
		elif arg == _help:
			help(argv)
			sys.exit()
		else:
			print('getopt error')
			sys.exit(1)

		if arg < 0:
			print('missing argument after \''+argstr+'\'')
			sys.exit(1)

	if keygen:
		generate_key(password or '', keygen, key_bits)
		sys.exit()

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
		sys.exit(1)

	if key_file:
		kbs = load_key(key_file)
	else:
		if not password:
			password = input('Please enter the password: ' if is_tty else '')
		if not len(password):
			password = '\n'
		kbs = generate_key(password, '', key_bits)

	fernet(kbs)

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
	print(' -k/-key key       Specifying the key file')
	print(' -p/-password ***  Specifying the password')
	print(' -keygen           Generate key')
	print(' -kb/-key-bits %d  Specify key length while Generate key, default =', all_key_bits[0])
	print(' -c/-check key     check key format')
	print(' -h/-help          Display this message')


if __name__ == '__main__':
	main(sys.argv)

