import mysql.connector
from Variables.databases import *
from Variables.config import logger, bot, admins
from Variables.error_messages import *


class DatabaseSQL:

	def __init__(self):
		'''Подключение в базе данных'''

		try:
			self.db = mysql.connector.connect(host=IP_DB,
											user=USER_DB,
											password=PASSWORD_DB,
											database=DATABASE)
			self.sql = self.db.cursor()

			print("[INFO] Success connect to MySQL")
			logger.info("Success connect to MySQL")
		except Exception as error:
			print("[ERROR] Connection to MySQL")
			logger.error(f"Connection to MySQL: {error}")


	def connect_db(self):
		'''Подключение в базе данных'''

		try:
			self.db = mysql.connector.connect(host=IP_DB,
											user=USER_DB,
											password=PASSWORD_DB,
											database=DATABASE)
			self.sql = self.db.cursor()

			return 1
		except Exception as error:
			logger.error(error)
			return error


	def create_tables(self):
		'''Создание таблицы в базе данных users'''

		try:
			self.sql.execute(f"""CREATE TABLE IF NOT EXISTS `{TABLE_USERS}` (
							id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
							user_id INTEGER NOT NULL,
							username VARCHAR(255),
							first_name VARCHAR(50) NOT NULL,
							last_name VARCHAR(100),
							status_unicalizing INTEGER DEFAULT 0,
							time DATETIME DEFAULT CURRENT_TIMESTAMP);""")
			self.db.commit()
			logger.info(f'Создана таблица {TABLE_USERS} в БД')

			return 1
		except Exception as error:
			logger.error(error)
			return error


	async def add_user(self, user: dict):
		"""Добавление пользователя в БД"""

		try:
			self.sql.execute(f"SELECT COUNT(*) FROM {TABLE_USERS} WHERE user_id={user['user_id']};")

			if self.sql.fetchone()[0] == 0:
				self.sql.execute(f"INSERT INTO {TABLE_USERS} (user_id, username, first_name, last_name) VALUES ({user['user_id']}, '{user['username']}', '{user['first_name']}', '{user['last_name']}');")
				self.db.commit()
				
				logger.info(f"[@{user['username']} {user['user_id']}] Создан новый пользователь")
				try:
					for i in admins:
						await bot.send_message(i, f"Новый пользователь @{user['username']} {user['user_id']}")
				except:
					pass

			return 1

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					await self.add_user(user)
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				await self.add_user(user)

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	async def change_status_unicalized(self, user_id: int, status: int):
		try:
			self.sql.execute(f"UPDATE {TABLE_USERS} SET status_unicalizing={status} WHERE user_id={user_id};")
			self.db.commit()

			return 1

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					await self.change_status_unicalized(user_id, status)
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				await self.change_status_unicalized(user_id, status)

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	async def get_count_stack(self):
		try:
			self.sql.execute(f"SELECT COUNT(*) FROM {TABLE_USERS} WHERE status_unicalizing=1;")
			count_ = self.sql.fetchone()

			if count != None:
				return count_[0]
			return count_

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					await self.get_count_stack()
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				await self.get_count_stack()

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	async def get_users_unicalizing(self):
		try:
			self.sql.execute(f"SELECT * FROM {TABLE_USERS} WHERE status_unicalizing=1;")
			users = self.sql.fetchall()

			return users

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					await self.get_users_unicalizing()
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				await self.get_users_unicalizing()

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error
