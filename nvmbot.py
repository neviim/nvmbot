#!/usr/bin/python
# -*- coding: utf8 -*-

import datetime
import xmpp
import re

jid 	= xmpp.protocol.JID('usuario@jabber.org')
pwd 	= 'senha'
server 	= "jabber.org" 
port 	= 5222

nvmkeyid = "nvmkeyid"
listakey = []
 
# conecta ao server 
conn = xmpp.Client(jid.getDomain(),debug=[])  
conn.connect([server, port])
conn.auth(jid.getNode(), pwd)

# avisando contatos de disponibilidade
conn.sendInitPresence()

print "nvmBot-> ativado..."
print

# função: procuraKeyid()
#
def procuraKeyid(r_lista, r_keyid):
	#
	for item in range(1,len(r_lista)):
		if r_lista[item] == r_keyid:
	   	   return True
	return False

# função: callback_message()
def callback_message(conn, mess):
	message_body = mess.getBody()

	# se não tiver uma mensagem retorna
	if not message_body:
		return

	# tendo mensagem a escreve no promp do bot.
	# 		 posteriormente envia-la para um arquivo log. 
	reply_message = "nvmBot<- " + message_body
	print reply_message

	# imprime a lista.
	if message_body == "lista":
	   print listakey
	   # retorna a lista com os codigo gerado, que estão em buffer.
	   conn.send(xmpp.protocol.Message(mess.getFrom(), listakey ))
	   return

	# pede um codigo ack-->
	#
	if message_body == nvmkeyid:
	 	# --- o keyid é altenticado.
	 	# retorna um ID com direito de executar x acoes
	 	keyid = re.sub("\D", "", str(datetime.datetime.now()))

	 	# retorna o codigo fullID <--ack
	 	conn.send(xmpp.protocol.Message(mess.getFrom(), keyid+" -> ok" ))
	 	
	 	# algoritimo que filtra a chave keyID do godigo e o coloca em uma lista.
	 	# para ser validado futuramente.
	 	listakey.append(keyid[6:8]+keyid[12:14]+keyid[18:20])
	 	
	# é um codigoID de comando?, o retorno de um fullID enviado <--ack
	#
	keyid_retorno = re.sub("\D", "", message_body ) # pega os numeros se tiver.

	if keyid_retorno.isdigit():
	   	# verifica se o codigo é valido esta na listaKey 	 
	   	if not procuraKeyid(listakey, keyid_retorno):
	   		return
	   	# remove o item da lista.
	   	listakey.remove(keyid_retorno)   
	   	# o codigoID de retorno é valido, executa o comando...
	   	conn.send(xmpp.protocol.Message(mess.getFrom(), " -> Codigo valido!" ))

# chama a mensagem em callback_message
conn.RegisterHandler( 'message', callback_message)

# main loop
#
def idle_proc( ):
	 """This function will be called in the main loop."""
	 pass

while True:
 try:
  conn.Process(1)
  idle_proc()
 except KeyboardInterrupt:
  print 'bot stopped by user request. shutting down.'
  conn.disconnect()
  break
 except xmpp.protocol.InternalServerError:
  print "Server error at Google, trying again"
