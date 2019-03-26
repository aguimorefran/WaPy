import datetime
# waPy.py
# Takes a txt WhatsApp converastion and displays relevant data


class Message:
    # 08/03/2019, 17:19 - Fco: Hi
    line = ""
    timeStamp = None
    author = ""
    content = ""

    def processMessage(self, input):
        self.line = input
        day = input[0:2]
        month = input[3:5]
        year = input[6:10]
        hour = input[12:14]
        minute = input[15:17]

        # timeStamp = 

        print("--")
        print("Day '%s'" %(day))
        print("Month: '%s'" %(month))
        print("Year: '%s'" %(year))
        print("Hour: '%s'" %(hour))
        print("Minute: '%s'" %(minute))


msgList = []
count = 0

filepath = "WaPy/conver1.txt"
with open(filepath, encoding="utf8") as fp:
    line = fp.readline()
    while line:
        msg = Message()
        msg.processMessage(line)
        msgList.append(msg)


        line = fp.readline()
        count += 1
