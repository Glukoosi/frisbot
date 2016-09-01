import socket
from urllib.request import urlopen
import json

ircserver = "irc.inet.fi"
port = 6667

nick = "frisbotti"
username = "frisbot"
realname = "frisbot"
channel = "#frisbottest"


def main():
	irc = connect()
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
		data = data.split()
		print(data)
		if "PING" in data:
			irc.send ( "PONG {}\r\n".format(data[1]).encode('utf-8'))
		elif "JOIN" in data: 
			name = data[0].lstrip(":").split("!")
			op(name[0], irc)
		elif ":!rank" in data:
			if data[-2] == ":!rank":
				name = data[-1]
				say(playerrank(name), irc)
			elif data[-1] == ":!rank":
				name = data[0].lstrip(":").split("!")
				say(playerrank(name[0]), irc)
			else:
				say("Vain yksi argumentti, korvaa välilyönnit alaviivalla.", irc)
		elif ":!help" in data:
			say("komennot: !rank, !lastgame, !lastlastgame !defname", irc)
		elif ":!lastgame" in data:
			say(lastgame(-1), irc)
		elif ":!lastlastgame" in data:
			say(lastgame(-2), irc)
		elif ":!defname" in data;
			if data [-2] == ":defname":
				name = data[0].lstrip(":").split("!")
				defname(data[-1], name)
			else:
				say("Vain yksi argumentti, anna frisbeer clientin nimimerkki jonka haluat linkittää irc nimimerkkiin.", irc)
			
def opcheck(nick):
	operators = rankedplayers()
	for op in operators:
		if nick == op:
			return 1
	return 0

def say(message, irc):
	irc.send("PRIVMSG {} :{}\r\n".format(channel, message).encode('utf-8'))
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
