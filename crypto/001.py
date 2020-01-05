#!/usr/bin/env python3

import crypto

s = 'ABC傻逼'

key = crypto.generate_key(s) # s是密码
print('key =', key)

crypto.fernet(key) # 设置密钥
s = crypto.encrypt(s.encode()) #加密
print('密文:', s)

crypto.fernet(key) # 设置密钥
s = crypto.decrypt(s).decode() #解密
print('明文:', s)

# key = crypto.generate_key(password, file_name)
	# 根据password生成key
	# 设置file_name可以保存key(base64) 以供load_key加载
# key = crypto.load_key(file_name)
	# 从文件加载key
