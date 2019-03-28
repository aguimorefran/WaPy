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

            
filepath = "WaPy/conver1.txt"
msgList = []
authorList = []

#   read the file line by line, create the messages and store them in msgList
readFromFile(filepath)

#   get a list of the authors in the conversation
for msg in msgList:
    if msg.author not in authorList:
        authorList.append(msg.author)

