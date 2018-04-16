# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# IGOR ANDRE HOURI E COSTA - 2016077942

import socket				 					#importa modulo de socket
import sys										#importa modulo de argv
import functools
from base64 import b16encode, b16decode
import binascii


BUFFER_LEN=65000
host = '127.0.0.1'
port =  55555
sync_int = 0xDCC023C2
sync="{:032b}".format(sync_int)
checksum_true = 2**16-1
TAMANHO_PEDACOS=100
TIMEOUT=15.0

def make_checksum(sync,id_,flag,msg):
	checksum=(sync+sync+len(msg)+id_+flag+sum(msg))%(2**16)
	#print("{:016b}".format(checksum))
	checksum=(checksum^ 0xFFFF)
	#print("{:016b}".format(checksum))
	return checksum

def compare_checksum(sync,id_,flag,msg,chk):
	checksum=(sync+sync+len(msg)+id_+flag+sum(msg))%(2**16)
	#print("{:016b}".format(checksum))
	#print("{:016b}".format(checksum+chk))
	return checksum+chk


chk_ack0=make_checksum(sync_int,0,0x80,[0])
ack0="{:08X}{:08X}{:04X}{:04X}{:02X}{:02X}".format(sync_int,sync_int,0,chk_ack0,0,0x80)
chk_ack1=make_checksum(sync_int,1,0x80,[0])
ack1="{:08X}{:08X}{:04X}{:04X}{:02X}{:02X}".format(sync_int,sync_int,0,chk_ack1,1,0x80)

def recebe_pacote(c,file_out):
	pacote=c.recv(BUFFER_LEN)
	pacote=b16decode(pacote)
	if pacote!=b'':
		print(pacote)
		sync_msg01=int(pacote[0:8],16)
		sync_msg02=int(pacote[8:16],16)
		length=int(pacote[16:20],16)
		chksum=int(pacote[20:24],16)
		id_msg=int(pacote[24:26],16)
		flag=int(pacote[26:28],16)
		dados=pacote[28:28+length]
		chk_flag = (compare_checksum(sync_msg01,id_msg,flag,dados,chksum)==checksum_true)
		print("sync_msg01 {:X}\nsync_msg02 {:X}\nlength {}\nchksum {}\nid_msg {}\nflag {}\ndados {}\nchksum_flag {}\n".format(sync_msg01,sync_msg02,length,chksum,id_msg,flag,dados,chk_flag))
		if chk_flag:
			if id_msg==0:
				c.send(b16encode(ack0.encode()))
			elif id_msg==1:
				c.send(b16encode(ack1.encode()))
			file_out.write(dados)

def envia_pacote(s,msg_lista,id_tx,pivo):
	if pivo<len(msg_lista):
			chk=make_checksum(sync_int,id_tx%2,0,msg_lista[pivo])
			pacote="{:08X}{:08X}{:04X}{:04X}{:02X}{:02X}".format(sync_int,sync_int,len(msg_lista[pivo]),chk,id_tx%2,0).encode()+msg_lista[pivo]
			print("chk {}\npacote {}".format(chk,pacote))
			pacote=b16encode(pacote)
			s.send(pacote)
			ack=s.recv(BUFFER_LEN)
			ack=b16decode(ack).decode()
			if (id_tx%2==1 and ack==ack1) or (id_tx%2==0 and ack==ack0):
				print("mensagem recebida com sucesso {}".format(id_tx))
				pivo+=1
				id_tx+=1		
			else:
				print("mensagem recebida sem sucesso {}\n{}\n{}\n\n\n".format(id_tx,ack,ack0))

	return (id_tx, pivo)

if len(sys.argv)==4:
	print("servidor")
	file_out=open(sys.argv[3],'wb')
	file_in=open(sys.argv[2],'rb')
	f=file_in.read()
	msg_lista=[ f[i:i+TAMANHO_PEDACOS] for i in range(0, len(f), TAMANHO_PEDACOS) ]
	file_in.close()

	port = int(sys.argv[1])
	s = socket.socket()				#Abre Socket e trata erro de address already in use
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)				
	s.bind(('', port))					#faz o bind na porta devida
	s.listen(5)						#prepara conexões vindouras
	c, addr = s.accept()     		#espera conexão com o cliente
	c.settimeout(TIMEOUT)

	id_tx=0
	pivo=0
	while True:
		recebe_pacote(c,file_out)
		id_tx, pivo = envia_pacote(c,msg_lista,id_tx,pivo)
		

		
		




elif len(sys.argv)==5:
	print("cliente")
	file_out=open(sys.argv[4],'wb')
	file_in=open(sys.argv[3],'rb')
	f=file_in.read()
	#print (f)
	msg_lista=[ f[i:i+TAMANHO_PEDACOS] for i in range(0, len(f), TAMANHO_PEDACOS) ]
	file_in.close()

	host=sys.argv[1]								#obtem o ip do servidor do primeiro argumento
	port=int(sys.argv[2])							#obtem a porta do segundo arguemento
	s = socket.socket()         					#cria socket para comunicação com o servidor
	s.settimeout(TIMEOUT)
	host = socket.gethostbyname(host)				#obtem nome de maquina doip do servidor				
	s.connect((host, port))							#conecta ao servidor pelo host na porta port
	
	id_tx=0
	pivo=0
	while True:
		id_tx, pivo = envia_pacote(s,msg_lista,id_tx,pivo)
		recebe_pacote(s,file_out)
	
	
