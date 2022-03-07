#!/usr/bin/env python3
#  ftpcom.py
#  
#  @link https://github.com/ctlcltd/e2-sat-editor-qb
#  @copyright e2 SAT Editor Team
#  @author Leonardo Laureti
#  @version 0.1
#  @license MIT License
#  

from ftplib import FTP
import time

from commons import *



class FTPcom(FTP):
	def __init__(self, *args, **keywords):
		FTP.__init__(self, *args, **keywords)

	def open(self, host, port, user, passwd):
		connect = self.connect(host=host, port=int(port))
		login = self.login(user=user, passwd=passwd)

		debug('FTPcom', 'open()', self.getwelcome())

		if connect.startswith('220') and login.startswith('230'):
			return self
		else:
			self.close()

			raise Exception('FTPcom', 'could not connect', [connect, login])

	def retrieve(self, source, outfile, close=False, read=False):
		debug('FTPcom', 'retrieve()', 'START')

		q = queue.Queue()

		def retry(start=None):
			self.retrbinary('RETR ' + source, callback=q.put, rest=start)
			q.put(None)

		threading.Thread(target=retry).start()

		with open(outfile, 'wb') as output:
			while True:
				chunk = q.get()

				if chunk is not None:
					debug('FTPcom', 'retrieve()', 'REST')

					output.write(chunk)
				else:
					debug('FTPcom', 'retrieve()', 'END')

					if close:
						self.close()

					break

		if read:
			with open(outfile, 'rb') as input:
				return input.read()

	def retrievechunked(self, source, outfile, retry_delay, close=False, read=False):
		debug('FTPcom', 'retrievechunked()', 'START')

		q = queue.Queue()

		def retry(start=None):
			self.retrbinary('RETR ' + source, callback=q.put, rest=start)
			q.put(None)

		threading.Thread(target=retry).start()

		with open(outfile, 'wb') as output:
			size = 0
			last = 0

			while True:
				chunk = q.get()
				size = output.tell()

				if chunk is not None:
					output.write(chunk)
				elif not size == last:
					time.sleep(retry_delay)

					debug('FTPcom', 'retrievechunked()', 'REST', size)

					retry(size)

					last = output.tell()
				else:
					debug('FTPcom', 'retrievechunked()', 'END', size, last)

					if close:
						self.close()

					break

		if read:
			with open(outfile, 'rb') as input:
				return input.read()

	def close(self):
		debug('FTPcom', 'close()', self.quit())

