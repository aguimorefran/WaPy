import datetime
import string


class Message:

    def __init__(self, username, line, content, isMedia, time):
        self.line = line
        self.username = username
        self.content = content
        self.isMedia = isMedia
        self.time = time


class User:
    def __init__(self, username):
        self.username = username
        self.numberMessages = 0
        self.numberMedia = 0
        self.averageResponseTimeMinutes = 0
        self.timesDoubleTexted = 0


#   Parses a line of message into its different fields
def parseMsg(input):
    # 012345678901234567890123456789
    # 10/10/2018, 19:33 - Lau: hola que tal
    # 10/10/2018, 19:34 - Fco: bien y tu
    line = input.rstrip()
    day = int(line[0:2])
    month = int(line[3:5])
    year = int(line[6:10])
    hour = int(line[12:14])
    minute = int(line[15:17])
    content = line[20:].split(':')[1]
    user = line[20:].split(':')[0]
    time = datetime.datetime(year, month, day, hour, minute)
    isMedia = False
    if content.find("Media omitted"): isMedia = True
    return Message(user, line, content, isMedia, time)

#   read conversation file and create a list with its parsed msgs


def readFromFile(filepath):
    msgList = []
    with open(filepath, encoding="utf-8") as fp:
        line = fp.readline()
        while line:
            if len(line) > 0 and line != "\n" and line.find("Messages to this chat and calls") == -1:
                # parse line to message
                msg = parseMsg(line)
                msgList.append(msg)
            line = fp.readline()
    fp.close()
    return msgList


def isUserAdded(userList, username):
    for u in userList:
        if u.username == username:
            return True
    return False


# creates a list of user objects
def createUserList(msgList):
    userList = []
    for msg in msgList:
        if not isUserAdded(userList, msg.username):
            userList.append(User(msg.username))
    return userList


# mode = text (counts only text messages) / mode = media (counts only media messages)
def numberMessages(userList, msgList, mode):
    nm = {}
    for u in userList:
        if u not in nm.keys(): nm[u.username] = 0
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>")) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username] += 1
    return nm

msgList = readFromFile("WaPy/Cb.txt")
userList = createUserList(msgList)
numberMessagesMedia = numberMessages(userList, msgList, "text")
numerMessagesMedia = numberMessages(userList, msgList, "media")
print(numberMessagesMedia)
print(numerMessagesMedia)