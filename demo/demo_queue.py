# Author: Nike Liu
import time
import configparser
import queue
import os

class test():
	def __init__(self):
		self.q = queue.Queue(20)
		self.putdata()
		self.getdata()

	def putdata(self):

		list1=[159915,159939,161028]

		# 读取列表里的股票代码 并存入到队列
		for num in list1:

			self.q.put(num)

	def printdata(self,a):
		print('%s is ok'%a)

	def getdata(self):
		# 这里利用队列取尽时的异常 来判断是否取尽 取尽则停止三秒 并清空控制台输出
		while True:
			try:
				self.data = self.q.get(False)
				self.printdata(self.data)
			except:
				time.sleep(1)
				# 清空控制台输出
				os.system('cls')
				self.putdata()


if __name__ == '__main__':
	test()

