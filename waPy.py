import datetime
from datetime import timedelta
import json
import os
import string
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
import operator
import collections
import numpy as np
import pandas as pd
from classifier import SentimentClassifier
import unidecode
import seaborn as sns
import sys
from tqdm import tqdm
import emoji
import multiprocessing

# TODO:
# positivism per day per yser
#   per hour,day, DOW
# most repeated words
# avgFollowingMsgs
# emojis
# multithreading
# export to txt
# export to json

class Message:

    def __init__(self, username, line, content, isMedia, time, pos):
        self.line = line
        self.username = username
        self.content = content
        self.isMedia = isMedia
        self.time = time
        self.pos = pos

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
    content = line[20:].split(':')[1].rstrip().lstrip()
    user = line[20:].split(':')[0]
    time = datetime.datetime(year, month, day, hour, minute)
    isMedia = False
    if content.find("Media omitted"):
        isMedia = True
    return Message(user, line, content, isMedia, time, 0)


#   read conversation file and create a list with its parsed msgs
def readFromFile(filepath):
    msgList = []
    with open(filepath, encoding="utf-8") as fp:
        line = fp.readline()
        while line:
            if len(line) > 0 and line.find("created group") == -1 and line.find("changed the subject") == -1 and line.find("security code changed") == -1 and line.find("You created group") == -1 and line.find("Messages to this group are now secured with") == -1 and line.find("You changed this group's icon") == -1 and line != "\n" and line.find("Messages to this chat and calls") == -1 and (line[0:2].isnumeric() and line[2] == "/") and line.find("added") == -1 and line.find("removed") == -1 and line.find("left") == -1 and line.find("changed the group description") == -1:
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
        # sets a limit of 100 words, just in case it is a pasted long text
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
def getWordsPerHour(userList, msgList):
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


def plotWordsPerHour(userList, msgList, filename):
    raw = getWordsPerHour(userList, msgList)
    df = pd.DataFrame(raw).sort_index()
    df.index.name = "Hour"
    df.plot(kind="bar", title="Total number of words per hour\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.legend(loc="upper left")
    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")
    plt.ylabel("Words")

    filename = "plots/" + filename + "/WordsPerHour.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# returns the sum of all words sorted by day of the week / user
def getWordsPerDOW(userList, msgList):
    nm = collections.defaultdict(lambda: collections.defaultdict(int))
    for msg in msgList:
        nm[msg.username][msg.time.weekday()] += len(msg.content.split())

    return nm


def plotAverageMessageLength(userList, msgList, filename):
    raw = getAvgMessageLength(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=[
                      "Avg len"]).sort_values(by="Avg len")
    df.index.name = "User"
    df.plot(kind="bar", title="Average message length\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")", legend=False)

    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")
    plt.ylabel("Words per message")

    filename = "plots/" + filename + "/avgMessageLength.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


def getWordsPerDayPerUser(userList, msgList):
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
def getWordsPerUser(userList, msgList):
    avl = collections.defaultdict(int)
    for msg in msgList:
        avl[msg.username] += len(msg.content.split())
    return collections.OrderedDict(sorted(avl.items(), key=operator.itemgetter(1)))


# plots a the words per day of conversation, from start to finish
def plotWordsPerDayPerUser(userList, msgList, filename):
    days = getDaysLong(msgList)
    if days < 10:
        msaWindow1 = days
    elif days >= 10 and days < 30:
        msaWindow1 = 5
    else:
        msaWindow1 = 7
    raw = getWordsPerDayPerUser(userList, msgList)
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))
    ax1.set_title("Original data")
    df = pd.DataFrame(raw).sort_index()
    df.plot(ax=ax1, rot=25)
    ax1.grid()

    fig.suptitle("Words per day of conversation\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    ax2.set_title("Rolling " + str(msaWindow1) + "-day mean")

    df.rolling(msaWindow1).mean().plot(ax=ax2, rot=25)
    ax2.grid()

    filename = "plots/" + filename + "/WordsPerDayPerUser.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# plots the total number of words per user in pie format
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
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# plots the total number of words per user in bar format
def plotWordsPerUserBar(userList, msgList, filename):
    raw = getWordsPerUser(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=["Times"])
    df.plot(kind="bar", title="Total number of words\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")", legend=False)
    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")

    filename = "plots/" + filename + "/WordsPerUser.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# plots the total number of messages a user has sent
def plotMessagesPerUser(userList, msgList, filename):
    raw = getMessagesPerUser(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=[
                      "Messages"]).sort_values(by="Messages")

    df.plot(kind="bar", title="Number of messages.\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")", legend=False)

    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")
    plt.ylabel("Messages")
    plt.xlabel("User")

    filename = "plots/" + filename + "/MessagesPerUser.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
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


# plots the times a user has double texted
def plotDoubleTextTimes(userList, msgList, lowerBound, upperBound, filename):
    minHour = lowerBound/60
    maxHour = upperBound/60
    raw = getDoubleTextTimes(userList, msgList, lowerBound, upperBound)
    df = pd.DataFrame(raw.values(), index=raw.keys(), columns=[
                      "Times"]).sort_values(by="Times")
    df.plot(kind="bar", title="Double texts. " + str(minHour) + "h <= t <= " + str(maxHour) + " h\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")", legend=False)

    plt.xticks(rotation=45)
    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")
    plt.ylabel("Double text times")
    plt.xlabel("User")

    # save panda dataframe
    filename = "plots/" + filename + "/DoubleTextTimes.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# returns the response time per minutes per user
def getResponseTimePerMinutes(userList, msgList):
    avl = collections.defaultdict(lambda: collections.defaultdict(int))

    for i in range(len(msgList)):
        if msgList[i].username != msgList[i-1].username:
            # response
            dif = (msgList[i].time - msgList[i-1].time).total_seconds()/60
            avl[msgList[i].username][5] += 1
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
            elif dif > 120 and dif <= 180:
                avl[msgList[i].username][180] += 1
            elif dif > 180 and dif <= 240:
                avl[msgList[i].username][240] += 1
            else:
                avl[msgList[i].username][241] += 1

    return avl


# plots the response time of every user
def plotResponseTimePerMinutes(userList, msgList, filename):
    raw = getResponseTimePerMinutes(userList, msgList)
    df = pd.DataFrame(raw).sort_index()
    df.rename(index={5: "<=5", 15: "<=15", 30: "<=30",
                     60: "<=60", 120: "<=120", 120: "<=120", 180: "<=180", 240: "<=240", 241: ">240"}, inplace=True)
    df.plot(title="Response time per time period\nDuration: " +
            str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")
    plt.xlabel("Minutes")
    plt.ylabel("Number of responses")
    plt.legend(loc="upper left")
    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")

    filename = "plots/" + filename + "/ResponseTime.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# plots the total number of words per DOW per user
def plotWordsPerDOW(userList, msgList, filename):
    raw = getWordsPerDOW(userList, msgList)
    df = pd.DataFrame(raw).sort_index()
    df.rename(index={0: "Mon", 1: "Tue", 2: "Wed",
                     3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}, inplace=True)
    df.index.name = "Day of week"
    df.plot(kind="bar", title="Total number of words per day of week\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    plt.legend(loc="upper left")
    plt.rc("grid", linestyle="--")
    plt.grid(axis="y")
    plt.ylabel("Number of words")

    # save panda dataframe
    filename = "plots/" + filename + "/WordsPerDow.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


def getAvgPositivism(userList, msgList):
    avl = collections.defaultdict(float)
    nMessages = getNumberMessages(userList, msgList, "text")
    for msg in msgList:
        avl[msg.username] += msg.pos
    for k in avl.keys():
        avl[k] /= nMessages[k]
    return avl


def plotAvgPositivism(userList, msgList, filename):
    raw = getAvgPositivism(userList, msgList)
    df = pd.DataFrame(raw.values(), index=raw.keys(),
                      columns=["Avg positivism"])
    df.plot(kind="bar", title="Average positivism per user (0-1).\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")", legend=False)
    plt.rc("grid", linestyle="--")

    plt.grid(axis="y")
    plt.ylabel("Positivism")
    plt.xlabel("User")

    print("***********************")
    filename = "plots/" + filename + "/AvgPositivism.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


def getMessagesPerDayPerUser(userList, msgList):
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
        avl[msg.username][msg.time.date()] += 1

    return avl


def getPositivismPerDay(userList, msgList):
    avl = {}
    msgCount = getMessagesPerDayPerUser(userList, msgList)

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
        avl[msg.username][msg.time.date()] += msg.pos

    for u in avl.keys():
        for d in avl[u].keys():
            try:
                avl[u][d] /= msgCount[u][d]
            except ZeroDivisionError:
                avl[u][d] = None

    return avl


# plots the positivism per day of conversation and the moving mean
# msaWindow (int > 0) = the size of the mean window
def plotPositivismPerDay(userList, msgList, filename):
    raw = getPositivismPerDay(userList, msgList)
    days = getDaysLong(msgList)
    if days < 10:
        msaWindow1 = days
    elif days >= 10 and days < 30:
        msaWindow1 = 5
    else:
        msaWindow1 = 7

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))
    ax1.set_title("Original data")

    df = pd.DataFrame(raw).sort_index()
    ax1.grid(axis="y")

    df.plot(ax=ax1, rot=25)
    ax1.grid()
    fig.suptitle("Positivism per day of conversation\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    ax2.set_title("Rolling " + str(msaWindow1) + "-day mean")
    df.rolling(msaWindow1).mean().plot(ax=ax2, rot=25)
    ax2.grid()
    filename = "plots/" + filename + "/PositivismPerDay.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# takes the msgList and calculates the positiveness of its content
def posClassify(msgList):
    clf = SentimentClassifier()
    for i in tqdm(range(len(msgList))):
        if msgList[i].content.find("omitted") == -1:
            msgList[i].pos = clf.predict(msgList[i].content)


# divides the msg array in cpu-1 parts, and each part is treated by a thread, then the arrays are merged
def posClassifyConcurrent(msgList):
    #TODO: create semaphores
    cores = multiprocessing.cpu_count()-1
    #TODO: create threads with id, and each calls treat with the id and the part of the array correspondent
    # this function waits for all semaphores to finish, and then merges the arrays



# takes a part of the array, and classifies it, saves it into pos, and returns it
def treat(id, first, last, msgList, sem):
    pos = []
    clf = SentimentClassifier()
    for i in range(first, last):
        pos.append(clf.predict(msgList[i].content))
    
    #unlock semaphore[id]
    return pos
    

# plots a scatter plot about number of words / positivism
def plotRelWordsPos(userList, msgList, filename):
    rawWords = getWordsPerDayPerUser(userList, msgList)
    rawPos = getPositivismPerDay(userList, msgList)

    fig, ax = plt.subplots(nrows=1, ncols=len(userList), figsize=(15, 5))
    fig.suptitle("Relation between number of words and positivism\nDuration: " +
                 str(getDaysLong(msgList)) + " days (" + getFirstLastDateString(msgList) + ")")

    for i in range(len(userList)):
        ax[i].set_title(userList[i])
        xValues = list(rawWords[userList[i]].values())
        yValues = list(rawPos[userList[i]].values())
        df = pd.DataFrame(xValues, yValues, columns=["Words"])
        df = df.reset_index()

        sns.regplot(x="index", y="Words", data=df, ax=ax[i])
        ax[i].grid()
        ax[i].set_xlabel("Positiveness")
    filename = "plots/" + filename + "/relationWordsPositivism.png"
    print("Generating:\t ", filename)
    plt.savefig(filename, dpi=1400)
    print("Generated:\t ", filename)
    print("***********************")


# returns a dictionary with K = date and V = number of words in that date
def getTotalWordsPerDay(msgList):
    words = collections.defaultdict(int)
    count = 0
    for i in range(len(msgList)):
        if msgList[i].time.day != msgList[i-1].time.day:
            words[msgList[i-1].time] = count
            count = 0
        count += len(msgList[i].content.split())
    
    return words


# returns the more talked n days
def getMostTalkedDays(msgList, days):
    words = getTotalWordsPerDay(msgList)
    words = collections.OrderedDict(sorted(words.items(), key=operator.itemgetter(1), reverse=True)[:days])
    return dict(words)


# returns the days with the most positivism
def getMostPositiveDays(msgList, nDays):
    days = collections.defaultdict(float)
    count = 0
    suma = 0
    for i in range(len(msgList)):
        if msgList[i-1].time.day != msgList[i].time.day:
            days[msgList[i].time.day] = suma/count
            suma = 0
            count = 0
        count += 1
        suma += msgList[i].pos 
    days = dict(collections.OrderedDict(sorted(days.items(), key=operator.itemgetter(1), reverse=True)[:nDays]))

    return days
        
        



# -------------------------------------------- main --------------------------------------------
# convName = the name of the conversation, without .txt
# plotting (Boolean) = True for plotting the normal charts
# posPlotting (Boolean) = True for plotting the positiveness charts


def main(convName, plotting, posPlotting):
    print("\n\n------------------------ WAPY 1.0 -------------------------- ")
    if plotting:
        print("Normal plotting ENABLED")
    else:
        print("Normal plotting DISABLED")
    if posPlotting:
        print("Positivism plotting ENABLED")
    else:
        print("Positivism plotting DISABLED")
    start_time = datetime.datetime.now()
    print("Program starting at: %s" % start_time.time())
    print("***********************")
    print("Reading from file and parsing...")
    conversationFile = convName
    filename = conversationFile + ".txt"
    msgList = readFromFile(filename)
    userList = createUserList(msgList)

    print("***********************")

    # plots
    if not os.path.exists("plots"):
        os.mkdir("plots")
    if not os.path.exists("plots/" + conversationFile):
        os.mkdir("plots/" + conversationFile)
    

    # ---------------------- normal plotting part ----------------------
    if plotting:
        plotAverageMessageLength(userList, msgList, conversationFile)
        plotMessagesPerUser(userList, msgList, conversationFile)
        plotWordsPerUserBar(userList, msgList, conversationFile)
        plotWordsPerDayPerUser(userList, msgList, conversationFile)
        plotWordsPerDOW(userList, msgList, conversationFile)
        plotWordsPerHour(userList, msgList, conversationFile)
        plotDoubleTextTimes(userList, msgList, 15, 1440, conversationFile)
        plotResponseTimePerMinutes(userList, msgList, conversationFile)

    # --------------------- positivism plotting part ----------------------
    if posPlotting:
        print("Positivism processing")
        posClassify(msgList)
        plotAvgPositivism(userList, msgList, conversationFile)
        plotPositivismPerDay(userList, msgList, conversationFile)
        plotRelWordsPos(userList, msgList, conversationFile)

    print(getMostPositiveDays(msgList, 5))

    print("\n\n------- ELAPSED TIME: %s minutes %s seconds -------" % (round((datetime.datetime.now() -
                                                                              start_time).total_seconds()/60), round((datetime.datetime.now()-start_time).total_seconds() % 60)))


main("cande", False, True)
