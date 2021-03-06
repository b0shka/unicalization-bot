import os
import logging
import telebot
from dotenv import load_dotenv


dotenv_path = '../.env'
load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN_TEST")
bot = telebot.TeleBot(TOKEN)

USER = "q"
PATH_TO_BOT = f"/home/{USER}/p/python/projects/unicalization"
PATH_TO_LOGS = f"{PATH_TO_BOT}/Logs/info.log"

PROGRAMMER_ID = int(os.getenv("PROGRAMMER_ID"))
MANAGER_ID = int(os.getenv("MANAGER_ID"))
admins = [PROGRAMMER_ID]


IP_DB = os.getenv("BOTS_CATEGORY_IP")
USER_DB = os.getenv("USER_DB")
PASSWORD_DB = os.getenv("BOTS_CATEGORY_PASSWORD")
DATABASE = os.getenv("DATABASE")

TABLE_USERS = 'users_unicalization'

ERROR_NOT_EXISTS_TABLE = 1146
ERROR_CONNECT_MYSQL = 2006
ERROR_LOST_CONNECTION_MYSQL = 2013


if not os.path.exists('Logs'):
	os.mkdir('Logs')

logging.basicConfig(filename=PATH_TO_LOGS, format = u'[%(levelname)s][%(asctime)s] %(funcName)s:%(lineno)s: %(message)s', level='INFO')
logger = logging.getLogger()