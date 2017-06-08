#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/app/")

from app import app as application
application.secret_key = '596a96cc7bf9108cd896f33c44aedc8a'
