import mysql.connector
from datetime import datetime
from Variables.config import *
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
							time DATETIME DEFAULT CURRENT_TIMESTAMP,
							file_id TEXT,
							status_using INTEGER DEFAULT 0,
							time_get_in_line DATETIME);""")
			self.db.commit()
			logger.info(f'Создана таблица {TABLE_USERS} в БД')

			return 1
		except Exception as error:
			logger.error(error)
			return error


	def add_user(self, user: dict):
		"""Добавление пользователя в БД"""

		try:
			self.sql.execute(f"SELECT COUNT(*) FROM {TABLE_USERS} WHERE user_id={user['user_id']};")

			if self.sql.fetchone()[0] == 0:
				self.sql.execute(f"INSERT INTO {TABLE_USERS} (user_id, username, first_name, last_name) VALUES ({user['user_id']}, '{user['username']}', '{user['first_name']}', '{user['last_name']}');")
				self.db.commit()
				
				logger.info(f"[@{user['username']} {user['user_id']}] Создан новый пользователь")
				try:
					for i in admins:
						bot.send_message(i, f"Новый пользователь @{user['username']} {user['user_id']}")
				except:
					pass

			return 1

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					self.add_user(user)
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.add_user(user)

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	def add_file_id(self, user_id: int, file_id: str):
		try:
			self.sql.execute(f"UPDATE {TABLE_USERS} SET file_id='{file_id}' WHERE user_id={user_id};")
			self.db.commit()

			return 1

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					self.add_file_id(user_id, file_id)
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.add_file_id(user_id, file_id)

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	def change_status_using(self, user_id: int, status: int):
		try:
			self.sql.execute(f"UPDATE {TABLE_USERS} SET status_using={status}, time_get_in_line='{datetime.now()}' WHERE user_id={user_id};")
			self.db.commit()

			return 1

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					self.change_status_using(user_id, status)
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.change_status_using(user_id, status)

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	def get_users_using(self):
		try:
			self.sql.execute(f"SELECT * FROM {TABLE_USERS} WHERE status_using=1 ORDER BY time_get_in_line;")
			users = self.sql.fetchall()

			return users

		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					self.get_users_using()
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.get_users_using()

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	def check_status_using(self, user_id):
		try:
			self.sql.execute(f"SELECT status_using FROM {TABLE_USERS} WHERE user_id={user_id};")
			status = self.sql.fetchone()

			if status != None:
				return status[0]
			return status
			
		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					self.check_status_using(user_id)
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.check_status_using(user_id)

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	def get_count_users(self):
		try:
			self.sql.execute(f"SELECT COUNT(*) FROM {TABLE_USERS};")
			count_users = self.sql.fetchone()

			self.sql.execute(f"SELECT COUNT(*) FROM {TABLE_USERS} WHERE file_id!='NULL';")
			count_used_users = self.sql.fetchone()

			self.sql.execute(f"SELECT COUNT(*) FROM {TABLE_USERS} WHERE DATE(time_get_in_line)='{datetime.now().date()}';")
			count_used_today_users = self.sql.fetchone()

			return count_users, count_used_users, count_used_today_users
			
		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					self.get_count_users()
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.get_count_users()

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error


	def get_id_users(self, whom):
		try:
			if whom == "mailing_all_users":
				self.sql.execute(f"SELECT user_id FROM {TABLE_USERS};")

			users = self.sql.fetchall()
			return users
		except mysql.connector.Error as error:
			if error.errno == ERROR_NOT_EXISTS_TABLE:
				result_create = self.create_tables()
				if result_create == 1:
					return []
				else:
					return result_create

			elif error.errno == ERROR_CONNECT_MYSQL:
				logger.error(f"Connection to MYSQL: {error}")
				return error

			elif error.errno == ERROR_LOST_CONNECTION_MYSQL:
				self.connect_db()
				self.get_id_users()

			else:
				logger.error(error)
				return error

		except Exception as error:
			logger.error(error)
			return error