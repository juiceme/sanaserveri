import hashlib
import time
import random

from database import Database as db

class Session:
    def __init__(self):
        self.database = db()
        self.sessions = []

    def create(self):
        key = hashlib.sha1(str(time.time()+random.randrange(1000)).encode('utf-8')).hexdigest()
        self.sessions.append({ "key": key,
                               "score": 0,
                               "highscore": 0,
                               "found_words": [],
                               "used_vectors": [],
                               "username": "" })
        return { "key": key, "status": "OK" }

    def delete(self, session):
        self.sessions.remove(session)

    def get(self, key):
        for i in self.sessions:
            if i["key"] == key:
                return i
        return False

    def set_user(self, session, username):
        for i in self.sessions:
            if i["key"] != session["key"]:
                if i["username"] == username:
                    i["username"] = ""
        session["username"] = username

    def user_is_loggedin(self, session):
        if session["username"] != "":
            return True
        else:
            return False

    def user_is_admin(self, session):
        if session["username"] == "Admin":
            return True
        else:
            return False

    def clear_used_vectors(self):
        for i in self.sessions:
            i["used_vectors"] = []

    def load_highscores(self):
        for i in self.sessions:
            if self.user_is_loggedin(i):
                i["highscore"] = self.database.get_highscore(i["username"])

    def update_highscores(self):
        for i in self.sessions:
            if self.user_is_loggedin(i):
                print(i["score"])
                print(i["highscore"])
                if i["score"] > i["highscore"]:
                    self.database.update_highscore(i["username"], i["score"])

    def clear_scores(self):
        for i in self.sessions:
            i["score"] = 0

    def dump(self):
        return self.sessions
