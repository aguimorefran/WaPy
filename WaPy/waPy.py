import datetime
import string


class Message:

    def __init__(self, user, line, content, time):
        self.line = line
        self.user = user
        self.content = content
        self.time = time


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
    return Message(user, line, content, time)

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

#TODO: create user class with msg/media per hour and DOW
#TODO: tener en cuenta dejarlo todo organizado en clases