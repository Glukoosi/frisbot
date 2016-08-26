import socket
import sys

ircserver = "irc.nebula.fi"
port = 6667

nick = "frisbot"
username = "frisbot"
realname = "testing frisbot"
channel = "#frisbottest"


irc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((ircserver, port))

print irc.recv( 4096 )
irc.send( "USER %s a a :%s" % (username, realname))
irc.send("NICK %s" % nick)   
irc.send("JOIN %s" % channel)

while True:
	data = irc.recv ( 4096 )
	print data
   	if data.find ("PING") != -1:
		irc.send ( "PONG" + data.split() [ 1 ] + '\r\n' )
