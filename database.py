import mysql.connector as mariadb

class Database:
    def __init__(self):
        self.db_connection = mariadb.connect(user='sanaserveri',
                                             password='54n453rv3r1',
                                             database='sanaserveri',
                                             host='toosa')
        self.cursor = self.db_connection.cursor()

    def update_highscore(self, user, score):
        try:
            self.cursor.execute("select id from highscores where username like %s", (user,))
            records = self.cursor.fetchall()
            if self.cursor.rowcount == 0:
                self.cursor.execute("insert into highscores (username, score) values (%s,%s)", (user, score))
                self.db_connection.commit()
            else:
                self.cursor.execute("update highscores set score=%s where username=%s ", (score, user))
                self.db_connection.commit()
        except mariadb.Error as error:
            print("Error: {}".format(error))
