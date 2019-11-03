import datetime
import os
import string
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
import operator
import collections
import numpy as np


# TODO:
# emoji counter:
# most repeated emoji
# who sends the most emojis
# mostRelevantWord per DOW, hour, user
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


# removes emojis
def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')


#   Parses a line of message into its different fields
def parseMsg(input):
    # 012345678901234567890123456789
    # 10/10/2018, 19:33 - Lau: hola que tal
    # 10/10/2018, 19:34 - Fco: bien y tu

    line = deEmojify(input.rstrip())
    day = int(line[0:2])
    month = int(line[3:5])
    year = int(line[6:10])
    hour = int(line[12:14])
    minute = int(line[15:17])
    content = line[20:].split(':')[1]
    user = line[20:].split(':')[0]
    time = datetime.datetime(year, month, day, hour, minute)
    isMedia = False
    if content.find("Media omitted"):
        isMedia = True
    return Message(user, line, content, isMedia, time)


#   read conversation file and create a list with its parsed msgs
def readFromFile(filepath):
    msgList = []
    with open(filepath, encoding="utf-8") as fp:
        line = fp.readline()
        while line:
            if len(line) > 0 and line.find("You created group") == -1 and line.find("Messages to this group are now secured with") == -1 and line.find("You changed this group's icon") == -1 and line != "\n" and line.find("Messages to this chat and calls") == -1 and (line[0:2].isnumeric() and line[2] == "/") and line.find("added") == -1 and line.find("removed") == -1 and line.find("left") == -1 and line.find("changed the group description") == -1:
                # parse line to message
                # print(line)
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
    nm = dict.fromkeys(userList)
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username] += 1
    return nm


# messages per hour. mode = text / mode = media
def getMessagesPerHour(userList, msgList, mode):
    h = dict.fromkeys(range(24), 0)
    nm = dict.fromkeys(userList, h)
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username][msg.time.hour] += 1

    return nm


# average message length
def getAvgMessageLength(userList, msgList):
    avl = dict.fromkeys(userList, 0)
    msgPerUser = getMessagesPerUser(userList, msgList)
    for m in msgList:
        avl[m.username] += len(m.content.split())
    for k in avl.keys():
        avl[k] = round(avl[k] / msgPerUser[k], 2)
    return avl


# messages per user per conversation
def getMessagesPerUser(userList, msgList):
    avl = dict.fromkeys(userList, 0)
    for m in msgList:
        avl[m.username] += 1
    return dict(collections.OrderedDict(sorted(avl.items(), key=operator.itemgetter(1))))


# get the duration in days of the conversation
def getDaysLong(msgList):
    first = msgList[0].time
    last = msgList[len(msgList)-1].time
    return (last-first).days+1


# gets messages per day of week by user
def getMessagesPerDOW(userList, msgList, mode):
    h = dict.fromkeys(range(7), 0)
    nm = dict.fromkeys(userList, h)
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username][msg.time.weekday()] += 1

    return nm


# returns a dictionary of the sum of all words per hour of day / user
def getTotalWordsPerHour(userList, msgList):
    h = dict.fromkeys(range(24), 0)
    nm = dict.fromkeys(userList, h)
    for msg in msgList:
        nm[msg.username][msg.time.hour] += len(msg.content.split())

    return nm


# returns a string with the datetimes of the first and last day of the msgList
def getFirstLastDateString(msgList):
    return str(msgList[0].time.date()) + " - " + str(msgList[len(msgList)-1].time.date())


def plotTotalWordsPerHour(userList, messageList, filename):
    daysLong = getDaysLong(msgList)
    if daysLong == 0:
        daysLong = 1
    userData = []
    a = getTotalWordsPerHour(userList, msgList)
    for u in userList:
        userData.append(dict(a[u]))

    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', ]
    fig, ax = plt.subplots()
    ind = np.arange(24)
    width = 0.35
    i = 0
    for x in userData:
        ax.bar(ind + (i*width), x.values(), width,
               color=colors[i % len(colors)], label=userList[i])
        i += 1

    ax.set_title("Total number of words per hour\nDuration: " +
                 str(daysLong) + " days\n" + getFirstLastDateString(msgList))
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels([j for j in range(0, 24)])
    plt.xlabel("Hour")
    ax.autoscale_view()
    ax.legend()
    plt.grid(True)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "totalMessagesPerHour.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


# returns the sum of all words sorted by day of the week / user
def getTotalWordsPerDOW(userList, msgList):
    h = dict.fromkeys(range(7), 0)
    nm = dict.fromkeys(userList, h)
    for msg in msgList:
        nm[msg.username][msg.time.weekday()] += len(msg.content.split())

    return nm


def plotTotalWordsPerDOW(userList, msgList, filename):
    daysLong = getDaysLong(msgList)
    if daysLong == 0:
        daysLong = 1
    userData = []
    a = getTotalWordsPerDOW(userList, msgList)
    for u in userList:
        userData.append(dict(a[u]))

    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', ]
    fig, ax = plt.subplots()
    ind = np.arange(7)
    width = 0.35
    i = 0
    for x in userData:
        ax.bar(ind + (i*width), x.values(), width,
               color=colors[i % len(colors)], label=userList[i])
        i += 1

    ax.set_title(
        "Average number of words per day of week\nDuration: " + str(daysLong) + " days\n" + getFirstLastDateString(msgList))
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels(["Monday", "Tuesday", "Wednesday",
                        "Thursday", "Friday", "Saturday", "Sunday"])
    plt.xlabel("Day of week")
    plt.xticks(rotation=30)

    ax.autoscale_view()
    ax.legend()
    plt.grid(True)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "totalWordsPerDOW.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def plotAverageMessageLength(userList, msgList, filename):
    daysLong = getDaysLong(msgList)
    userData = []
    a = getAvgMessageLength(userList, msgList)
    for u in userList:
        userData.append(a[u])
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', ]
    fix, ax = plt.subplots()
    ind = np.arange(len(userList))
    width = 0.35

    ax.bar(ind, userData, width, color=colors)
    ax.set_title("Average words per message\nDuration: " +
                 str(daysLong) + " days\n" + getFirstLastDateString(msgList))
    ax.set_xticks(ind)
    ax.set_xticklabels([userList[j] for j in range(len(userList))])
    plt.xlabel("User")
    ax.autoscale_view()
    plt.grid(True)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "avgWordsPerMessage.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def getMonthTicks(msgList):
    months = []
    for msg in msgList:
        m = str(msg.time.month) + "-" + str(msg.time.year)
        if m not in months:
            months.append(m)
    return months


def getTotalWordsPerDayPerUser(userList, msgList):
    daysLong = getDaysLong(msgList)
    h = dict.fromkeys(range(daysLong), 0)
    avl = dict.fromkeys(userList, h)

    dayCount = 0
    for i in range(len(msgList)-1):
        if msgList[i+1].time.date() > msgList[i].time.date():
            dayCount += 1
        if dayCount != daysLong:
            avl[msgList[i].username][dayCount] += len(
                msgList[i].content.split())

    return avl


# returns a list of the datetimes of all the days in the msgList
def getDaysList(msgList):
    dates = []
    i = 0
    dates.append(str(msgList[0].time.date()))
    for i in range(len(msgList)):
        if (msgList[i-1].time.day < msgList[i].time.day):
            dates.append(str(msgList[i].time.date()))
    return dates


# returns a dictionary with the percentage of words by user
def getWordPercentage(userList, msgList):
    avl = dict.fromkeys(userList, 0)
    total = 0
    for msg in msgList:
        avl[msg.username] += len(msg.content.split())
        total += len(msg.content.split())
    for k in avl.keys():
        avl[k] = round((avl[k]/total)*100, 2)
    return avl


# returns a dictionary the total words said by each user
def getTotalWords(userList, msgList):
    avl = {}
    for u in userList:
        if u not in avl.keys():
            avl[u] = 0
    for msg in msgList:
        avl[msg.username] += len(msg.content.split())
    return dict(collections.OrderedDict(sorted(avl.items(), key=operator.itemgetter(1))))


def plotTotalWordsPerDayPerUser(userList, msgList, filename):
    # FIXME: fix days
    nMonts = len(getMonthTicks(msgList))
    daysLong = getDaysLong(msgList)
    daysList = getDaysList(msgList)
    dif = abs(daysLong - len(daysList))

    if daysLong == 0:
        daysLong = 1
    userData = []
    a = getTotalWordsPerDayPerUser(userList, msgList)
    for u in userList:
        userData.append(dict(a[u]))
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', ]
    width = 0.35
    ind = np.arange(len(daysList))
    fig, ax = plt.subplots()

    i = 0
    for x in userData:
        valores = list(x.values())
        if len(daysList) > len(x.values()):
            daysList = daysList[:len(daysList)-dif]
        elif len(x.values()) > len(daysList):
            valores = valores[:len(valores)-dif]
        ax.bar(ind + (i*width), valores, width,
               color=colors[i % len(colors)], label=userList[i])
        i += 1
    ax.set_title(
        "Words per day\nDuration: " + str(len(daysList)) + " days\n" + getFirstLastDateString(msgList))
    plt.xlabel("Day")
    plt.ylabel("Words")

    # ticks
    nTicks = 10
    indTick = np.arange(0, len(daysList), nTicks)
    tickLabels = [daysList[i] for i in indTick]
    ax.set_xticks(indTick)
    ax.set_xticklabels(tickLabels)
    plt.grid(True)
    ax.legend()

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "totalWordsPerDayPerUser.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def plotTotalWordPercentagePie(userList, msgList, filename):
    daysLong = getDaysLong(msgList)
    percentageList = getWordPercentage(userList, msgList)
    labels = userList
    sizes = []
    for x in percentageList:
        sizes.append(percentageList[x])
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
    ax.axis("equal")
    ax.set_title("Percentage of words per user\nDuration: " +
                 str(daysLong) + " days\n" + getFirstLastDateString(msgList))
    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "TotalWordPercentage.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def plotTotalWordsBar(userList, msgList, filename):
    daysLong = getDaysLong
    wordTotal = getTotalWords(userList, msgList)
    users = list(wordTotal.keys())
    values = list(wordTotal.values())

    ind = np.arange(len(userList))
    width = 0.35
    fig, ax = plt.subplots()
    ax.barh(ind, values, width, align="center")
    ax.set_title("Number of words per user\nDuration: " +
                 str(daysLong(msgList)) + " days\n" + getFirstLastDateString(msgList))
    ax.grid()
    ax.set_yticks(ind)
    ax.set_yticklabels(users)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "TotalWordPerUser.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def plotMessagesPerUser(userList, msgList, filename):
    daysLong = getDaysLong
    msgTotal = getMessagesPerUser(userList, msgList)
    users = list(msgTotal.keys())
    values = list(msgTotal.values())

    ind = np.arange(len(userList))
    width = 0.35
    fig, ax = plt.subplots()
    ax.barh(ind, values, width, align="center")
    ax.set_title("Number of messages per user\nDuration: " +
                 str(daysLong(msgList)) + " days\n" + getFirstLastDateString(msgList))
    ax.grid()
    ax.set_yticks(ind)
    ax.set_yticklabels(users)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "TotalWordPerUser.png"
    print("Generating ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


# returns the number of responses when response time is less than thresholdTime (minutes)
def getTotalResponses(userList, msgList, thresholdTime):
    #TODO:
    return None


# returns the average response time when time between messages is lower than 6 hours
def getAverageResponseTime(userList, msgList):
    #TODO:
    return None
        


# main
conversationFile = "juanma"
filename = "WaPy/" + conversationFile + ".txt"
msgList = readFromFile(filename)
userList = createUserList(msgList)
# plotAverageMessageLength(userList, msgList, conversationFile)
# plotMessagesPerUser(userList, msgList, conversationFile)
# plotTotalWordsBar(userList, msgList, conversationFile)
# plotTotalWordsPerDayPerUser(userList, msgList, conversationFile)
# plotTotalWordsPerDOW(userList, msgList, conversationFile)
# plotTotalWordsPerHour(userList, msgList, conversationFile)

print(getTotalResponses(userList, msgList, 1))