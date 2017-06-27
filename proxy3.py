#coding: utf-8

import socket
import thread
import sys
import time
import string
import binascii

def proxy (conexao, cliente, pedido):	
	try:
		linha = pedido.split('\n')[0] #Separa a primeira linha do pedido
		url = linha.split(' ')[1] #Pega a url depois do GET
		posicao = url.find('://') #Procura informação de protocolo HTTP ou HTTPS
		url_completa = url[(posicao+3):] #Pega a url sem essainformação
		posicao = url_completa.find('/') #Encontra a primeira barra para extrair o domínio (url raíz)
		if posicao == -1:
			posicao = len(url_completa)
		porta = 80
		url_raiz = url_completa[:posicao]
		urlCacheadaFlag = False
		for j in range (0, len(urls)):
			if url_completa == urls[j]:
				urlCacheadaFlag = True
				break
	except Exception, e:
		pass

	for i in range(0, len(blacklist)):
		if blacklist[i] in url:
			conexao.send(str.encode("HTTP/1.1 400 Bad Request\nContent-Type:text/html\n\n<html><body> Acesso Negado! </body></html>\n"))
			if conexao:
				conexao.close()
			arq=open('log.txt', 'a')
			arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Recusado: "+url+" presente na blacklist\n")
			arq.close()
			sys.exit(1)	

	WhiteListFlag = False
	for i in range(0, len(whitelist)):
		if whitelist[i] in url:
			WhiteListFlag = True
			break

	try:
		internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		internet.connect((url_raiz, porta))
		internet.send(pedido)

		resposta_final = ""
		while True:
			if urlCacheadaFlag:
				resposta_final = respostas[j]
				break
			resposta = internet.recv(maximo_dados)
			if resposta:
				resposta_final += resposta
				resposta_analise = resposta.upper()
				if (resposta_analise.find("CONTENT-TYPE: TEXT/HTML") != -1):
					if not WhiteListFlag:
						for i in range(0, len(termo)):
							posicao = str.find(resposta_analise, termo[i])
							if posicao!=-1:
								conexao.send(str.encode("HTTP/1.1 400 Bad Request\nContent-Type:text/html\n\n<html><body> Conteudo Restrito! </body></html>\n"))
								if internet:
									internet.close()
								if conexao:
									conexao.close()
								arq=open('log.txt', 'a')
								arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Recusado: "+url+" possui o termo "+ termo[i]+"\n")
								arq.close()
								sys.exit(1)
			else:
				break
		
		if not urlCacheadaFlag:
			urls.append(url_completa)
			respostas.append(resposta_final)
		conexao.send(resposta_final)
		internet.close()
		conexao.close()
		arq=open('log.txt', 'a')
		arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Autorizado: "+url+"\n")
		arq.close()
		sys.exit(1)
	except socket.error, (valor, mensagem):
		if internet:
			internet.close()
		if conexao:
			conexao.close()
		print "Erro: ", mensagem
		sys.exit(1)

IP = '127.0.0.1'
porta_proxy = 2045
porta_destino = 80
maximo_dados = 1024
conexao_pendente = 100
arq=open('blacklist.txt', 'r') #Abre, lê e separa em linhas o arquivo blacklist.txt salvando no vetor de strings blacklist
blacklist_string = arq.read() 
blacklist = blacklist_string.split('\n')
arq.close()
arq=open('whitelist.txt', 'r') #Abre, lê e separa em linhas o arquivo whitelist.txt salvando no vetor de strings whitelist
whitelist_string = arq.read() 
whitelist = whitelist_string.split('\n')
arq.close()
arq=open('badterms.txt', 'r') #Abre, lê e separa em linhas o arquivo badterms.txt salvando no vetor de strings termo
termo_string = arq.read()
termo_string = termo_string.upper()
termo = termo_string.split('\n')
arq.close()
urls = [] #Cria dois vetores globais para o caching
respostas = []


try:
	servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Inicia o servidor Proxy
	servidor.bind((IP, porta_proxy)) #Funcionando no IP 'localhost' e na porta 2045
	servidor.listen(conexao_pendente)
except socket.error, (valor, mensagem): #Mensagem de erro caso não consiga iniciar a conexão
	if servidor:
		servidor.close()
	print "Socket indisponivel: ", mensagem
	sys.exit(1)

while True:
	(conexao, cliente) = servidor.accept() #Aceita o pedido de conexão do navegador
	print 'Conectado por: ', cliente[0], ":", porta_proxy
	try:
		pedido = conexao.recv(maximo_dados) #Recebe pacote de dados de até 1024 bits
		if not pedido: #Se não obteve o pedido encerra
			break 
		thread.start_new_thread( proxy, (conexao, cliente, pedido, ) ) #Começa uma nova Thread para cada pedido
	except KeyboardInterrupt: #Ao encerrar com o ctrl+C, fecha o servidor e a conexão
		if servidor:
			servidor.close()
		if conexao:
			conexao.close()
		print '\nFinalizando conexao do cliente ', cliente
		sys.exit(1)