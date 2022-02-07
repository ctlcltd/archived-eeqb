#!/usr/bin/env python3
#  app.py
#  
#  @author Leonardo Laureti
#  @license MIT License
#  

import sys

from config import *
from commons import debug



def main():
	debug('main()')

	if GUI_INTERFACE == 'tk':
		from gui_tk import gui
	elif GUI_INTERFACE == 'qt6':
		from gui_qt6 import gui

	if gui:
		gui()
	else:
		debug('sys exit')


if __name__ == '__main__':
	main()
