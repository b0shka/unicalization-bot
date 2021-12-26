import time
from Variables.config import *
from Requests.functions import FunctionsBot
from Databases.database_sql import DatabaseSQL


class Unicalizing:

    def __init__(self):
        try:
            self.func = FunctionsBot()
            self.db_sql = DatabaseSQL()
        except Exception as error:
            logger.error(error)


    def uncalizing(self):
        try:
            while True:
                time.sleep(5)
                self.func.check_size_log()
                users = self.db_sql.get_users_using()
                
                if type(users) == list and len(users) > 0:
                    for user in users:
                        self.func.unicalization_video(user[6], user[1])
                        self.db_sql.change_status_using(user[1], 0)
        except Exception as error:
            logger.error(error)
            print(f"[ERROR] {error}")