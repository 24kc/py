#!/usr/bin/env python3

class string:
	__data = []

	def __init__(self, s=''):
		self.assign(s);

	def __str__(self):
		return "".join(self.__data)

	def assign(self, s):
		self.__data = list(s);

	def __getitem__(self, index):
		return self.__data[index]

	def data(self):
		return self.__data

	def __iter__(self):
		self.index = 0
		return self

	def __next__(self):
		if self.index >= self.size():
			raise StopIteration
		x = self[self.index]
		self.index += 1
		return x

	def empty(self):
		return self.size() > 0

	def size(self):
		return len(self.__data)

	def reverse(self):
		self.__data.reverse()

	def clear(self):
		self.__data.clear()

	def insert(self, index, c):
		self.__data.insert(index, c)

	def erase(self, index):
		del self.__data[index]

	def push_back(self, c):
		self.__data.append(c)

	def pop_back(self):
		self.__data.pop()

	def append(self, s):
		self.__data.extend(list(s))

	def substr(self, index, count):
		s = string()
		s.__data = self.__data[index:index+count]
		return s

	def swap(self, ks):
		ks.__data,self.__data = self.__data,ks.__data

	def find(self, c, index=0):
		try:
			return self.__data.index(c, index)
		except ValueError:
			return -1


