import datetime


class Message:
    def __init__(self, line, user, content, year, month, day, hour, minute):
        self.line = line
        self.user = user
        self.content = content
        self.time = datetime.datetime(year, month, day, hour, minute)

    def toString(self):
        return ("'%s'->'%s'\n'%s'" % (self.user, self.content, self.time))


class User:
    def __init__(self, name):
        self.name = name
        self.msgs = []
        self.files = []

    def toString(self):
        return ("Name: %s, msgs: %d, files: %d" % (self.name, len(self.msgs), len(self.files)))

#   Checks if user exists. If not, create and add it


def addUser(username, userList):
    ok = False
    for u in userList:
        if username == u.name:
            ok = True
    if ok is False:
        userList.append(User(username))

#   Parses a line of message into its different fields


def parseMsg(input):
    line = input.rstrip()
    day = int(line[0:2])
    month = int(line[3:5])
    year = int(line[6:10])
    hour = int(line[12:14])
    minute = int(line[15:17])
    content = line[20:].split(':')[1]
    user = line[20:].split(':')[0]
    return Message(line, user, content[1:], year, month, day, hour, minute)

#   read conversation file and create a list with its parsed msgs


def readFromFile(filepath, msgList):
    with open(filepath, encoding="utf8") as fp:
        line = fp.readline()
        while line:
            if len(line) > 0 and line != "\n":
                msgList.append(parseMsg(line))
            line = fp.readline()

#   creates a list of users from the msgList


def createUsers(msgList, userList):
    for msg in msgList:
        ok = False
        for u in userList:
            if u.name == msg.user:
                ok = True
        if not ok:
            userList.append(User(msg.user))

#   assigns every msg of msgList to a user


def assignMsgs(msgList, userList):
    for msg in msgList:
        for u in userList:
            if msg.user == u.name:
                if "omitted" in msg.content:
                    u.files.append(msg)
                else:
                    u.msgs.append(msg)
#   Takes a user. msg = True -> displays msgs list data, msg = False -> displays files list data
#   avg = True -> divides data by total num of msgs


def msgPerHour(user, msg, avg):
    hours = [0]*24
    if msg is True:
        for msg in user.msgs:
            hours[msg.time.hour] += 1
        if avg is True:
            return [x / len(user.msgs) for x in hours]
        else:
            return hours
    else:
        for fi in user.files:
            hours[fi.time.hour] += 1
        if avg is True:
            return [x / len(user.files) for x in hours]
        else:
            return hours


def msgPerDOW(user, msg, avg):
    DOW = [0]*7
    if msg is True:
        for msg in user.msgs:
            DOW[msg.time.weekday()] += 1
        if avg is True:
            return[x / len(user.msgs) for x in DOW]
        else:
            return DOW
    else:
        for msg in user.files:
            DOW[msg.time.weekday()] += 1
        if avg is True:
            return[x / len(user.files) for x in DOW]
        else:
            return DOW


def mostActiveDay(user):
    mad = {}
    max = 0
    acu = 0
    for i in range(len(user.msgs)-1):
        if user.msgs[i+1].time.day == user.msgs[i].time.day and user.msgs[i+1].time.month == user.msgs[i].time.month:
            acu = acu + 1
        elif acu > max:
            max = acu
            acu = 0
    mad[acu] = user.msgs[i].time.strftime('%d-%m-%Y')
    
    acu = 0
    for i in range(len(user.msgs)-1):
        if user.msgs[i+1].time.day == user.msgs[i].time.day and user.msgs[i+1].time.month == user.msgs[i].time.month:
            acu = acu + 1
        elif acu == max:
            mad[acu] = user.msgs[i].time.strftime('%d-%m-%Y')

    return mad

filepath = "WaPy/elena.txt"
msgList = []
userList = []

readFromFile(filepath, msgList)
createUsers(msgList, userList)
assignMsgs(msgList, userList)
