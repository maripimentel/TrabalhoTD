import socket
import thread
import sys
import time

def proxy (conexao, cliente, pedido):	

	try:
		linha = pedido.split('\n')[0]
		url = linha.split(' ')[1]
		posicao = url.find('://')
		url_completa = url[(posicao+3):]
		posicao = url_completa.find('/')
		if posicao == -1:
			posicao = len(url_completa)
		porta = 80
		url_raiz = url_completa[:posicao]
		urlCacheadaFlag = False
		print "***********************\n"
		for j in range (0, len(urls)):
			print "url completa: ", url_completa, "\n"
			print "urls: ",urls[j], "\n"
			print "comparacao: ", url_completa in urls[j], "\n"
			if url_completa == urls[j]:
				urlCacheadaFlag = True
				break
	except Exception, e:
		pass

	for i in range(0, len(blacklist)):
		#print "blacklist: ", blacklist[i]
		#print "url: ", url
		#print "comparacao: ", (blacklist[i] in url)
		if blacklist[i] in url:
			print "Site na blacklist: ", url
			conexao.send(str.encode("HTTP/1.1 400 Bad Request\nContent-Type:text/html\n\n<html><body> Acesso Negado! </body></html>\n"))
			if conexao:
				conexao.close()
			arq=open('log.txt', 'a')
			arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Recusado: "+url+" presente na blacklist\n")
			arq.close()
			sys.exit("SAINDO DA THREAD")	

	WhiteListFlag = False
	for i in range(0, len(whitelist)):
		#print "whitelist: ", whitelist[i]
		#print "url: ", url
		#print "comparacao: ", (whitelist[i] in url)
		if whitelist[i] in url:
			WhiteListFlag = True
			arq=open('log.txt', 'a')
			arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Autorizado: "+url+"\n")
			arq.close()
			break

	#print "O PROBLEMA EH O GETHOST: ", url_raiz
	try:
		internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		internet.connect((url_raiz, porta))
		internet.send(pedido)
		#print "*** Pedido ***"
		#print pedido
		#print "*** Fim Pedido ***\n\n"
		resposta_final = ""
		while True:
			if urlCacheadaFlag:
				print "USOU CACHE\n\n\n\n"
				resposta_final = respostas[j]
				break
			print "NAO USOU CACHE\n\n\n\n"
			resposta = internet.recv(maximo_dados)
			#print "*** Resposta ***"
			#print resposta
			#print "*** Fim Resposta ***\n\n"
			if resposta:
				resposta_final += resposta
				#print "*** Resposta Final ***"
				#print resposta_final
				#print "*** Fim Resposta Final ***\n\n"
				if not WhiteListFlag:
					for i in range(0, len(termo)):
						#print "******** TERMO *********"
						#print termo[i]
						posicao = resposta.find(" "+termo[i]+" ")
						if posicao!=-1:
							print "Termo na blacklist: ", termo[i]
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
			print "PASSOU AQUIIIIII \n\n\n\n\n" , len(urls), "\t", len(respostas), "\n"
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

print "Comecou programa! \n\n"
IP = 'localhost'
porta_proxy = 2049
porta_destino = 80
maximo_dados = 1024
conexao_pendente = 100
arq=open('blacklist.txt', 'r')
blacklist_string = arq.read() 
blacklist = blacklist_string.split('\n')
arq.close()
arq=open('whitelist.txt', 'r')
whitelist_string = arq.read() 
whitelist = whitelist_string.split('\n')
arq.close()
arq=open('badterms.txt', 'r')
termo_string = arq.read()
termo = termo_string.split('\n')
arq.close()
urls = [] 
respostas = []


try:
	servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servidor.bind((IP, porta_proxy))
	servidor.listen(conexao_pendente)
except socket.error, (valor, mensagem):
	if servidor:
		servidor.close()
	print "Socket indisponivel: ", mensagem
	sys.exit(1)

while True:
	(conexao, cliente) = servidor.accept()
	print 'Conectado por: ', cliente, ":", porta_proxy
	try:
		pedido = conexao.recv(maximo_dados)
		if not pedido: break
		print pedido
		thread.start_new_thread( proxy, (conexao, cliente, pedido, ) )
		print "\n\n\n\n\n\n\n\n\nEXIT!!!\n\n\n\n\n\n\n\n\n"
	except KeyboardInterrupt:
		if servidor:
			servidor.close()
		if conexao:
			conexao.close()
		print '\nFinalizando conexao do cliente ', cliente
		sys.exit(1)