# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# IGOR ANDRE HOURI E COSTA - 2016077942

import socket				 					#importa modulo de socket
import sys										#importa modulo de argv
import threading								#importa modulo de threading

BUFFER_LEN=1024
host = '127.0.0.1'
port =  55555
sync='DCC023C2'

def encode(number):
	return "{:X}".format(number)

def decode(number):
	hex_int = int(number, 16)
	return hex_int


msg = "0010101000101010"

s = socket.socket()				
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)				
s.bind(('', port))					
s.listen(1)
c, addr = s.accept()
pacote=c.recv(BUFFER_LEN).decode()
print(pacote)
c.close()