import datetime
import os
import string
import matplotlib.pyplot as plt
import numpy as np


# TODO:
# plotTotalWordsPerWeekOfYear
# avgResponseTime
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
    nm = {}
    # initialize dictionary with keys = users
    for u in userList:
        if u not in nm.keys():
            nm[u] = 0
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


# average message length
def getAvgMessageLength(userList, msgList):
    avl = {}
    msgPerUser = getMessagesPerUser(userList, msgList)
    for u in userList:
        if u not in avl.keys():
            avl[u] = 0
    for m in msgList:
        avl[m.username] += len(m.content.split())
    for k in avl.keys():
        avl[k] = round(avl[k] / msgPerUser[k], 2)
    return avl


# messages per user per conversation
def getMessagesPerUser(userList, msgList):
    avl = {}
    for u in userList:
        if u not in avl.keys():
            avl[u] = 0
    for m in msgList:
        avl[m.username] += 1
    return avl


# get the duration in days of the conversation
def getDaysLong(msgList):
    first = msgList[0].time
    last = msgList[len(msgList)-1].time
    return (last-first).days


# saves to a file a plot of average text and media messages per hour per user
def plotAverageMessagesPerHour(userList, msgList, mode):
    daysLong = getDaysLong(msgList)
    if daysLong == 0:
        daysLong = 1
    userData = []
    msgsPerHour = getMessagesPerHour(userList, msgList, mode)
    for u in userList:
        userData.append(dict(msgsPerHour[u]))
    for d in userData:
        for k in d.keys():
            d[k] /= daysLong

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', ]
    fig, ax = plt.subplots()
    ind = np.arange(24)
    width = 0.35
    i = 0
    for x in userData:
        ax.bar(ind + (i*width), x.values(), width,
               color=colors[i % len(colors)], label=userList[i])
        i += 1

    ax.set_title("Average number of messages per hour")
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels([i for i in range(0, 24)])
    plt.xlabel("Hour")
    plt.xticks(rotation=45)
    ax.autoscale_view()
    ax.legend()

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/avg" + mode + "messagesPerHour.png"
    plt.savefig(filename)


# plots msgs per dow
def plotAverageMessagesPerDOW(userList, msgList, mode):
    daysLong = getDaysLong(msgList)
    if daysLong == 0:
        daysLong = 1
    userData = []
    msgPerDOW = getMessagesPerDOW(userList, msgList, mode)
    for u in userList:
        userData.append(dict(msgPerDOW[u]))
    for d in userData:
        for k in d.keys():
            d[k] /= 7

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', ]
    fig, ax = plt.subplots()
    ind = np.arange(7)
    width = 0.35
    i = 0
    for x in userData:
        ax.bar(ind + (i*width), x.values(), width,
               color=colors[i % len(colors)], label=userList[i])
        i += 1

    ax.set_title("Average number of messages per day of week")
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels(["Monday", "Tuesday", "Wednesday",
                        "Thursday", "Friday", "Saturday", "Sunday"])
    plt.xlabel("Day of week")
    plt.xticks(rotation=30)
    ax.autoscale_view()
    ax.legend()

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/avg" + mode + "messagesPerDOW.png"
    plt.savefig(filename)


def getMessagesPerDOW(userList, msgList, mode):
    nm = {}
    # initialize users
    for u in userList:
        if u not in nm.keys():
            h = {}
            for i in range(7):
                h[i] = 0
            nm[u] = h
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username][msg.time.weekday()] += 1

    return nm


def getAverageWordsPerHour(userList, msgList):
    nm = {}
    # initialize users
    for u in userList:
        if u not in nm.keys():
            h = {}
            for i in range(24):
                h[i] = 0
            nm[u] = h
    for msg in msgList:
        nm[msg.username][msg.time.hour] += len(msg.content.split())
    for u in nm:
        for h in nm[u]:
            nm[u][h] = round(nm[u][h] / 24, 2)

    return nm


def plotAverageWordsPerHour(userList, messageList):
    daysLong = getDaysLong(msgList)
    if daysLong == 0:
        daysLong = 1
    userData = []
    a = getAverageWordsPerHour(userList, msgList)
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

    ax.set_title("Average number of words per hour")
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels([i for i in range(0, 24)])
    plt.xlabel("Hour")
    ax.autoscale_view()
    ax.legend()

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/avgMessagesPerHour.png"
    plt.savefig(filename)


def getAvgWordsPerDOW(userList, msgList):
    nm = {}
    # initialize users
    for u in userList:
        if u not in nm.keys():
            h = {}
            for i in range(7):
                h[i] = 0
            nm[u] = h
    for msg in msgList:
        nm[msg.username][msg.time.weekday()] += len(msg.content.split())
    for u in nm:
        for h in nm[u]:
            nm[u][h] = round(nm[u][h] / (getDaysLong(msgList)/7), 2)

    return nm


def plotAverageWordsPerDOW(userList, msgList):
    daysLong = getDaysLong(msgList)
    if daysLong == 0:
        daysLong = 1
    userData = []
    a = getAvgWordsPerDOW(userList, msgList)
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

    ax.set_title("Average number of words per day of week")
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels(["Monday", "Tuesday", "Wednesday",
                        "Thursday", "Friday", "Saturday", "Sunday"])
    plt.xlabel("Day of week")
    plt.xticks(rotation=30)

    ax.autoscale_view()
    ax.legend()

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/avgWordsPerDOW.png"
    plt.savefig(filename)


def getWordsByWeek(userList, msgList):
    #TODO: terminar
    return None


# main
filename = "WaPy/lau.txt"
msgList = readFromFile(filename)
userList = createUserList(msgList)
plotAverageWordsPerHour(userList, msgList)
plotAverageWordsPerDOW(userList, msgList)
print(getWordsByWeek(userList, msgList))