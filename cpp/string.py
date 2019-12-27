#!/usr/bin/env python3

class string:
	__data = []

	def __init__(self, s=''):
		self.assign(s);

	def __repr__(self):
		return "".join(self.__data)

	def assign(self, s):
		self.__data = list(s);

	def __getitem__(self, index):
		return self.__data[index]

	def __iter__(self):
		self.index = 0
		return self

	def __next__(self):
		if self.index >= self.size():
			raise StopIteration
		x = self[self.index]
		self.index += 1
		return x

	def size(self):
		return len(self.__data)

	def data(self):
		return self.__data

#
# main()

s = string("ABC傻逼")

for c in s:
	print(c, end=' ')
print()


