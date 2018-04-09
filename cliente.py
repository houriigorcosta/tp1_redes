# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# IGOR ANDRE HOURI E COSTA - 2016077942

import socket				 					#importa modulo de socket
import sys										#importa modulo de argv
import functools
BUFFER_LEN=1024
host = '127.0.0.1'
port =  55555
sync="{:032b}".format(0xDCC023C2)


def carry_around_add(a, b):
    c = a + b
    return(c &0xffff) + (c>>16)

def encode(number):
	return "{:X}".format(number)
def decode(number):
	hex_int = int(number, 16)
	return hex_int

def twos_comp(val, bits):
	"""compute the 2's complement of int value val"""
	if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
		val = val - (1 << bits)        # compute negative value
	return val  


def obtem_xor(soma,s):
	if (2**s-1>soma):
		return 2**s-1
	else:
		return obtem_xor(soma,s+1) 

def checksum_maker(msg):
	chunks, chunk_size = len(msg), 8
	msg = [ msg[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
	print (msg)
	soma = sum([int(h,2) for h in msg]) % (2**16)
	print ("soma: {} {:016b}".format(soma,soma))
	soma = (soma ^ 0xFFFF) % (2**16)
	print ("soma2: {} {:016b}".format(soma,soma))
	return 	soma

def checksum_compare(msg,chk):
	chunks, chunk_size = len(msg), 8
	msg = [ msg[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
	print (msg)
	soma = (sum([int(h,2) for h in msg]) +chk)%(2**16)
	print ("soma: {} {:016b}".format(soma,soma))
	return soma

def extrai_msg_sem_chk(msg_com_chk):
	return 	msg_com_chk[0:80]+msg_com_chk[96:len(msg_com_chk)], int(msg_com_chk[80:96],2)

msg="00101010001010100010101000101010"

s = socket.socket()         					
s.settimeout(15.0)
#host = socket.gethostbyname(host)							
#s.connect((host, port))
#msg=encode(msg)
msg_sem_chk = "{}{}{:016b}{:08b}{:08b}{}".format(sync,sync,len(msg),0,0,msg)
chk=checksum_maker(msg_sem_chk)
print("{}".format(chk))
msg_com_chk = "{}{}{:016b}{:016b}{:08b}{:08b}{}".format(sync,sync,len(msg),chk,0,0,msg)

msg_sem_chk_nova,chk_novo=extrai_msg_sem_chk(msg_com_chk)

print(msg_sem_chk)
print(msg_sem_chk_nova)
print((msg_sem_chk_nova == msg_sem_chk))
print(chk == chk_novo)
print (checksum_compare( msg_sem_chk_nova,chk_novo)+1%2**16)

#s.send(msg.encode())
#s.close()							