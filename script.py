import socket
import time
from urllib.request import urlopen
import json

ircserver = "irc.inet.fi"
port = 6667

nick = "frisbot"
username = "frisbot"
realname = "frisbot"
channel = "#frisbottest"


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
		data = irc.recv ( 4096 ).decode('utf-8')
		print(data)
		if data.find ("PING") != -1:
			irc.send ( "PONG {}\r\n".format(data.split() [ 1 ]).encode('utf-8'))
		elif data.find ("JOIN") != -1:
			data = data.split("!")
			data = data[0].lstrip(":")
			op(data, irc)
		elif data.find (" MODE {} +o {}\r\n".format(channel, nick)) != -1:
			names = namelist(irc)
			for name in names:
				op(name, irc)
		elif data.lower().find("!rank")!=-1:
			ndata = data.split(" ")
			if ndata[-1] != ":!rank\r\n":
				name = ndata[-1].rstrip()
			else:
				data = data.split("!")
				name = data[0].lstrip(":")
			say(playerrank(name), irc)
		elif data.lower().find("!lastgame")!=-1:
			glist = getdata("games")
			plist = getdata("players")
			
			
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
	irc.send("NAMES {}\r\n".format(channel))
	names = irc.recv ( 4096 )
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
	return json.loads(myjson)

def playerrank(name):
	plist = getdata("players")
	for player in plist:
		if player["name"] == name:
			if player["rank"] == "":
				return "Mutta sinullahan ei ole rankkia."
			else:
				return player["rank"]
	return "lol noob"
				
			
main()
