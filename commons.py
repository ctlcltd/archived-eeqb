#!/usr/bin/env python3
#  commons.py
#  
#  @author Leonardo Laureti
#  @license MIT License
#  

import sys
import traceback
import json

from config import *


IS_WIN = sys.platform == 'win32'
IS_DARWIN = sys.platform == 'darwin'
IS_LINUX = sys.platform == 'linux'



def to_UTF8(obj):
	return str(obj)


def to_JSON(obj):
	return json.dumps(obj, separators=(',', ':')).encode('utf-8')


def debug(*args):
	if DEBUG:
		print(*args)


def error(*args):
	if isinstance(args[-1], BaseException):
		errmsg = str(args[-1])
		errtype = type(errmsg).__name__
	else:
		errmsg = str(sys.exc_info()[1])
		errtype = sys.exc_info()[0].__name__

	print(*args[:1], 'error:', errtype, '"' + errmsg + '"')
	traceback.print_tb(sys.exc_info()[2])
	print()
