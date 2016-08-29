import socket
import time
import urllib2
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

	irc.send("USER %s a a :%s\r\n" % (username, realname))
	irc.send("NICK %s\n" % nick)  
	irc.send("JOIN %s\n" % channel)
	return irc

def inputloop(irc):
	while True:
		data = irc.recv ( 4096 )
		print(data)
		if data.find ("PING") != -1:
			irc.send ( "PONG " + data.split() [ 1 ] + "\r\n" )
		elif data.find ("JOIN") != -1:
			data = data.split("!")
			data = data[0].lstrip(":")
			op(data, irc)
		elif data.find (" MODE %s +o %s" % (channel, nick)) != -1:
			names = namelist(irc)
			for name in names:
				op(name, irc)
		elif data.lower().find("!rank")!=-1:
			ndata = data.split(" ")
			if ndata[-1] != ":!rank":
				name = ndata[-1]
			else:
				data = data.split("!")
				name = data[0].lstrip(":")
			print name
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
	irc.send("PRIVMSG %s :%s\r\n" %(channel, message))
	return ""

def namelist(irc):
	irc.send("NAMES %s\r\n" % channel)
	names = irc.recv ( 4096 )
	names = names.split(":")
	names = names[2].split(" ")
	names.pop()
	print names
	return names

def op(name, irc):
	if opcheck(name) == 1:
		irc.send("MODE %s +o %s\r\n" % (channel, name))

def rankedplayers():
	rankedplayers = []
	list = getdata("players")
	for item in list:
		if item["rank"] != "":
			rankedplayers.append(item["name"])
	return rankedplayers

def getdata(dtype):
	response = urllib2.urlopen("https://moetto.dy.fi/frisbeer/API/%s/?format=json" % dtype)
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
