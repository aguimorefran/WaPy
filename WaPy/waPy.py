import datetime
import string


# TODO:avgResponseTime
# avgFollowingMsgs
# timesDoubleTexted
# messages and media per DOW, hour, month


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


# creates a list of user objects
def createUserList(msgList):
    userList = []
    for msg in msgList: 
        if msg.username not in userList: 
            userList.append(msg.username)
    return userList


# mode = text (counts only text messages) / mode = media (counts only media messages)
def getNumberMessages(userList, msgList, mode):
    nm = {}
    # initialize dictionary with keys = users
    for u in userList:
        if u not in nm.keys(): nm[u] = 0
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username] += 1
    return nm


# messages per hour. mode = text / mode = media
def getMessagesPerHour(userList, msgList, mode):
    nm = {}
    # initialize users
    for u in userList:
        if u not in nm.keys():
            h = {}
            for i in range(24):
                h[i] = 0
            nm[u] = h
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username][msg.time.hour] += 1
    
    return nm


# main
msgList = readFromFile("WaPy/Cb.txt")
userList = createUserList(msgList)
textMessagesPerHour = getMessagesPerHour(userList, msgList, "text")
mediaMessagesPerHour = getMessagesPerHour(userList, msgList, "media")
print(textMessagesPerHour)