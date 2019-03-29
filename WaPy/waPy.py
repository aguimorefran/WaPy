import datetime

class Message:
    def __init__(self, line, user, content, year, month, day, hour, minute):
        self.line = line
        self.user = user
        self.content = content
        self.time = datetime.datetime(year, month, day, hour, minute)
    def toString(self):
        return ("%s\n%s\n%s" %(self.user, self.content, self.time))

class User:
    def __init__(self, name):
        self.name = name
        self.msgs = []
        self.files = []
    def toString(self):
        return ("Name: %s, msgs: %d, files: %d" %(self.name, len(self.msgs), len(self.files)))

def addUser(username, userList):
    ok = False
    for u in userList:
        if username == u.name:
            ok = True
    if ok is False:
        userList.append(User(username))

