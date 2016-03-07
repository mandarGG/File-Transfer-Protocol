#!/usr/bin/python
import socket, os, time, hashlib, sys, select
s = socket.socket()             
host = socket.gethostname()
port = 56000                    

s.connect((host, port))
s.send("Hello server!")

def receive_data():
	received = s.recv(1024)
	if not received or not len(received):
		return None
	else:
		return received

def receive_data_udp(filename, command):
	port = 9999
	sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock_udp.bind((host,port))
	addr = (host,port)
	buf = 1024

	f = open(filename + '_udp','wb')
	# Now send the command to listen for UDP
	s.send(command)
	# Listen for UDP packet from the server just after sending the command 
	data,addr = sock_udp.recvfrom(buf)
	try:
	    while(data):
	        f.write(data)
	        sock_udp.settimeout(2)
	        data,addr = sock_udp.recvfrom(buf)
	except socket.timeout:
	    f.close()
	    sock_udp.close()
	    print 'File Downloaded via UDP protocol'

def receive_data_tcp(filename):
	data = receive_data()
	with open(filename + '_tcp','wb') as f:
		f.write(data)
	print 'File Downloaded via TCP protocol'

def main():
	# Ask the user for the command and send it to the server
	command = raw_input("\nEnter the command: ")
	cmdlist = command.split()
	if not len(cmdlist):
		print "Please enter a valid command"
		return 1

	if cmdlist[0] == 'FileDownload':
		filename=cmdlist[2]
		if cmdlist[1] == 'UDP':
			data = receive_data_udp(filename, command)
		elif cmdlist[1] == 'TCP':
			s.send(command)
			data = receive_data_tcp(filename)
	else:
		s.send(command)
		data = receive_data()
	print data
	return 0

while True:
	main()