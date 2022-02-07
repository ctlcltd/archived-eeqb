#!/usr/bin/env python3
#  gui_qt6.py
#  
#  @author Leonardo Laureti
#  @license MIT License
#  

import sys
import os
import time
import re
import json
from functools import partial
from PySide6.QtGui import QScreen
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QToolBar, QFileDialog, QMessageBox, QSizePolicy, QWidget)

from config import *
from commons import debug
from e2db import e2db_parser



class gui():
	def __init__(self):
		debug('gui', 'qt6')

		root = QApplication([])

		screen = root.primaryScreen()
		wsize = screen.availableSize()

		mwid = QWidget()
		mwid.setWindowTitle('enigma2 channel editor')
		mwid.resize(wsize)

		root.setStyleSheet('QGroupBox { spacing: 0; padding: 20px 0 0 0; border: 0 } QGroupBox::title { margin: 0 12px }')

		self.main(mwid)

		mwid.show()

		root.exec()


	def main(self, root):
		debug('gui', 'main()', root)

		self.chdata = None

		self.tab(root)


	def tab(self, root):
		debug('gui', 'tab()', root)

		frm = QGridLayout(root)

		top = QHBoxLayout()
		container = QGridLayout()
		bottom = QHBoxLayout()

		bouquets = QGroupBox('Bouquets')
		channels = QGroupBox('Channels')

		bouquets_box = QVBoxLayout()
		list_box = QVBoxLayout()

		container.addWidget(bouquets, 1, 0)
		container.addWidget(channels, 1, 1)

		self.bouquets_tree = QTreeWidget()
		self.list_tree = QTreeWidget()

		self.bouquets_tree.setStyleSheet('::item { padding: 2px auto }')
		self.list_tree.setStyleSheet('::item { padding: 4px auto }')

		header_item = self.bouquets_tree.headerItem()
		header_item.setText(0, 'Bouquets')
		header_item.setSizeHint(0, QSize(0, 0))

		header_item = QTreeWidgetItem(('Index', 'Name', 'CHID', 'Provider', 'DATA'))
		#TODO FIX
		# header_item.setSizeHint(0, QSize(50, 20))
		# header_item.setSizeHint(1, QSize(100, 20))
		# header_item.setSizeHint(2, QSize(100, 20))
		# header_item.setSizeHint(3, QSize(100, 20))
		# header_item.setSizeHint(4, QSize(0, 20))

		self.list_tree.setHeaderItem(header_item)

		top_toolbar = QToolBar()
		top_toolbar.addAction('New', self.new)
		top_toolbar.addAction('Open',self.load)
		top_toolbar.addAction('Save', todo)
		top_toolbar.addAction('Import', todo)
		top_toolbar.addAction('Export', todo)
		top_toolbar.setStyleSheet('QToolButton { font: 20px }')

		# spacer = QWidget()
		# spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		bottom_toolbar = QToolBar()
		# bottom_toolbar.addWidget(spacer)
		bottom_toolbar.setStyleSheet('QToolButton { font: bold 16px }')

		if DEBUG:
			f_temp_load_bound = partial(self.load, APP_SEEDS)
			bottom_toolbar.addAction('§ Load seeds', f_temp_load_bound)

		self.bouquets_tree.itemClicked.connect(self.populate)

		top.addWidget(top_toolbar)
		bottom.addWidget(bottom_toolbar)

		bouquets_box.addWidget(self.bouquets_tree)
		bouquets.setLayout(bouquets_box)

		list_box.addWidget(self.list_tree)
		channels.setLayout(list_box)

		bouquets.setFlat(True)
		channels.setFlat(True)

		container.setColumnStretch(0, 0)
		container.setColumnStretch(1, 1)

		frm.addLayout(top, 0, 0)
		frm.addLayout(container, 1, 0)
		frm.addLayout(bottom, 2, 0)


	def new(self):
		debug('gui', 'new()')

		self.chdata = None

		self.bouquets_tree.scrollToItem(self.bouquets_tree.topLevelItem(0))
		self.bouquets_tree.clear()
		self.list_tree.scrollToItem(self.list_tree.topLevelItem(0))
		self.list_tree.clear()


	def load(self, filename=False):
		debug('gui', 'load()', filename)

		if filename:
			dirname = filename
		else:
			dirname = QFileDialog.getExistingDirectory(caption='Select enigma2 db folder', dir='~')

		if dirname:
			self.new()
			self.chdata = e2db_parser().load(dirname)
		else:
			return

		titem = QTreeWidgetItem()
		titem.setData(0, Qt.UserRole, {'bouquet_id': 'all'})
		titem.setText(0, 'All channels')

		self.bouquets_tree.addTopLevelItem(titem)

		bgroups = {}

		for bname in self.chdata:
			debug('gui', 'load()', 'bname', bname)

			if bname == 'channels':
				continue

			bdata = self.chdata[bname]

			# debug('gui', 'load()', 'bdata', bdata)

			bgroup = bname.split(':')[0]

			if bdata['name'] == 0:
				pgroup = QTreeWidgetItem()
				pgroup.setData(0, Qt.UserRole, {'bouquet_id': bgroup})
				pgroup.setText(0, bgroup.upper())

				self.bouquets_tree.addTopLevelItem(pgroup)
				self.bouquets_tree.expandItem(pgroup)

				bgroups[bgroup] = pgroup
			else:
				pgroup = bgroups[bgroup]

				bitem = QTreeWidgetItem(pgroup)
				bitem.setData(0, Qt.UserRole, {'bouquet_id': bname})
				bitem.setText(0, bdata['name'])

				self.bouquets_tree.addTopLevelItem(bitem)

		self.populate()


	def populate(self, item=None):
		selected = self.bouquets_tree.currentItem()
		cur_bouquet = None

		if selected:
			selected = selected.data(0, Qt.UserRole)
			cur_bouquet = selected['bouquet_id']

		debug('gui', 'populate()', item, cur_bouquet)

		cur_chlist = 'channels'
		cur_chdata = self.chdata['channels']

		if cur_bouquet and cur_bouquet != 'all':
			cur_chlist = cur_bouquet
			cur_chdata = self.chdata[cur_bouquet]['list']

		self.list_tree.scrollToItem(self.list_tree.topLevelItem(0))
		self.list_tree.clear()

		# debug('gui', 'populate()', 'self.chdata[cur_chlist]', self.chdata[cur_chlist])

		for cid in cur_chdata:
			if cid in self.chdata['channels']:
				cdata = self.chdata['channels'][cid]

				if cur_chlist != 'channels':
					idx = cur_chdata[cid]
				else:
					idx = cdata['index']

				item = QTreeWidgetItem((str(idx), cdata['channel'], cid, cdata['data'][0][1], str(cdata['data'])))
				item.setTextAlignment(4, Qt.AlignRight)

				self.list_tree.addTopLevelItem(item)
			else:
				item = QTreeWidgetItem(('', cur_chdata[cid], cid, '', ''))

				self.list_tree.addTopLevelItem(item)


def todo():
	print('app TODO')
	QMessageBox(text='app TODO').exec()


if __name__ == '__main__':
	app()
