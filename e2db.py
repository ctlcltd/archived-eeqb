#!/usr/bin/env python3
#  e2db.py
#  
#  @author Leonardo Laureti
#  @license MIT License
#  

import os
from io import BytesIO
import re
from ftplib import FTP
from xml.etree import ElementTree

from commons import *



class e2db_parser():
	allowed = r'(^blacklist|lamedb|settings|whitelist$)|(^(cables|satellites|terrestrial)\.xml$)|(^bouquets\.(radio|tv)$)|(^[^\.]+\.[\w\d]+\.(radio|radio\.simple|tv|tv\.simple)$)'

	def parse_e2db(self, e2db):
		debug('e2db_parser', 'parse_e2db()')

		channels = {}
		channels['lamedb'] = self.parse_e2db_lamedb(e2db['lamedb'])

		bouquets = filter(lambda path: path.startswith('bouquets.'), e2db)

		for filename in bouquets:
			db = self.parse_e2db_bouquet(e2db[filename])

			for filename in db['userbouquets']:
				name = re.match(r'[^.]+.([\w\d]+).(\w+)', filename)
				idx = name[2] + ':' + name[1]

				channels[idx] = self.parse_e2db_userbouquet(channels['lamedb'], e2db[filename])

		return channels

	def parse_e2db_lamedb(self, lamedb):
		debug('e2db_parser', 'parse_e2db_lamedb()')

		db = {}

		step = False
		count = 0
		index = 0
		chid = ''

		for line in lamedb:
			if not step and line == 'services':
				step = True
				continue
			elif step and line == 'end':
				step = False
				continue

			if step:
				count += 1

				if count == 1:
					# chid = line[:-5].upper().split(':')
					chid = line.upper().split(':')
					chid = chid[0].lstrip('0') + ':' + chid[2].lstrip('0') + ':' + chid[3].lstrip('0') + ':' + chid[1].lstrip('0')
					index += 1
				elif count == 2:
					db[chid] = {}
					db[chid]['index'] = index
					db[chid]['channel'] = to_UTF8(line)
				elif count == 3:
					chdata = line.split(',')

					for i, value in enumerate(chdata):
						chdata[i] = value.split(':') 

					db[chid]['data'] = chdata

					count = 0
					chid = ''

		return db

	def parse_e2db_bouquet(self, bouquet):
		debug('e2db_parser', 'parse_e2db_bouquet()')

		bs = {'name': '', 'userbouquets': []}

		for line in bouquet:
			if line.startswith('#SERVICE'):
				filename = re.search(r'(?:")([^"]+)(?:")', line)[1]

				bs['userbouquets'].append(filename)
			elif line.startswith('#NAME'):
				bs['name'] = line.lower()

		return bs

	def parse_e2db_userbouquet(self, channels_lamedb, userbouquet):
		debug('e2db_parser', 'parse_e2db_userbouquet()')

		ub = {'name': '', 'list': {}}
		step = False
		index = 0

		for line in userbouquet:
			if step and line.startswith('#SORT'):
				step = False
				continue
			elif not step and line.startswith('#NAME'):
				ub['name'] = to_UTF8(line[6:].split('  ')[0])
				step = True
				continue
			elif step and line.startswith('#DESCRIPTION'):
				ub['list'][chid] = to_UTF8(line[13:])
				continue

			if step:
				# chid = line[9:-7].upper().split(':')
				chid = line[9:-7].upper().split(':')

				if len(chid) > 6:
					if chid[1] != '64':
						index += 1

						chid = chid[3] + ':' + chid[4] + ':' + chid[5] + ':' + chid[6]
					else:
						chid = chid[0] + ':' + chid[1] + ':' + chid[2] + ':' + chid[3]
				else:
					chid = False

				if chid and chid in channels_lamedb and chid not in ub['list']:
					ub['list'][chid] = index

		return ub

	def get_channels_data(self, e2db):
		debug('e2db_parser', 'get_channels_data()')

		chdata= {}
		channels = self.parse_e2db(e2db)

		chdata['channels'] = channels['lamedb']
		chdata['tv:0'] = {'name': 0, 'list': {}}
		chdata['radio:0'] = {'name': 0, 'list': {}}
		groups = {'tv': {}, 'radio': {}}

		for clist in channels:
			if clist == 'lamedb':
				continue

			group = clist.split(':')[0]

			for chid in channels[clist]['list']:
				if chid not in groups[group]:
					groups[group][chid] = channels[clist]['list'][chid]

			chdata[clist] = channels[clist]

		index = {'tv': 0, 'radio': 0}

		for chid in channels['lamedb']:
			if chid in groups['tv']:
				index['tv'] += 1
				chdata['tv:0']['list'][chid] = index['tv']
			elif chid in groups['radio']:
				index['radio'] += 1
				chdata['radio:0']['list'][chid] = index['radio']

		debug('e2db_parser', 'get_channels_data()', 'index', index)

		return chdata

	def get_ftpfile(self, ftp, filename):
		debug('e2db_parser', 'get_ftpfile()')

		try:
			reader = BytesIO()
			ftp.retrbinary('RETR ' + filename, reader.write)
			return reader.getvalue()
		except Exception as err:
			error('e2db_parser', 'get_ftpfile()', 'FTPcom Exception', err)
		except:
			error('e2db_parser', 'get_ftpfile()')

	def get_e2db_ftp(self):
		debug('e2db_parser', 'get_e2db_ftp()')

		e2db = {}

		try:
			ftp = FTPcom().open()
			e2db = update(ftp)
		except Exception as err:
			error('e2db_parser', 'get_e2db_ftp()', 'FTPcom Exception', err)
		except:
			error('e2db_parser', 'get_e2db_ftp()')
		#TODO FIX
		# else:
		# 	ftp.close()

		return e2db

	def get_e2db_localdir(self, localdir):
		debug('e2db_parser', 'get_e2db_localdir()')

		e2db = {}
		localdir = localdir.rstrip('/')
		dirlist = os.listdir(localdir)

		for path in dirlist:
			path = os.path.basename(path)
			filename = localdir + '/' + path

			if not re.match(self.allowed, path):
				continue
			with open(filename, 'rb') as input:
				e2db[path] = input.read().decode('utf-8').splitlines()

		return e2db

	def load(self, localdir):
		debug('e2db_parser', 'load()', localdir)

		e2db = self.get_e2db_localdir(localdir)
		chdata = self.get_channels_data(e2db)

		return chdata
