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
sync="{:032b}".format(0xDCC023C2)
checksum_true = 2**16-1
TAMANHO_PEDACOS=100



def twos_comp(val, bits):
	"""compute the 2's complement of int value val"""
	if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
		val = val - (1 << bits)        # compute negative value
	return val  

def checksum_maker(msg):
	chunks, chunk_size = len(msg), 8
	msg = [ msg[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
	#print (msg)
	soma=0
	for h in msg:
		#print (h)
		soma+=int(h,16)%(2**16)
		#try:
		#	soma+=int(h,2)%(2**16)
		#except:
		#	print(h)
		#	exit(-1)

	#soma = sum([int(h,2) for h in msg]) % (2**16)
	#print ("soma: {} {:016b}".format(soma,soma))
	soma = (soma ^ 0xFFFF) % (2**16)
	#print ("soma2: {} {:016b}".format(soma,soma))
	return 	soma

def checksum_compare(msg,chk):
	chunks, chunk_size = len(msg), 8
	msg = [ msg[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
	#print (msg)
	soma = (sum([int(h,16) for h in msg]) +chk)%(2**16)
	#print ("soma: {} {:016b}".format(soma,soma))
	return soma

def extrai_msg_sem_chk(msg_com_chk):
	return 	msg_com_chk[0:80]+msg_com_chk[96:len(msg_com_chk)], int(msg_com_chk[80:96] or '0',2)

ack_id1 = "{}{}{:016b}{:08b}{:08b}".format(sync,sync,0,1,0x80)
chk_ack_id1=checksum_maker(ack_id1)
ack_id1 = "{}{}{:016b}{:016b}{:08b}{:08b}".format(sync,sync,0,chk_ack_id1,1,0x80)

ack_id0 = "{}{}{:016b}{:08b}{:08b}".format(sync,sync,0,0,0x80)
chk_ack_id0=checksum_maker(ack_id0)
ack_id0 = "{}{}{:016b}{:016b}{:08b}{:08b}".format(sync,sync,0,chk_ack_id0,0,0x80)

if len(sys.argv)==4:
	print("Servidor")
	#file_in = open(sys.argv[2],'r')
	file_out = open(sys.argv[3],'wb')
	file_in = open(sys.argv[2],'rb')
	f=file_in.read()
	msg_lista=[ f[i:i+TAMANHO_PEDACOS] for i in range(0, len(f), TAMANHO_PEDACOS) ]
	file_in.close()
	port = int(sys.argv[1])
	s = socket.socket()				#Abre Socket e trata erro de address already in use
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)				
	s.bind(('', port))					#faz o bind na porta devida
	s.listen(5)						#prepara conexões vindouras
	c, addr = s.accept()     		#espera conexão com o cliente
	c.settimeout(15.0)
	id_tx = 0
	pivo=0
	while True:
		#Servidor recebe a mensagem
		msg_codificada=c.recv(BUFFER_LEN)
		msg_decodificada=b16decode(msg_codificada)
		if msg_decodificada != b'':
			msg_decodificada = msg_decodificada.decode()
			msg_sem_chk_nova, chk_novo=extrai_msg_sem_chk(msg_decodificada)
			checksum_flag = checksum_compare( msg_sem_chk_nova,chk_novo)
			#print ("Mensagem decodificada:\n {}\nchecksum:{} e flag_checksum:{}".format(msg_decodificada,chk_novo,checksum_flag))
			if checksum_flag == checksum_true:
				sync_msg01=msg_decodificada[0:32]
				sync_msg02=msg_decodificada[32:64]
				length=int(msg_decodificada[64:80],2)
				chksum=msg_decodificada[80:96]
				id_msg=int(msg_decodificada[96:104],2)
				flag=int(msg_decodificada[104:112],2)
				#print("dados {}".format(msg_decodificada[112:]))
				dados=int(msg_decodificada[112:] or '0',2)
				try:
					dados=int(msg_decodificada[112:] or '0',2)
					dados=binascii.unhexlify('%x' % dados)
				except:
					dados=binascii.unhexlify('0%x' % dados)

				print("sync_msg01 {}\nsync_msg02 {}\nlength {}\nchksum {}\nid_msg {}\nflag {}\ndados {}".format(sync_msg01,sync_msg02,length,chksum,id_msg,flag,dados))
				if id_msg==0:
					c.send(b16encode(ack_id0.encode()))
				elif id_msg==1:
					c.send(b16encode(ack_id1.encode()))
				file_out.write(dados)
				file_out.flush()

		#servidor envia mensagem
		if pivo<len(msg_lista):	
			msg=msg_lista[pivo]
			pivo+=1
			msg_sem_chk = "{}{}{:016b}{:08b}{:08b}{}".format(sync,sync,len(msg),id_tx%2,0,msg).encode()
			chk=checksum_maker(msg_sem_chk)
			print("{}".format(chk))
			msg_com_chk = "{}{}{:016b}{:016b}{:08b}{:08b}{}".format(sync,sync,len(msg),chk,id_tx%2,0,msg).encode()
			c.send(b16encode(msg_com_chk.encode()))
			ack=c.recv(BUFFER_LEN)
			ack=b16decode(ack).decode()
			if (id_tx%2==1 and ack==ack_id1) or (id_tx%2==0 and ack==ack_id0):
				print("mensagem recebida com sucesso {}".format(id_tx))
			else:
				print("mensagem recebida sem sucesso {}\n{}\n{}".format(id_tx,ack,ack_id0))
			id_tx+=1		





		


elif len(sys.argv)==5:
	print("cliente")
	#file_in = open(sys.argv[3],'r')
	file_out = open(sys.argv[4],'wb')
	file_in = open(sys.argv[3],'rb')
	f=file_in.read()
	msg_lista=[ f[i:i+TAMANHO_PEDACOS] for i in range(0, len(f), TAMANHO_PEDACOS) ]
	file_in.close()
			
	#msg_lista = [bin(i) for i in msg_lista]
	#file_in.close()

	host=sys.argv[1]								#obtem o ip do servidor do primeiro argumento
	port=int(sys.argv[2])							#obtem a porta do segundo arguemento
	s = socket.socket()         					#cria socket para comunicação com o servidor
	s.settimeout(15.0)
	host = socket.gethostbyname(host)				#obtem nome de maquina doip do servidor				
	s.connect((host, port))							#conecta ao servidor pelo host na porta port
	id_rx = 0
	id_tx = 0
	pivo=0
	while True:
		#cliente envia mensagem
		if pivo<len(msg_lista):		
			msg=msg_lista[pivo]
			pivo+=1
			msg_sem_chk = "{}{}{:016b}{:08b}{:08b}{}".format(sync,sync,len(msg),id_tx%2,0,msg).encode()
			chk=checksum_maker(msg_sem_chk)
			print("{}".format(chk))
			msg_com_chk = "{}{}{:016b}{:016b}{:08b}{:08b}{}".format(sync,sync,len(msg),chk,id_tx%2,0,msg).encode()
			s.send(b16encode(msg_com_chk.encode()))
			ack=s.recv(BUFFER_LEN)
			ack=b16decode(ack).decode()
			if (id_tx%2==1 and ack==ack_id1) or (id_tx%2==0 and ack==ack_id0):
				print("mensagem recebida com sucesso {}".format(id_tx))
			else:
				print("mensagem recebida sem sucesso {}\n{}\n{}".format(id_tx,ack,ack_id0))
			id_tx+=1		
		

		#cliente recebe a mensagem
		msg_codificada=s.recv(BUFFER_LEN)
		msg_decodificada=b16decode(msg_codificada)
		if msg_decodificada != b'':
			msg_decodificada = msg_decodificada.decode()
			msg_sem_chk_nova, chk_novo=extrai_msg_sem_chk(msg_decodificada)
			checksum_flag = checksum_compare( msg_sem_chk_nova,chk_novo)
			#print ("Mensagem decodificada:\n {}\nchecksum:{} e flag_checksum:{}".format(msg_decodificada,chk_novo,checksum_flag))
			if checksum_flag == checksum_true:
				sync_msg01=msg_decodificada[0:32]
				sync_msg02=msg_decodificada[32:64]
				length=int(msg_decodificada[64:80],2)
				chksum=msg_decodificada[80:96]
				id_msg=int(msg_decodificada[96:104],2)
				flag=int(msg_decodificada[104:112],2)
				dados=int(msg_decodificada[112:] or '0',2)
				try:
					dados=int(msg_decodificada[112:] or '0',2)
					dados=binascii.unhexlify('%x' % dados)
				except:
					dados=binascii.unhexlify('0%x' % dados)
				print("sync_msg01 {}\nsync_msg02 {}\nlength {}\nchksum {}\nid_msg {}\nflag {}\ndados {}".format(sync_msg01,sync_msg02,length,chksum,id_msg,flag,dados))
				if id_msg==0:
					s.send(b16encode(ack_id0.encode()))
				elif id_msg==1:
					s.send(b16encode(ack_id1.encode()))
					file_out.write(dados)
				file_out.flush()


