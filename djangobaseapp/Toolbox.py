import configparser
import requests
import random
import urllib
import base64
from Crypto.Cipher import AES
from datetime import datetime
from time import gmtime, strftime
import hmac,hashlib
import platform
import os
import datetime
import pprint
import psycopg2
import psycopg2.extras
import uuid
import logging
import json
from django.db import models, connection
# from Crypto import Random
# from Constants import Constants
# import pandas as pd

class Toolbox():
	def __init__(self):
		# 	Load config file - must happen first
		self.loadConfigFile()
		self.pp = pprint.PrettyPrinter(indent=4)
		self.SOFTWARE_DATA = {
			"name":"website"
			, "version":"0.01"
			, "log":"django_website_rpr"}
		self.SLACK = {}

	def loadConfigFile(self):
		"""
			Validates the existence of & type of file. Then loads config.json
		"""
		CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
		fileLoc = '{}/config.json'.format(CURRENT_DIRECTORY)
		if not os.path.isfile(fileLoc):
			log_msg = "A config file is required"
			self.cleanPrint(log_msg)
			raise Exception(log_msg)

		with open(fileLoc) as config_file:
			self.CONFIG = json.load(config_file)
		#	Config can be changed after it is loaded.  
		#	At the time of loading it is still unchanged by another
		self.CONFIG_WAS_CHANGED = False

	def establish_PGSQL(self):
		self.PGSQL_CONNECTION = psycopg2.connect(
			host 		= self.CONFIG['pgsql']['host']
			, database 	= self.CONFIG['pgsql']['name']
			, user 		= self.CONFIG['pgsql']['user']
			, password 	= self.CONFIG['pgsql']['pass']
			)
		self.PGSQL_CURSOR = self.PGSQL_CONNECTION.cursor()
		self.PGSQL_DICT_CURSOR = self.PGSQL_CONNECTION.cursor(
			cursor_factory=psycopg2.extras.RealDictCursor)

	def multiLogger(self, msg, **kwargs):
		"""
			Routes a message to:
				 * Log
				 * Slack
				 * Display

			Supports status types
				 * info
				 * error

			Example usage:
				 * self.multiLogger("Hello world",status = "error")

		"""

		#	Get the log level or set it to 3 if None
		level = kwargs.get('level',3)

		#	Get the log status or set it to 'info' if None
		status = kwargs.get('status','info')


		slack_message = "`{uuid}`\t{SOFTWARE_NAME} [{SOFTWARE_VERSION}]\t"\
				"`{status}`\t{msg}".format(uuid = str(uuid.uuid4())[:8]
			, SOFTWARE_NAME 	= self.SOFTWARE_DATA['name']
			, SOFTWARE_VERSION 	= self.SOFTWARE_DATA['version']
			, status = status.upper()
			, msg = msg)
		full_message = slack_message.replace("`","")

		if level >= 1:
			if status.lower() == 'error':
				#self.LOGGER.error(full_message)
				pass
			else:
				#self.LOGGER.info(full_message)
				pass
		if level >= 2:
			if status.lower() == 'error':
				self.cleanPrint(full_message,"Fail")
			else:
				self.cleanPrint(full_message)
		# if level >= 3:
		# 	self.SLACK.chat.post_message(self.CONFIG['slackbot']['log']
		# 		, slack_message)

	def cleanPrint(self,msg, msgType = None):
		"""
			Prints in a neat format and in different colors
		"""
		self.CLEANPRINT_COLOR_SET = {"Header":'\033[95m'
				,"Blue":'\033[94m'
				,"Green":'\033[92m'
				,"Warn":'\033[93m'
				,"Fail":'\033[91m'
				,"Underline":'\033[4m'
				,"End":'\033[0m'}
		if len(str(datetime.datetime.now().hour)) == 1:
			hourVar = "0{}".format(datetime.datetime.now().hour)
		else:
			hourVar = datetime.datetime.now().hour
		if len(str(datetime.datetime.now().minute)) == 1:
			minuteVar = "0{}".format(datetime.datetime.now().minute)
		else:
			minuteVar = datetime.datetime.now().minute
		if len(str(datetime.datetime.now().second)) == 1:
			secondVar = "0{}".format(datetime.datetime.now().second)
		else:
			secondVar = datetime.datetime.now().second
		cleanTime = "{}/{} {}:{}:{}".format(datetime.datetime.now().month
			,datetime.datetime.now().day
			,hourVar
			,minuteVar
			,secondVar
			)
		if "windows" in platform.platform().lower() or msgType == None:
			print(" * *\t{} - {}".format(cleanTime, msg))
		else:
			print(self.CLEANPRINT_COLOR_SET[msgType], "* *\t{} - {}".format(
				cleanTime, msg),self.CLEANPRINT_COLOR_SET["End"])

	def startLogger(self):
		"""
			Logs general app functionality
			Stores logs in C:\\logs or /var/logs depending on OS
			Prepends filename of runner to filename
		"""
		SERVER_OS = platform.system().lower()
		if 'windows' in SERVER_OS:
			# If windows add to windows directory
			LOG_FILE_DIRECTORY = "C:\\logs\\"
			if not os.path.isdir(LOG_FILE_DIRECTORY):
				os.makedirs(LOG_FILE_DIRECTORY)
			tmp_filename = __file__.split("\\")
		else:
			# If Linux (or Mac) add to default log directory
			LOG_FILE_DIRECTORY = "/home/admin/"
			if not os.path.isdir(LOG_FILE_DIRECTORY):
				os.makedirs(LOG_FILE_DIRECTORY)
			tmp_filename = __file__.split("/")

		# Filename is the last item on the list
		SCRIPT_FILENAME = tmp_filename[len(tmp_filename)-1]
		LOG_FILE_LOCATION = "{LOG_FILE_DIRECTORY}{LOG_NAME}.txt".format(
				LOG_FILE_DIRECTORY = LOG_FILE_DIRECTORY
				, LOG_NAME = self.SOFTWARE_DATA['log'])
		LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
		logging.basicConfig(
			filename = LOG_FILE_LOCATION
			, level = logging.INFO
			, format = LOG_FORMAT
			, filemode = 'a')
		self.LOGGER = logging.getLogger()


	def strip_decoding(self,_str):
		"""
			@method strip_decoding will string base64 and decode the string to a 
			normal format
			@param _str is a string which will be decoded

		"""
		return _str.decode('UTF-8').split('_')[0]
		#end of encryption block

	def fileWrite(self, cursor, filename, filetype):
		"""
			Sergio Molanes - 10/29/2016
			@fileWrite creates a file based on a SQL Query.
			It accepts a cursor, filename (with location)
			and file type as parameters.
			Dependencies: CSV, Pandas
		"""
		if filetype.lower() == "xls" or filetype.lower() == "xlsx":
			data_set =  cursor.fetchall()
			columns = [desc[0] for desc in cursor.description]
			df = pd.DataFrame(list(data_set), columns=columns)
			writer = pd.ExcelWriter("{}.xlsx".format(filename))
			df.to_excel(writer, sheet_name='Data', index=False)
			writer.save()

		elif filetype.lower() == "csv":
			data_set =  cursor.fetchall()
			with open("{}.csv".format(filename), 'w', newline='') as csvfile:
				csvwriter = csv.writer(csvfile, delimiter=',',
					quotechar='"', quoting=csv.QUOTE_MINIMAL)
				xHeader = [columnHeader[0] for columnHeader in cursor.description]
				csvwriter.writerow(xHeader)
				for i, row in enumerate(data_set):
					xList = []
					for column in row:
						xList.append(column)
					csvwriter.writerow(xList)

	def django_addNotification(self,uid,_type,message):
		notif_cursor = connection.cursor()
		addNote_query = """SELECT public.usp_add_user_notification(
			'{}','{}','{}!')""".format(uid,_type,message)
		try:
			notif_cursor.execute(addNote_query)
		except Exception as ex:
			print(str(ex))
			print("Notification could not be added.")
		notif_cursor.close()

	def django_getNotifications(self,uid):
		notif_cursor = connection.cursor()
		notifications_query="""SELECT 
					v_notification_type
					,v_notification_value
					,to_char(v_dateadded, 'MM/DD/YYYY')
					,v_ui_element
				FROM public.usp_get_user_notification('{}')
				ORDER BY v_dateadded DESC""".format(uid)
		notif_cursor.execute(notifications_query)

		notifications=[]
		for notification_block in notif_cursor.fetchall():
			current_notification = {"Type":     notification_block[0]
									,"Message": notification_block[1]
									,"Date":    notification_block[2]
									,"ui_element":    notification_block[3]}
			notifications.append(current_notification)
		notif_cursor.close()
		return notifications

	def sweetify_errors(self,error_block):
		out = ""
		if "The two password fields didn&#39;t match." in error_block:
			print("1")
			out = "{}{}".format(out," - The two passwords did not match\n")
		if "Enter a valid email address" in error_block:
			print("2")
			out = "{}{}".format(out," - Enter a valid email address\n")
		if "password is too short" in error_block:
			print("3")
			out = "{}{}".format(out," - The password must be at least 8 characters\n")
		return out

	def encrypt( self, raw_text ):
		"""
			Encrypts a string using bcrypt algorithm 
			@raw_text is data to be encrypted
			returns bcrypt encrypted text
		"""
		raw_text = (raw_text)
		# - AES requires its bnlocks to be of size mod 16
		# - However we don't want unusable characters in a password
		# - First Pipe "|" delimits the padding from the password
		# - Then Tilde "~" acts as padding.
		if len(raw_text)%16 != 0:
			raw_text = raw_text+"|"
		while len(raw_text)%16 != 0:
			raw_text = raw_text+"~"
		raw_text = raw_text.encode()
		#genearate a random block
		iv = Random.new().read( AES.block_size )
		#encrypt plain text with a key and hash
		cipher = AES.new( self.ENCRYPTION_KEY, AES.MODE_CBC, iv )
		#return base64 encrypted string
		return base64.b64encode( iv + cipher.encrypt( raw_text ) ) 
	
	def decrypt( self, encrypted_text ):
		"""
			Decrypts into text using bcrypt algorithm
			@encrypted_text:Input is a bcrypt encrypted block
			returns raw text
		"""
		encrypted_text = base64.b64decode(encrypted_text)
		iv = encrypted_text[:16]
		try:
			cipher = AES.new(self.ENCRYPTION_KEY, AES.MODE_CBC, iv )
		except:
			self.cleanPrint("Decryption error","error")
			return

		# - To compensate for delimeter/padding above, we rstrip
		# - the excess & remove the padding
		decrypt_msg = cipher.decrypt(encrypted_text[16:])
		decrypt_msg = decrypt_msg.decode()
		decrypt_msg = decrypt_msg.rstrip("~")
		decrypt_msg = decrypt_msg.rstrip("|")
		return decrypt_msg