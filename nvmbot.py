#!/usr/bin/python
# -*- coding: utf8 -*-
#
# versão: 0.0.1

import datetime
import xmpp
import re

jid    = xmpp.protocol.JID('homeia@jabber.org')
pwd    = '#homeia#'
server = "jabber.org" 
port   = 5222

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
		for item in range(0,len(r_lista)):
				if r_lista[item] == r_keyid:
					 return True
		return False

# função: ler_meminfo()
def ler_meminfo():
    """
    Retorna um dicionario com os dados de meminfo formato (str:int).
    Valores estão em kilobytes.
    """
    re_parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')
    result = dict()

    for line in open('/proc/meminfo'):
        match = re_parser.match(line)
        if not match:
            continue # pula a linha
        key, value = match.groups(['key', 'value'])
        result[key] = int(value)
    return result

# função: callback_message()
def callback_message(conn, mess):
		message_body = mess.getBody()

		# se não tiver uma mensagem retorna
		if not message_body:
				return

		# tendo mensagem a escreve no promp do bot.
		#        posteriormente envia-la para um arquivo log. 
		reply_message = "nvmBot<- " + message_body
		print reply_message

		# imprime a lista.
		if message_body == "lista":
			 print "nvmBot-> " + str(listakey)
			 # retorna a lista com os codigo gerado, que estão em buffer.
			 conn.send(xmpp.protocol.Message(mess.getFrom(), "nvmBot-> " + str(listakey) ))
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
						print "nvmBot-> " + "keyid não encontrado."
						return

				# valida se o parametro de reconhecimento esta correto.
				if len(message_body) > 6:
					#
					if message_body[6] != ".":
						conn.send(xmpp.protocol.Message(mess.getFrom(), " -> Parametro invalido!" ))
						return
						#
					else:
						# se solicitar a "data", retorna a data e hora do sistema.
						comando = message_body.split(".")[1]

						# Data ...
						if comando == "data":
							conn.send(xmpp.protocol.Message(mess.getFrom(), str(datetime.datetime.now()) ))
							#
						elif comando == "meminfo":
							conn.send(xmpp.protocol.Message(mess.getFrom(), ler_meminfo() ))

						else:
							# o codigoID de retorno é valido, executa o comando...
							conn.send(xmpp.protocol.Message(mess.getFrom(), " -> Codigo valido!" ))
				else:
					# o codigoID de retorno é valido, executa o comando...
					conn.send(xmpp.protocol.Message(mess.getFrom(), " -> Uso incorreto, id indo para αποτέφρωση, ?:|" ))

				# remove o keyid da listakey.
				listakey.remove(keyid_retorno)

# chama a mensagem em callback_message
conn.RegisterHandler( 'message', callback_message)

# main loop
#
def idle_proc( ):
		"""Esta função sera chamada no main loop."""
		pass

while True:
		try:
			conn.Process(1)
			idle_proc()
		except KeyboardInterrupt:
			print 'nvmbot paralizado por definição do admin. shutting down.'
			conn.disconnect()
			break
		except xmpp.protocol.InternalServerError:
			print "Server jabber com error, ..."