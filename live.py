#!/usr/bin/env python3
#  live.py
#  
#  @link https://github.com/ctlcltd/e2-sat-editor-qb
#  @copyright e2 SAT Editor Team
#  @author Leonardo Laureti
#  @version 0.1
#  @license MIT License
#  

import os
import time
from subprocess import Popen
from functools import partial
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class wd_EventHandler(FileSystemEventHandler):
	def __init__(self, target):
		super(wd_EventHandler, self).__init__()

		self.target = target
		self.prevented = False

	def on_modified(self, event):
		self.trigger(event)

	def on_created(self, event):
		self.trigger(event)

	def on_deleted(self, event):
		self.trigger(event)

	def prevent(self, event):
		path = os.path.basename(event.src_path)

		self.prevented = False

		if path.startswith('.') or path.endswith('.'):
			self.prevented = True

	def trigger(self, event):
		self.prevent(event)

		if not self.prevented:
			self.target()


def reload():
	if 'app_p' in globals():
		globals()['app_p'].terminate()
		time.sleep(2)

	#TODO os switch

	globals()['app_p'] = Popen(['python3', './app.py'])


def main():
	event_handler = wd_EventHandler(reload)
	observer = Observer()
	observer.schedule(event_handler, path='.', recursive=False)
	observer.start()

	reload()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
		observer.join()


if __name__ == '__main__':
	main()
