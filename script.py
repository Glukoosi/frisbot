import socket
import time
from urllib.request import urlopen
import json

ircserver = "irc.inet.fi"
port = 6667

nick = "frisbot"
username = "frisbot"
realname = "frisbot"
channel = "#frisbeer"


def main():
	irc = connect()
	time.sleep(5)
	say("gibe op pls", irc)
	inputloop(irc)

def connect():
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	irc.connect((ircserver, port))

	irc.send("USER {} a a :{}\r\n".format(username, realname).encode('utf-8'))
	irc.send("NICK {}\n".format(nick).encode('utf-8'))  
	irc.send("JOIN {}\n".format(channel).encode('utf-8'))
	return irc

def inputloop(irc):
	while True:
		data = str(irc.recv(4096),"UTF-8", "replace")
		data = data.strip() + "\r\n"
		print(data)
		if data.find ("PING") != -1:
			irc.send ( "PONG {}\r\n".format(data.split() [ 1 ]).encode('utf-8'))
		elif data.find ("JOIN") != -1:
			data = data.split("!")
			data = data[0].lstrip(":")
			op(data, irc)
		elif data.find (" MODE {} +o {}".format(channel, nick)) != -1:
			names = namelist(irc)
			for name in names:
				op(name, irc)
		elif data.lower().find(":!rank ")!=-1 or data.lower().find(":!rank\r\n")!=-1:
			ndata = data.split()
			if ndata[-2] == ":!rank":
				name = ndata[-1].strip()
				say(playerrank(name), irc)
			elif ndata[-1] == ":!rank":
				data = data.split("!")
				name = data[0].lstrip(":")
				say(playerrank(name), irc)
			else:
				say("Vain yksi argumentti, korvaa välilyönnit alaviivalla.", irc)
		elif data.lower().find(":!help\r\n")!=-1:
			say("komennot: !rank, !lastgame, !lastlastgame", irc)
		elif data.lower().find(":!lastgame\r\n")!=-1:
			say(lastgame(-1), irc)
		elif data.lower().find(":!lastlastgame\r\n")!=-1:
			say(lastgame(-2), irc)
			
def opcheck(nick):
	operators = rankedplayers()
	for op in operators:
		if nick == op:
			return 1
	return 0

def say(message, irc):
	irc.send("PRIVMSG {} :{}\r\n".format(channel, message).encode('utf-8'))
	return ""

def namelist(irc):
	irc.send("NAMES {}\r\n".format(channel).encode('utf-8'))
	names = irc.recv ( 4096 ).decode('utf-8')
	names = names.split(":")
	names = names[2].split(" ")
	names.pop()
	print (names)
	return names

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
	response = urlopen("https://moetto.dy.fi/frisbeer/API/{}/?format=json".format(dtype))
	myjson = response.read()
	return json.loads(myjson.decode('utf-8'))

def playerrank(name):
	plist = getdata("players")
	for player in plist:
		if player["name"].replace(" ", "_") == name:
			if player["rank"] == "":
				return "Pelaajalla {} ei ole rankkia.".format(player["name"])
			else:
				return player["rank"]
	return "{} ei ole pelannut frisbeeriä :(".format(name)

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
				n+=1
	for iidee in glist[index]["team2"]:
		n = 0
		while 1:
			if plist[n]["id"] == iidee:
				data.append(plist[n]["name"])
				break
			else:
				n+=1
	data.append(glist[index]["team1_score"])
	data.append(glist[index]["team2_score"])
	return ("{0}  {1}, {2}, {3} vs. {4}, {5}, {6}  päättyi {7} - {8}".format(*data))
			
main()
