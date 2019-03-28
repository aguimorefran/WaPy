import datetime
#   waPy.py
#   Takes a txt WhatsApp converastion and displays relevant data

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
            day = int(line[0:2])
            month = int(line[3:5])
            year = int(line[6:10])
            hour = int(line[12:14])
            minute = int(line[15:17])
            self.time = datetime.datetime(year, month, day, hour, minute)
            self.author = line[20:].split(':')[0]
            # find second occurrence of ':'
            

msgList = []
authorList = []


#   read the file line by line, create the messages and store them in msgList
filepath = "WaPy/conver1.txt"
with open(filepath, encoding="utf8") as fp:
    line = fp.readline()
    while line:
        msg = Message()
        msg.processMessage(line)
        if(msg.line != ''):
            msgList.append(msg)
        line = fp.readline()
