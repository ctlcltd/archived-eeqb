#!/usr/bin/env python3
#  app.py
#  
#  @link https://github.com/ctlcltd/e2-sat-editor-qb
#  @copyright e2 SAT Editor Team
#  @author Leonardo Laureti
#  @version 0.1
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
