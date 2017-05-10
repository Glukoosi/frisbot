import socket
import time
import sys
from urllib.request import urlopen
import urllib.error
import json
from fuzzywuzzy import fuzz

ircserver = "irc.nebula.fi"
port = 6667

nick = "frisbot"
username = "frisbot"
realname = "frisbot"
channel = "#frisbeer"


class Message:

    def __init__(self, data):
        self.channel = ""
        self.sender = ""
        self.channel = ""
        self.msg = ""
        self.msgdata = [""]

        data = data.split()
        print(data)
        self.type = data[1]
        if data[0] == "PING" or "PING" in data:
            irc.send("PONG {}\r\n".format(data[1]).encode('utf-8'))
        if self.type == "JOIN":
            self.sender = data[0].lstrip(":").split("!")[0]
        if self.type == "PRIVMSG":
            self.sender = data[0].lstrip(":").split("!")[0]
            if data[2] == nick:
                self.channel = "query"
            elif self.sender == ircserver:
                self.channel = "msg from server"
            else:
                self.channel = data[2]
        self.msg = " ".join(data[3:])[1:]
        self.msgdata = data[3:]


def connect():
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((ircserver, port))

    irc.send("USER {} a a :{}\r\n".format(username, realname).encode('utf-8'))
    irc.send("NICK {}\n".format(nick).encode('utf-8'))
    irc.send("JOIN {}\n".format(channel).encode('utf-8'))

    return irc

def inputloop(irc):
    while True:
        m = Message(str(irc.recv(4096), "UTF-8", "replace"))
        print(m.msg)
        print(m.msgdata)

        if m.type == "JOIN":
            op(m.sender, irc)
        elif m.type == "PRIVMSG":
            recipient = m.channel
            if m.channel == "query":
                recipient = m.sender
            if m.msgdata[0] == ":!rank":
                if m.msgdata[-1] == ":!rank":
                    player = fuzzmach(m.sender)
                    say("Pelaajan {} rankki: {}".format(player, playerrank(player)), recipient, irc)
                elif m.msgdata[-2] == ":!rank":
                    player = fuzzmach(m.msgdata[1])
                    say("Pelaajan {} rankki: {}".format(player, playerrank(player)), recipient, irc)
                else:
                    say("Vain yksi argumentti, korvaa välilyönnit alaviivalla.", recipient, irc)
            if m.msgdata[0] == ":!op":
                names = namelist(irc)
                for name in names:
                    op(name, irc)
            if m.msgdata[0] == ":!help":
                say("komennot: !rank, !lastgame, !lastlastgame !op", recipient, irc)
            if m.msgdata[0] == ":!lastgame":
                say(lastgame(-1), recipient, irc)
            if m.msgdata[0] == ":!lastlastgame":
                say(lastgame(-2), recipient, irc)


def fuzzmach(name):
    players = getdata("players")
    for player in players:
        print(fuzz.ratio(player["name"], name))
        if fuzz.partial_ratio(player["name"], name) > 85:
            return player["name"]
    return name

def opcheck(nick):
    operators = rankedplayers()
    for op in operators:
        if nick == op:
            return 1
    return 0


def say(message, who, irc):
    irc.send("PRIVMSG {} :{}\r\n".format(who, message).encode('utf-8'))
    return ""


def op(name, irc):
    if opcheck(name) == 1:
        irc.send("MODE {} +o {}\r\n".format(channel, name).encode('utf-8'))


def rankedplayers():
    rankedplayers = []
    list = getdata("players")
    for item in list:
        if item["rank"] != "":
            rankedplayers.append(item["name"])
    return rankedplayers


def getdata(dtype):
    try: response = urlopen("https://rant.org/frisbeer/API/{}/?format=json".format(dtype))
    except urllib.error.URLError:
        say("Serveriin ei saatu yhteyttä, Runtu pls fix", channel, irc) 
        time.sleep(5)
        sys.exit(0)
    myjson = response.read()
    return json.loads(myjson.decode('utf-8'))


def playerrank(name):
    plist = getdata("players")
    for player in plist:
        if player["name"].replace(" ", "_") == name:
            if player["rank"] == "":
                return "ei ole :("
            else:
                return player["rank"]
    return "et ole edes ole pelannut tällä kaudella :("


def lastgame(index):
    plist = getdata("players")
    glist = getdata("games")
    data = []
    time = glist[index]["date"].split("T")
    data.append("{2}.{1}.{0}".format(*time[0].split("-")))
    for iidee in glist[index]["team1"]:
        n = 0
        while 1:
            if plist[n]["id"] == iidee:
                data.append(plist[n]["name"])
                break
            else:
                n += 1
    for iidee in glist[index]["team2"]:
        n = 0
        while 1:
            if plist[n]["id"] == iidee:
                data.append(plist[n]["name"])
                break
            else:
                n += 1
    data.append(glist[index]["team1_score"])
    data.append(glist[index]["team2_score"])
    return ("{0}  {1}, {2}, {3} vs. {4}, {5}, {6}  päättyi {7} - {8}".format(*data))

def namelist(irc):     
    irc.send("NAMES {}\r\n".format(channel).encode('utf-8'))        
    names = irc.recv ( 4096 ).decode('utf-8')       
    names = names.split(":")        
    names = names[2].split(" ")     
    names.pop()     
    print (names)       
    return names



if __name__ == "__main__":
    irc = connect()
    inputloop(irc)

