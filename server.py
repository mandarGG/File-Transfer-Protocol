#!/usr/bin/python
import socket, os, time, hashlib,re
from socket import error as SocketError
import errno
from datetime import datetime, timedelta
from dateutil import parser
from subprocess import Popen, PIPE

portno = 56000
s = socket.socket()

# In case if the server got interrupted and still the port is in use
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

hostname = socket.gethostname()
s.bind((hostname, portno))
s.listen(5)

print 'Server running on port number',portno
status = 1 # status between client and server connection

def main():
	received_data = ''

	try:
		# Receive the data from the client
		received_data = conn.recv(1024)
	except SocketError as e:
		if e.errno != errno.ECONNRESET:
			print 'Unknown error occured'
			raise
		pass

	if not len(received_data):
		print 'Client side connection lost'
		return 1

	print 'Data received from client', str(received_data)
	cmdlist = received_data.split()
	print cmdlist
	if cmdlist[0] == 'IndexGet':
		if cmdlist[1] == 'shortlist':
			print 'Client asked for shortlisting'
			time1 = cmdlist[2]
			time2 = cmdlist[3]
			shortlisting_output = shortListing(time1, time2)
			print shortlisting_output
			conn.send(shortlisting_output)

		elif cmdlist[1] == 'longlist':
			print 'Client asked for longlisting'
			data = longListing()
			print data
			conn.send(data)
		elif cmdlist[1] == 'regex':
			print 'Client asked for regex'
			regex = cmdlist[2]
			data = reg_match(regex)
			print data
			conn.send(data)
		else:
			# No other functionality available other than above three
			conn.send("Unknown type for IndexGet function")

	elif cmdlist[0] == 'FileHash':
		
		if cmdlist[1] == 'verify':
			filename=cmdlist[2]
			try:
				mysum=md5(filename);
				print mysum
				last_time=last_modify(filename)
				print "Last modified timestamp:" ,last_time
				response=""
				response += "Checksum:"+str(mysum)+", Last modified:"+str(last_time)
				conn.send(response)
				return response
			except IOError as err:
				print "Error", str(err), "File with the name",str(filename),"not found."


		elif cmdlist[1] == 'checkall':
			files = [f for f in os.listdir('.') if os.path.isfile(f)]
			response=""
			for i in files:
				print "Name:",i
				last_t=last_modify(i)
				print "Last modified:",last_t
				sum=md5(i)
				print "Checksum:",sum
				response +="Filename:"+str(i)+ "Checksum:"+str(sum)+", Last modified:"+str(last_t)
			conn.send(response)
			return response

	elif cmdlist[0] == 'FileDownload':
		if cmdlist[1] == 'TCP':
			buf = 1024
			filename = cmdlist[2]
			f = open(filename, 'rb')
			l = f.read(buf)
			while (l):
				conn.send(l)
				print('Sent ', repr(l))
				l = f.read(buf)
			f.close()
			
		elif cmdlist[1] == 'UDP':
			filename = cmdlist[2]
			sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			host_udp = socket.gethostname()
			port_udp = 9999
			buf = 1024
			addr = (host_udp, port_udp)
			f = open(filename, 'rb') 
			data = f.read(buf)
			while data:
				if sock_udp.sendto(data, addr):
					print 'sending ...'
					data = f.read(buf)
			print 'Closed'
			sock_udp.close()
			f.close()
	else:
		print "no command"
		pass
	return 0
	
def md5(fname):
	hash = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash.update(chunk)
	return hash.hexdigest()

def last_modify(file):
	return time.ctime(os.path.getmtime(file))

def reg_check(filename, regex):
	try:
		pattern = re.compile(str(regex))
		if pattern.match(filename):
			return True
		else:
			return False
	except:
		print 'Client sent an invalid regex pattern'
		return False

def size_file(file):
	statinfo = os.stat(file)
	return statinfo.st_size

def file_type(file):
	command = 'file {0} | cut -d ":" -f2-'.format(file)
	process = Popen(command, shell=True, stdout=PIPE)
	stdout= process.communicate()
	return str(eval(str(stdout))[0].strip())

def shortListing(time1, time2):
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	start = datetime.strptime(time1, '%d/%m/%Y')
	end = datetime.strptime(time2, '%d/%m/%Y')
	response = ''

	for f in files:
		last_modified_time = parser.parse(time.ctime(os.path.getmtime(f)))
		if last_modified_time >= start and last_modified_time <= end:
			response += 'Name: {0}, Size: {1}, LastModified: {2}, Type: {3}\n'.format(f, size_file(f), last_modify(f), file_type(f))
	return response

def longListing():
	response = ''
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	print files
	for f in files:
		response += 'Name: {0}, Size: {1}, LastModified: {2}, Type: {3}\n'.format(f, size_file(f), last_modify(f), file_type(f))
	return response

def reg_match(regex):
	response = ''
	files = [f for f in os.listdir('.') if os.path.isfile(f) and reg_check(f,regex)]
	print files
	for f in files:
		response += 'Name: {0}, Size: {1}, LastModified: {2}, Type: {3}\n'.format(f, size_file(f), last_modify(f), file_type(f))
	if response:
		return response
	else:
		return 'Response from server: Invalid regex pattern'
	
while True:
	if status == 1:
		# Now wait for client connection.
		conn, addr = s.accept()
		print 'Got connection from', addr
		# Client joins with an initial hello server message
		data = conn.recv(1024)
		print data
	status = main()
