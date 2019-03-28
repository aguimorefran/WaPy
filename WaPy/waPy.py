import datetime
#   waPy.py
#   Takes a txt WhatsApp converastion and displays relevant data

#   Message class


class Message:
    #   08/03/2019, 17:19 - Fco: Hi
    line = ""
    time = datetime
    author = ""
    content = ""

    def processMessage(self, input):
        #   first check if the line is a message
        if input != '\n' and len(input) > 0 and (input[2] == '/' and input[5] == '/'):
            self.line = input.rstrip()
            day = int(self.line[0:2])
            month = int(self.line[3:5])
            year = int(self.line[6:10])
            hour = int(self.line[12:14])
            minute = int(self.line[15:17])
            self.time = datetime.datetime(year, month, day, hour, minute)
            self.author = self.line[20:].split(':')[0]
            # find second occurrence of ':'

#   Reads from file 'filepath'


def readFromFile(filepath):
    with open(filepath, encoding="utf8") as fp:
        line = fp.readline()
        while line:
            msg = Message()
            msg.processMessage(line)
            if(msg.line != ''):
                msgList.append(msg)
            line = fp.readline()

class Author:
    name = ""
    nMsgs = 0
    nFiles = 0
    
def createAuthors():
    for msg in msgList:
        ok = False
        for au in authorList:
            if au.name == msg.author:
                ok = True
        if not ok:
            a = Author()
            a.name = msg.author
            authorList.append(a)

def assignMsgs():
    # read msg list and add msgs to the Author.nMsg

filepath = "WaPy/conver1.txt"
msgList = []
authorList = []
msgPerAuthor = {}

#   read the file line by line, create the messages and store them in msgList
readFromFile(filepath)

#   create list of authors
createAuthors()
