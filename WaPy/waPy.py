import datetime
from datetime import timedelta
import os
import string
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
import operator
import collections
import numpy as np
import pandas as pd


# TODO:
# separete folder for every conversation
# responseTime
# mostRelevantWord per DOW, hour, user
# avgFollowingMsgs
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
            if len(line) > 0 and line.find("changed the subject") == -1 and line.find("security code changed") == -1 and line.find("You created group") == -1 and line.find("Messages to this group are now secured with") == -1 and line.find("You changed this group's icon") == -1 and line != "\n" and line.find("Messages to this chat and calls") == -1 and (line[0:2].isnumeric() and line[2] == "/") and line.find("added") == -1 and line.find("removed") == -1 and line.find("left") == -1 and line.find("changed the group description") == -1:
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
    nm = collections.defaultdict(int)
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username] += 1
    return nm


# messages per hour. mode = text / mode = media
def getMessagesPerHour(userList, msgList, mode):

    nm = collections.defaultdict(lambda: collections.defaultdict(int))
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username][msg.time.hour] += 1

    return nm


# average message length
def getAvgMessageLength(userList, msgList):
    avl = collections.defaultdict(int)
    msgPerUser = getMessagesPerUser(userList, msgList)
    for m in msgList:
        avl[m.username] += len(m.content.split())
    for k in avl.keys():
        avl[k] = round(avl[k] / msgPerUser[k], 2)
    return avl


# messages per user per conversation
def getMessagesPerUser(userList, msgList):
    avl = collections.defaultdict(int)
    for m in msgList:
        avl[m.username] += 1
    return avl


# get the duration in days of the conversation
def getDaysLong(msgList):
    first = msgList[0].time
    last = msgList[len(msgList)-1].time
    return (last-first).days+1


# gets messages per day of week by user
def getMessagesPerDOW(userList, msgList, mode):
    nm = collections.defaultdict(lambda: collections.defaultdict(int))
    for msg in msgList:
        if (mode == "text" and msg.content.find("<Media omitted>") == -1) or (mode == "media" and msg.content.find("<Media omitted>") != -1):
            nm[msg.username][msg.time.weekday()] += 1

    return nm


# returns a dictionary of the sum of all words per hour of day / user
def getTotalWordsPerHour(userList, msgList):
    nm = {}
    for u in userList:
        if u not in nm.keys():
            h = {}
            for i in range(0, 24):
                h[i] = 0
            nm[u] = h
    for msg in msgList:
        nm[msg.username][msg.time.hour] += len(msg.content.split())

    return nm


# returns a string with the datetimes of the first and last day of the msgList
def getFirstLastDateString(msgList):
    return str(msgList[0].time.date()) + " - " + str(msgList[len(msgList)-1].time.date())


def plotTotalWordsPerHour(userList, messageList, filename):
    raw = getTotalWordsPerHour(userList, msgList)
    df = pd.DataFrame(raw).sort_index()
    df.index.name = "Hour"
    df.plot(kind="bar", title="Total number of words per hour\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.legend(loc="upper left")
    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    plt.ylabel("Words")

    # save panda dataframe
    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "totalWordsPerHour.png"
    print("Generating: ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


# returns the sum of all words sorted by day of the week / user
def getTotalWordsPerDOW(userList, msgList):
    nm = collections.defaultdict(lambda: collections.defaultdict(int))
    for msg in msgList:
        nm[msg.username][msg.time.weekday()] += len(msg.content.split())

    return nm


def plotAverageMessageLength(userList, msgList, filename):
    raw = getAvgMessageLength(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=["Avg len"])
    df.index.name = "User"
    df.plot(kind="bar", title="Average message length\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.legend(loc="upper left")
    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    plt.ylabel("Words per message")

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "avgMessageLength.png"
    print("Generating: ", filename)
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
    avl = {}

    # get a list of the datetimes of days from first to last message, including empty days with no messages
    sdate = msgList[0].time.date()
    edate = msgList[len(msgList)-1].time.date()
    delta = edate-sdate
    days = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        days.append(day)

    for u in userList:
        if u not in avl.keys():
            h = {}
            for d in days:
                h[d] = 0
            avl[u] = h

    for msg in msgList:
        avl[msg.username][msg.time.date()] += len(msg.content.split())

    return avl


# returns a list of the datetimes of all the days in the msgList
def getDaysList(msgList):
    dates = []
    i = 0
    dates.append(msgList[0].time.date())
    for i in range(len(msgList)):
        if (msgList[i-1].time.day != msgList[i].time.day):
            dates.append(msgList[i].time.date())
    return dates


# returns a dictionary with the percentage of words by user
def getWordPercentage(userList, msgList):
    avl = collections.defaultdict(int)
    total = 0
    for msg in msgList:
        avl[msg.username] += len(msg.content.split())
        total += len(msg.content.split())
    for k in avl.keys():
        avl[k] = round((avl[k]/total)*100, 2)
    return avl


# returns a dictionary the total words said by each user
def getTotalWords(userList, msgList):
    avl = collections.defaultdict(int)
    for msg in msgList:
        avl[msg.username] += len(msg.content.split())
    return collections.OrderedDict(sorted(avl.items(), key=operator.itemgetter(1)))


def plotTotalWordsPerDayPerUser(userList, msgList, filename):
    raw = getTotalWordsPerDayPerUser(userList, msgList)    
    
    df = pd.DataFrame(raw).sort_index()
    df.plot(title="Number of words\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")
    
    #fit function
    #TODO
    
    plt.xlabel("Date")
    plt.ylabel("Number of words")
    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    
    # save panda dataframe
    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "TotalwordsPerDay.png"
    print("Generating: ", filename)
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
    print("Generating: ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def plotTotalWordsBar(userList, msgList, filename):
    raw = getTotalWords(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=["Times"])
    df.plot(kind="bar", title="Total number of words\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")
    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "TotalWordPerUser.png"
    print("Generating: ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def plotMessagesPerUser(userList, msgList, filename):
    raw = getMessagesPerUser(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=["Messages"])

    df.plot(kind="bar", title="Number of messages.\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    plt.ylabel("Messages")
    plt.xlabel("User")

    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "TotalmessagesPerUser.png"
    print("Generating: ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


# returns the times a user has double texted when x minutes have passed and x>lowerBound and x<upperBound
def getDoubleTextTimes(userList, msgList, lowerBound, upperBound):
    avl = collections.defaultdict(lambda: 0)
    for i in range(len(msgList)):
        if msgList[i].username == msgList[i-1].username:
            dif = (msgList[i].time - msgList[i-1].time).total_seconds()/60
            if dif >= lowerBound and dif <= upperBound:
                avl[msgList[i].username] += 1
    return avl


def plotTimesDoubleTexted(userList, msgList, lowerBound, upperBound, filename):
    minHour = lowerBound/60
    maxHour = upperBound/60
    raw = getDoubleTextTimes(userList, msgList, lowerBound, upperBound)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=["Times"])
    df.plot(kind="bar", title="Double texts. " + str(minHour) + "h <= t <= " + str(maxHour) + " h\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    plt.ylabel("Double text times")

    # save panda dataframe
    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "timesDoubleText.png"
    print("Generating: ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


def getResponseTime(userList, msgList):
    avl = collections.defaultdict(lambda: collections.defaultdict(int))

    for i in range(len(msgList)):
        if msgList[i].username != msgList[i-1].username:
            # response
            dif = (msgList[i].time - msgList[i-1].time).total_seconds()/60
            if dif > 0 and dif <= 5:
                avl[msgList[i].username][5] += 1
            elif dif > 5 and dif <= 15:
                avl[msgList[i].username][15] += 1
            elif dif > 15 and dif <= 30:
                avl[msgList[i].username][30] += 1
            elif dif > 30 and dif <= 60:
                avl[msgList[i].username][60] += 1
            elif dif > 60 and dif <= 120:
                avl[msgList[i].username][120] += 1
            else:
                avl[msgList[i].username]["inf"] += 1

    return avl


def plotTotalWordsPerDOW(userList, msgList, filename):
    raw = getTotalWordsPerDOW(userList, msgList)
    df = pd.DataFrame(raw).sort_index()
    df.rename(index={0: "Mon", 1: "Tue", 2: "Wed",
                     3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}, inplace=True)
    df.index.name = "Day of week"
    df.plot(kind="bar", title="Total number of words per day of week\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.legend(loc="upper left")
    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--", color="black")
    plt.grid(axis="y")
    plt.ylabel("Number of words")

    # save panda dataframe
    if not os.path.exists("plots"):
        os.mkdir("plots")
    filename = "plots/" + filename + "totalWordsPerDOW.png"
    print("Generating: ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated: ", filename)
    print("***********************")


# main
conversationFile = "lau"
filename = "WaPy/" + conversationFile + ".txt"
msgList = readFromFile(filename)
userList = createUserList(msgList)
plotAverageMessageLength(userList, msgList, conversationFile)
plotMessagesPerUser(userList, msgList, conversationFile)
plotTotalWordsBar(userList, msgList, conversationFile)
plotTotalWordsPerDayPerUser(userList, msgList, conversationFile)
plotTotalWordsPerDOW(userList, msgList, conversationFile)
plotTotalWordsPerHour(userList, msgList, conversationFile)
plotTimesDoubleTexted(userList, msgList, 15, 1440, conversationFile)
