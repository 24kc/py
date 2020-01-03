#!/usr/bin/env python3

import os
from cryptography.fernet import Fernet

_cipher = None

def generate_key(key_file_name=''):
	key = Fernet.generate_key()
	if len(key_file_name) > 0:
		if not os.access(key_file_name, os.W_OK):
			raise Exception('cannot open file \"'+key_file_name+'\" to write')
		key_file = open(key_file_name, 'wb')
		key_file.write(key)
		key_file.close()
	return key

def load_key(key_file_name):
	if not os.access(key_file_name, os.R_OK):
		raise Exception('cannot open file \"'+key_file_name+'\" to read')
	key_file = open(key_file_name, 'rb')
	key = key_file.read()
	key_file.close()
	return key

def fernet(key):
	_cipher = Fernet(key)

def encrypt(b):
	if _cipher == None:
		raise Exception('no key is set')
	return _cipher.encrypt(b)

def decrypt(b):
	if _cipher == None:
		raise Exception('no key is set')
	return _cipher.decrypt(b)

