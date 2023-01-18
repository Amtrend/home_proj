import mysql.connector
from main_variables import logger, USER, PASSWORD, HOST, DATABASE


class WorkDb:
    def __init__(self, user=USER, password=PASSWORD, host=HOST, database=DATABASE):
        self.db_user = user
        self.db_password = password
        self.db_host = host
        self.db_base = database

    def connect_db(self):
        cnx = None
        try:
            cnx = mysql.connector.connect(user=self.db_user, password=self.db_password, host=self.db_host, database=self.db_base)
        except mysql.connector.Error as e:
            logger.debug(f"Ошибка при подключении к бд: {e}")
        return cnx

    def create_video_recording(self, title, path, start_record, created_at):
        cnx = self.connect_db()
        try:
            if cnx:
                cursor = cnx.cursor()
                cursor.execute(f"""
                    INSERT INTO camera_home_cameraentrancesavevideos (title, video, start_recording, created_at) VALUES (%s, %s, %s, %s);
                """, (title, path, start_record, created_at))
                cnx.commit()
        except mysql.connector.Error as e:
            logger.debug(f"Ошибка при создании записи с новым видео в бд: {e}")
        finally:
            if cnx:
                cnx.close()

    def delete_video_recording(self, name):
        cnx = self.connect_db()
        try:
            if cnx:
                cursor = cnx.cursor()
                cursor.execute(f"""
                    DELETE FROM camera_home_cameraentrancesavevideos WHERE title = %s;
                """, (name,))
                cnx.commit()
        except mysql.connector.Error as e:
            logger.debug(f"Ошибка при удалении первого видео из бд: {e}")
        finally:
            if cnx:
                cnx.close()
