#!/usr/bin/env python3

from string import string

class box:
	__align = 0

	__px = ''
	__pa = ''
	__pyl = ''
	__pyr = ''

	__width = 0
	__buffer = string()

	def __init__(self, px='-', pa='+', pyl='| ', pyr=' |'):
		self.__px = px
		self.__pa = pa
		self.__pyl = pyl
		self.__pyr = pyr

	def __str__(self):
		return str(self.__buffer)

	def set_align(self, a):
		self.__align = a

	def clear(self):
		self.__buffer.clear()

	def buttom(self, n):
		w = n + len(self.__pyl) + len(self.__pyr) - len(self.__pa) * 2
		self.__buffer.append(self.__pa)
		for i in range(w):
			self.__buffer.push_back(self.__px)
		self.__buffer.append(self.__pa)
		self.__buffer.push_back('\n')

	def line(self, ks, start, end):
		wd = self.__width - self.width_fix(ks, start, end)
		if self.__align < 0:
			left = 0
			right = wd
		elif self.__align > 0:
			left = wd
			right = 0
		else:
			left = wd//2
			right = wd - left
		self.__buffer.append(self.__pyl)
		for i in range(left):
			self.__buffer.push_back(' ')
		for i in range(start, end):
			self.__buffer.push_back(ks[i])
		for i in range(right):
			self.__buffer.push_back(' ')
		self.__buffer.append(self.__pyr)
		self.__buffer.push_back('\n')

	def box(self, ks):
		index1 = 0
		width = self.string_width(ks)
		self.__width = width
		self.buttom(width)
		size = ks.size()
		while index1 < size:
			index2 = ks.find('\n', index1)
			if index2 < 0:
				index2 = size
			self.line(ks, index1, index2)
			index1 = index2 + 1
		self.buttom(width)
		return self
		

	def width_fix(self, ks, start, end):
		width = end - start
		for i in range(start, end):
			if '\u4e00' <= ks[i] <= '\u9fff':
				width += 1
		return width

	def string_width(self, ks):
		index1 = 0
		width = 0
		size = ks.size()
		while index1 < size:
			index2 = ks.find('\n', index1)
			if index2 < 0:
				index2 = size
			subw = self.width_fix(ks, index1, index2)
			if subw > width:
				width = subw
			index1 = index2 + 1
		return width

	def multi(self, n):
		ks = string()
		for i in range(n):
			ks.clear()
			ks.swap(self.__buffer)
			self.box(ks)

