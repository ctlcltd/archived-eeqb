#!/usr/bin/env python3
#  e2db.py
#  
#  @link https://github.com/ctlcltd/e2-sat-editor-qb
#  @copyright e2 SAT Editor Team
#  @author Leonardo Laureti
#  @version 0.1
#  @license MIT License
#  

import os
from io import BytesIO
import re

from commons import *


SAT_POL = ('H', 'V', 'L', 'R')
SAT_FEC = ('', 'Auto', '1/2', '2/3', '3/4', '5/6', '7/8', '3/5', '4/5', '8/9', '9/10')
SAT_INV = ('Auto', 'On', 'Off')
SAT_SYS = ('DVB-S', 'DVB-S2')
SAT_MOD = ('Auto', 'QPSK', 'QAM16', '8PSK')
SAT_ROL = ('Auto', 'QPSK', 'QAM16', '8PSK')
SAT_PIL = ('Auto', 'Off', 'On')



class e2db_parser():
	#TODO filter
	allowed = r'(^blacklist|lamedb|settings|whitelist$)|(^(cables|satellites|terrestrial)\.xml$)|(^bouquets\.(radio|tv)$)|(^[^\.]+\.[\w\d]+\.(radio|radio\.simple|tv|tv\.simple)$)'

	def parse_e2db(self, e2db):
		debug('e2db_parser', 'parse_e2db()')

		lamedb = self.parse_e2db_lamedb(e2db['lamedb'])

		channels = {}
		channels['lamedb'] = lamedb

		bouquets = filter(lambda path: path.startswith('bouquets.'), e2db)

		for filename in bouquets:
			db = self.parse_e2db_bouquet(e2db[filename])

			for filename in db['userbouquets']:
				name = re.match(r'[^.]+.([\w\d]+).(\w+)', filename)
				idx = name[2] + ':' + name[1]

				channels[idx] = self.parse_e2db_userbouquet(channels['lamedb']['services'], e2db[filename])

		return channels

	def parse_e2db_lamedb(self, lamedb):
		debug('e2db_parser', 'parse_e2db_lamedb()')

		db = {'transponders': {}, 'services': {}}

		step = 0
		count = 0
		index = 0
		txid = ''
		chid = ''

		for line in lamedb:
			if not step and line == 'transponders':
				step = 1
				continue
			if not step and line == 'services':
				step = 2
				continue
			elif step and line == 'end':
				step = 0
				continue

			if step == 1:
				count += 1

				if count == 1:
					tx = list(map(lambda a: a.lstrip('0'), line.upper().split(':')))
					txid = tx[1] + ':' + tx[2] + ':' + tx[0]
					db['transponders'][txid] = {'dvbns': tx[0], 'tid': tx[1], 'nid': tx[2]}
				elif count == 2:
					txdata = list(map(lambda a: int(a.lstrip('0') or 0), line[3:].split(':')))
					db['transponders'][txid]['type'] = line[1:2]
					db['transponders'][txid]['txdata'] = txdata
				elif count == 3:
					count = 0
			elif step == 2:
				count += 1

				if count == 1:
					ch = list(map(lambda a: a.lstrip('0'), line.upper().split(':')))
					txid = ch[2] + ':' + ch[3] + ':' + ch[1]
					chid = ch[0] + ':' + ch[2] + ':' + ch[3] + ':' + ch[1]
					db['services'][chid] = {}
					db['services'][chid]['ssid'] = ch[0]
					db['services'][chid]['dvbns'] = ch[1]
					db['services'][chid]['tsid'] = ch[2]
					db['services'][chid]['onid'] = ch[3]
					db['services'][chid]['stype'] = int(ch[4] or 0)
					db['services'][chid]['snum'] = int(ch[5] or 0)
					index += 1
				elif count == 2:
					db['services'][chid]['index'] = index
					db['services'][chid]['txid'] = txid
					db['services'][chid]['chname'] = to_UTF8(line)
				elif count == 3:
					chdata = line.split(',')

					for i, value in enumerate(chdata):
						chdata[i] = value.split(':') 

					db['services'][chid]['data'] = chdata

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

	def parse_e2db_userbouquet(self, services, userbouquet):
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
				chid = line[9:-7].upper().split(':')

				if len(chid) > 6:
					if chid[1] != '64':
						index += 1

						chid = chid[3] + ':' + chid[4] + ':' + chid[5] + ':' + chid[6]
					else:
						chid = chid[0] + ':' + chid[1] + ':' + chid[2] + ':' + chid[3]
				else:
					chid = False

				if chid and chid in services and chid not in ub['list']:
					ub['list'][chid] = index

		return ub

	def get_channels_data(self, channels):
		debug('e2db_parser', 'get_channels_data()')

		chdata = {}
		chdata['channels'] = channels['lamedb']['services']
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

		for chid in channels['lamedb']['services']:
			if chid in groups['tv']:
				index['tv'] += 1
				chdata['tv:0']['list'][chid] = index['tv']
			elif chid in groups['radio']:
				index['radio'] += 1
				chdata['radio:0']['list'][chid] = index['radio']

		debug('e2db_parser', 'get_channels_data()', 'index', index)

		return chdata

	#TODO
	def get_transponders_data(self, channels):
		debug('e2db_parser', 'get_transponders_data()')

		txdata = channels['lamedb']['transponders']

		for txid in txdata:
			tx = txdata[txid]

			if not tx['type'] == 's':
				continue

			tx['freq'] = '{:n}'.format(tx['txdata'][0] / 1e3)
			tx['sr'] = '{:n}'.format(tx['txdata'][1] / 1e3)
			tx['pol'] = SAT_POL[tx['txdata'][2]]
			tx['fec'] = SAT_FEC[tx['txdata'][3]]
			tx['pos'] = str(tx['txdata'][4]) #TODO satellites.xml
			tx['inv'] = SAT_INV[tx['txdata'][5]]
			tx['flgs'] = tx['txdata'][6]
			tx['sys'] = 7 in tx['txdata'] and SAT_SYS[tx['txdata'][7]] or SAT_SYS[0]
			tx['mod'] = 8 in tx['txdata'] and SAT_MOD[tx['txdata'][8]] or SAT_MOD[0]
			tx['rol'] = 9 in tx['txdata'] and SAT_ROL[tx['txdata'][9]] or None # DVB-S2 only
			tx['pil'] = 10 in tx['txdata'] and SAT_PIL[tx['txdata'][10]] or None # DVB-S2 only

		# debug('e2db_parser', 'get_transponders_data()', 'txdata', txdata)

		return txdata

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
		channels = self.parse_e2db(e2db)

		chdata = self.get_channels_data(channels)
		txdata = self.get_transponders_data(channels)

		return {'txdata': txdata, 'chdata': chdata}
