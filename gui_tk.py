#!/usr/bin/env python3
#  gui_tk.py
#  
#  @author Leonardo Laureti
#  @license MIT License
#  

import os
import time
from threading import Thread
import re
import json
from functools import partial
from tkinter import *
from tkinter import ttk, filedialog, messagebox

from config import *
from commons import debug, IS_DARWIN
from e2db import e2db_parser



class gui():
	def __init__(self):
		debug('gui', 'tk')

		root = Tk()

		root.title('enigma2 channel editor')
		w, h = root.winfo_screenwidth(), root.winfo_screenheight()
		root.geometry('%dx%d+0+0' % (w, h))

		style = ttk.Style(root)
		# style.theme_use('default')

		#TODO ? top / bottom buttons slow down
		# t_app = Thread(target=self.main, args=[root])
		# t_app.start()

		self.main(root)

		root.mainloop()


	def main(self, root):
		debug('gui', 'main()', root)

		self.chdata = None

		self.tab(root)


	def tab(self, root):
		debug('gui', 'tab()', root)

		frm = ttk.Frame(root, padding=4)
		frm.pack(fill=BOTH, expand=1)

		top = ttk.Frame(frm, padding=(12,12,4,16))
		container = ttk.Panedwindow(frm, orient=HORIZONTAL)
		bottom = ttk.Frame(frm, padding=(12,12,4,4))

		bouquets = ttk.Labelframe(container, text='Bouquets')
		channels = ttk.Labelframe(container, text='Channels')

		container.add(bouquets)
		container.add(channels)

		self.bouquets_tree = ttk.Treeview(bouquets)

		bouquets_vsb = ttk.Scrollbar(bouquets, orient=VERTICAL, command=self.bouquets_tree.yview)
		bouquets_hsb = ttk.Scrollbar(bouquets, orient=HORIZONTAL, command=self.bouquets_tree.xview)

		self.bouquets_tree.configure(xscrollcommand=bouquets_hsb.set, yscrollcommand=bouquets_vsb.set)

		self.list_tree = ttk.Treeview(channels, columns=('Index', 'Name', 'CHID', 'Provider', 'DATA'), show='headings')
		self.list_tree.column('Index', width=50)
		self.list_tree.column('Name', width=150)
		self.list_tree.column('CHID', width=100)
		self.list_tree.column('Provider', width=100)
		self.list_tree.column('DATA', anchor=E)
		self.list_tree.heading('Index', text='Index')
		self.list_tree.heading('Name', text='Name')
		self.list_tree.heading('CHID', text='CHID')
		self.list_tree.heading('Provider', text='Provider')
		self.list_tree.heading('DATA', text='DATA')

		list_vsb = ttk.Scrollbar(channels, orient=VERTICAL, command=self.list_tree.yview)
		list_hsb = ttk.Scrollbar(channels, orient=HORIZONTAL, command=self.list_tree.xview)

		self.list_tree.configure(xscrollcommand=list_hsb.set, yscrollcommand=list_vsb.set)

		ttk.Button(top, text='New', command=self.new).grid(column=0, row=0)
		ttk.Button(top, text='Open', command=self.load).grid(column=1, row=0)
		ttk.Button(top, text='Save', command=todo).grid(column=2, row=0)
		ttk.Button(top, text='Import', command=todo).grid(column=3, row=0)
		ttk.Button(top, text='Export', command=todo).grid(column=4, row=0)

		if DEBUG:
			f_temp_load_bound = partial(self.load, APP_SEEDS)
			ttk.Button(bottom, text='§ Load seeds', command=f_temp_load_bound).grid(column=6, row=0)

		self.bouquets_tree.grid(column=0, row=0, sticky=(N,W,E,S))
		bouquets_vsb.grid(column=1, row=0, sticky=(N,S))
		bouquets_hsb.grid(column=0, row=1, sticky=(W,E,S))

		list_contextual = Contextual(root)
		bouquets_contextual = Contextual(root)

		if IS_DARWIN:
			right_click = '<Button-2>'
		else:
			right_click = '<Button-3>'

		self.list_tree.bind(right_click, list_contextual.popup)
		self.bouquets_tree.bind(right_click, bouquets_contextual.popup)
		self.bouquets_tree.bind('<<TreeviewSelect>>', self.populate)

		self.list_tree.grid(column=0, row=0, sticky=(N,W,E,S))
		list_vsb.grid(column=1, row=0, sticky=(N,S))
		list_hsb.grid(column=0, row=1, sticky=(W,E,S))

		bouquets.columnconfigure(0, weight=1)
		bouquets.rowconfigure(0, weight=1)
		channels.columnconfigure(0, weight=1)
		channels.rowconfigure(0, weight=1)

		top.grid(column=0, row=0, sticky=(N,W,E))
		container.grid(column=0, row=1, sticky=(N,W,E,S))
		bottom.grid(column=0, row=2, sticky=(W,E,S))

		frm.columnconfigure(0, weight=1)
		frm.rowconfigure(1, weight=1)


	def new(self):
		debug('gui', 'new()')

		self.chdata = None

		self.bouquets_tree.delete(*self.bouquets_tree.get_children())
		self.list_tree.delete(*self.list_tree.get_children())


	def load(self, filename=False):
		debug('gui', 'load()', filename)

		if filename:
			dirname = filename
		else:
			dirname = filedialog.askdirectory(initialdir='~', title='Select enigma2 db folder')

		if dirname:
			self.new()
			self.chdata = e2db_parser().load(dirname)
		else:
			return

		self.bouquets_tree.insert('', 'end', 'all', text='All channels')

		for bname in self.chdata:
			debug('gui', 'load()', 'bname', bname)

			if bname == 'channels':
				continue

			bdata = self.chdata[bname]

			# debug('gui', 'load()', 'bdata', bdata)

			bgroup = bname.split(':')[0]

			if bdata['name'] == 0:
				self.bouquets_tree.insert('', 'end', bgroup, text=bgroup.upper(), open=TRUE)
			else:
				self.bouquets_tree.insert(bgroup, 'end', bname, text=bdata['name'])

		self.populate()


	def populate(self, event=None):
		selected = self.bouquets_tree.focus()

		debug('gui', 'populate()', event, selected)

		cur_chlist = 'channels'
		cur_chdata = self.chdata['channels']

		if selected and selected != 'all':
			cur_chlist = selected
			cur_chdata = self.chdata[selected]['list']

		self.list_tree.delete(*self.list_tree.get_children())

		# debug('gui', 'populate()', 'self.chdata[cur_chlist]', self.chdata[cur_chlist])

		for cid in cur_chdata:
			if cid in self.chdata['channels']:
				cdata = self.chdata['channels'][cid]

				if cur_chlist != 'channels':
					idx = cur_chdata[cid]
				else:
					idx = cdata['index']

				self.list_tree.insert('', 'end', cid, values=(idx, cdata['channel'], cid, cdata['data'][0][1], cdata['data']))
			else:
				self.list_tree.insert('', 'end', cid, values=('', cur_chdata[cid], cid, '', ''))


class Contextual:
	def __init__(self, root):
		self.menu = Menu(root, tearoff=0)
		self.menu.add_command(label='Cut', command=todo)
		self.menu.add_command(label='Copy', command=todo)
		self.menu.add_command(label='Paste', command=todo)
		self.menu.add_command(label='Delete', command=todo)

	def popup(self, event):
		self.menu.post(event.x_root, event.y_root)


def todo():
	print('app TODO')
	messagebox.showinfo(message='app TODO')


if __name__ == '__main__':
	app()
