import mysql.connector as mariadb

class Database:
    def __init__(self):
        self.db_connection = mariadb.connect(user='sanaserveri',
                                             password='54n453rv3r1',
                                             database='sanaserveri',
                                             host='toosa')
        self.cursor = self.db_connection.cursor()

    def login(self, username, password, session):
        try:
            self.cursor.execute("select password from users where username like %s", (username,))
            records = self.cursor.fetchall()
            if self.cursor.rowcount == 0:
                self.cursor.execute("insert into users (username, password, session) values (%s,%s,%s)",
                                    (username, password, session))
                self.db_connection.commit()
                return True
            else:
                if records[0][0] == password:
                    self.cursor.execute("update users set session=%s where username=%s",
                                        (session, username))
                    self.db_connection.commit()
                    return True
            return False
        except mariadb.Error as error:
            print("Error: {}".format(error))
            return False

    def logout(self, session):
        try:
            self.cursor.execute("select id from users where session like %s", (session,))
            records = self.cursor.fetchall()
            if self.cursor.rowcount == 0:
                return False
            else:
                self.cursor.execute("update users set session=%s where session=%s", ("", session))
                self.db_connection.commit()
                return True
        except mariadb.Error as error:
            print("Error: {}".format(error))
            return False

    def update_highscore(self, user, score):
        try:
            self.cursor.execute("select id from highscores where username like %s", (user,))
            records = self.cursor.fetchall()
            if self.cursor.rowcount == 0:
                self.cursor.execute("insert into highscores (username, score) values (%s,%s)",
                                    (user, score))
                self.db_connection.commit()
            else:
                self.cursor.execute("update highscores set score=%s where username=%s",
                                    (score, user))
                self.db_connection.commit()
        except mariadb.Error as error:
            print("Error: {}".format(error))
