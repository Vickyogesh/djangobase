from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.ui as ui
import json
from Crypto import Random
from Crypto.Cipher import AES
import requests
from datetime import datetime
import platform
import datetime
import pprint
import psycopg2
import psycopg2.extras
import json
import logging
import base64
import os
import platform

class Toolbox():
	def __init__(self):
		"""
			Provides peripheral & reusable functions for the app
				Loads configuration credentials
		"""
		self.CONSTANTS = {} 
		self.ENCRYPTION_KEY = '__bcrypt_key_here__'.encode()
		self.pp = pprint.PrettyPrinter(indent=4)

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

	def loadSelenium(self, driver, displayUI=True, profile=None):
		"""
			Loads Selenium & returns a driver element
			Supports 
				 - Chrome & Firefox
				 - UI & Headless
				 - With Profile or Default
		"""
		chrome_options = webdriver.ChromeOptions()

		#	Identify ChromeProfile path & create folder
		#script_dir = os.path.dirname(os.path.realpath(__file__))
		if os.name == "nt":
			app_dir = "C:\\app"
		else:
			app_dir = "/home/app"
		if not os.path.exists(app_dir):
			os.makedirs(app_dir)
			log_msg = "Created app directory"
			self.multiLogger(log_msg, level=2)

		profile_dir = f"{app_dir}/ChromeProfiles"
		if not os.path.exists(profile_dir):
			os.makedirs(profile_dir)
			log_msg = "Created Chrome Profiles directory"
			self.multiLogger(log_msg, level=2)

		#	If a profile is specified, find/set
		if profile is not None:
			str_profile = f" [ Profile: {profile} ] "
			profile_path = f"{chrome_profiles}\\{profile}"
			chrome_options.add_argument(f"user-data-dir={profile_path}")
		else:
			str_profile =""
		
		#	If driver is headless, set according options
		if displayUI == True:
			if driver.lower() != "chrome":
				log_msg = "Attempted headless on a non-chrome driver"
				self.multiLogger(log_msg, level=2, status = "error")
				raise Exception(f"Only Chrome supports headless driver"\
					"You have chosen: '{driver}'")
			str_display = f" [ Display: Headless ] "
			chrome_options.add_argument("--headless")
		else:
			str_display = f" [ Display: UI ] "

		#	Selects the driver and applies the options declared above
		if driver.lower() == "chrome":
			str_driver = f" [ Driver: Chrome ] "
			self.CURR_ELEMENT = webdriver.Chrome(chrome_options=chrome_options)
		elif driver.lower() == "firefox":
			str_driver = f" [ Driver: Firefox ] "
			self.CURR_ELEMENT = webdriver.Firefox()
		else:
			str_display = f" [ Driver: {driver} ] "
			raise Exception(f"Unknown Driver: {str_display}")

		log_msg = f"Selenium{str_driver}{str_profile}{str_display}"
		self.multiLogger(log_msg, level=2)
		return self.CURR_ELEMENT

	def mk_isolated_PGSQL_CONN(self):
		"""
			Connects to a PGSQL database & establishes a cursor
		"""
		PGSQL_CONN = psycopg2.connect(
			host 		= self.CONFIG['pgsql']['host']
			, database 	= self.CONFIG['pgsql']['name']
			, user 		= self.CONFIG['pgsql']['user']
			, password 	= self.CONFIG['pgsql']['pass']
		)
		PGSQL_CURS = PGSQL_CONN.cursor()
		return PGSQL_CURS, PGSQL_CONN

	def establish_PGSQL(self):
		"""
			Creates two PGSQL cursors
				Standard response	List of tuples
				Dictionary response	List of dictionaries
			These are shared connections

		"""
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
				self.LOGGER.error(full_message)
			else:
				self.LOGGER.info(full_message)
		if level >= 2:
			if status.lower() == 'error':
				self.cleanPrint(full_message,"Fail")
			else:
				self.cleanPrint(full_message)
		if level >= 3:
			self.SLACK.chat.post_message(self.CONFIG['slackbot']['log']
				, slack_message)

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
		LOG_FILE_NAME = "{LOG_NAME}.txt".format(
			LOG_NAME = self.SOFTWARE_DATA['log'])
		LOG_FILE_LOCATION = "{LOG_FILE_DIRECTORY}{LOG_FILE_NAME}".format(
				LOG_FILE_DIRECTORY = LOG_FILE_DIRECTORY
				, LOG_FILE_NAME = LOG_FILE_NAME)
		LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
		self.archivelog(LOG_FILE_DIRECTORY, LOG_FILE_NAME)

		logging.basicConfig(
			filename = LOG_FILE_LOCATION
			, level = logging.INFO
			, format = LOG_FORMAT
			, filemode = 'a')
		self.LOGGER = logging.getLogger()

	def archivelog(self, filepath, filename, log_size_limit = 3000000):
		"""
			Archives physical logs when they exceed a given size.
		"""
		full_filepath = '{filepath}{filename}'.format(
			filepath=filepath, filename=filename)
		# Check if the file exists
		if os.path.isfile(full_filepath):
			size = os.path.getsize(full_filepath)
			# Check if the file is greater than a given size
			if size > log_size_limit:
				rand = uuid.uuid4()
				rand = str(rand)[:8]
				new_filepath = '{filepath}archive_{filename}_{rand}'.format(
					filepath=filepath
					, filename=filename
					, rand = rand)
				os.rename(full_filepath, new_filepath)
				log_msg = "Log file archived as {new_filepath}".format(
					new_filepath = new_filepath)
				self.multiLogger(log_msg, level=3)
			else:
				log_msg = 'File is smaller than the limit [ {size} / {log_size_limit} ]'.format(
					size = size
					,log_size_limit = log_size_limit)
				self.multiLogger(log_msg, level=1)
		else:
			# Make the file which was either not present or recently moved.
			with open(full_filepath,'a') as f:
				f.write('')

	def download_file(self, url, filedirectory):
		"""
			Downloads binary files. Accepts:
				string: url
				string: filedirectory
				returns the filepath of the created file
		"""
		local_filename = url.split('/')[-1]
		local_filepath = "{filedirectory}{local_filename}".format.format(
			filedirectory = filedirectory
			, local_filename = local_filename)
		r = requests.get(url, stream=True)
		with open(local_filepath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk:
					f.write(chunk)
					#f.flush() commented by recommendation from J.F.Sebastian
		return local_filepath


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
