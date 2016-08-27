import socket
import sys

ircserver = "irc.inet.fi"
port = 6667

nick = "frisbotti"
username = "frisbot"
realname = "testing frisbot"
channel = "#frisbottest"

def main():
	irc = connect()
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
			print data
			if rankcheck(data) == 1:
				irc.send("MODE %s +o %s\r\n" % (channel, data))

def rankcheck(nick):
	if nick == "Maltoosi" or nick == "Glukoosi":
		return 1
	else:
		return 0
	
  
main()
