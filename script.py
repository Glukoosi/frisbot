import socket
import sys

ircserver = "irc.inet.fi"
port = 6667

nick = "frisbotti"
username = "frisbot"
realname = "testing frisbot"
channel = "#frisbottest"

operators = ["Glukoosi", "Maltoosi"]

def main():
	irc = connect()
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
		if data.find ("JOIN") != -1:
			data = data.split("!")
			data = data[0].lstrip(":")
			op(data, irc)
		if data.find (" MODE %s +o %s" % (channel, nick)) != -1:
			names = namelist(irc)
			for name in names:
				op(name, irc)

def rankcheck(nick):
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
	if rankcheck(name) == 1:
		irc.send("MODE %s +o %s\r\n" % (channel, name))

main()
