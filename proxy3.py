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
		for j in range (0, len(urls)): #Verifica se o objeto já foi rquisitado alguma vez e, se sim, aciona a flag
			if url_completa == urls[j]:
				urlCacheadaFlag = True
				break
	except Exception, e:
		pass

	for i in range(0, len(blacklist)): #Percorre o vetor da blacklist e procura a url rquisitada nele
		if blacklist[i] in url: #Se a url está na blacklist, envia mensagem de acesso negado ao navegador e encerra a thread
			conexao.send(str.encode("HTTP/1.1 400 Bad Request\nContent-Type:text/html\n\n<html><body> Acesso Negado! </body></html>\n"))
			if conexao:
				conexao.close()
			arq=open('log.txt', 'a') #Salva no log como "encaminhamento recusado" com a data, a hora e o motivo
			arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Recusado: "+url+" presente na blacklist\n")
			arq.close()
			sys.exit(1)

	WhiteListFlag = False
	for i in range(0, len(whitelist)): #Percorre o vetor da whitelist e procura a url rquisitada nele
		if whitelist[i] in url: #Se a url está na whitelist, aciona a flag que fará com que a verificação de termos seja ignorada
			WhiteListFlag = True
			arq=open('log.txt', 'a') #Salva no log como "encaminhamento aceito" com a data e a hora
			arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Autorizado: "+url+"\n")
			arq.close()
			break

	try:
		internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Inicia o socket que vai comunicar com o servidor web
		internet.connect((url_raiz, porta)) #Conecta com o domínio na porta 80
		internet.send(pedido) #Envia o pedido para o servidor e aguarda resposta

		resposta_final = ""
		while True:
			if urlCacheadaFlag: #Se esse site já foi acessado, pega informações da cache e segue em frente
				resposta_final = respostas[j]
				break
			resposta = internet.recv(maximo_dados) #Pega a resposta do servidor ao pedido
			if resposta: #Se existe uma resposta:
				resposta_final += resposta #Concatena à uma parte anterior da resposta (resposta_final começa vazia)
				resposta_analise = resposta.upper() #Coloca tudo em maiúsculo para deixar insensível ao caso (bloqueia termos em maiúsculo e minúsculo)
				if (resposta_analise.find("CONTENT-TYPE: TEXT/HTML") != -1): #Analisa apenas se for um pacote com conteúdo texto
					print "Resposta: ", resposta_analise, "\n"
					if not WhiteListFlag: #Se estiver na whitelist, pular a verificação de termos proibidos
						for i in range(0, len(termo)): #Para cada termo do vetor de termos bloqueados, procurar na resposta
							posicao = str.find(resposta_analise, termo[i])
							print "\nTermo: ", termo[i], "\n"
							print "Posicao: ", posicao, "\n\n\n"
							if posicao!=-1: #Se encontrou um termo proibido, envia mensagem de conteúdo restrito ao navegador e encerra a thread
								conexao.send(str.encode("HTTP/1.1 400 Bad Request\nContent-Type:text/html\n\n<html><body> Conteudo Restrito! </body></html>\n"))
								if internet:
									internet.close()
								if conexao:
									conexao.close()
								arq=open('log.txt', 'a') #Salva no log como "encaminhamento recusado" com a data, a hora e o motivo
								arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Recusado: "+url+" possui o termo "+ termo[i]+"\n")
								arq.close()
								sys.exit(1)
			else:
				break

		if not urlCacheadaFlag: #Se o objeto não estiver na cache ainda, aidicona-lo ao final do vetor
			urls.append(url_completa) #Sua url
			respostas.append(resposta_final) #Seu conteúdo
		conexao.send(resposta_final) #Se não foi barrado por blacklist ou bad terms, envia resposta do servidor ao navegador
		internet.close()
		conexao.close()
		arq=open('log.txt', 'a') #Salva no log como "encaminhamento aceito" com a data e a hora
		arq.write(time.strftime('%d/%m/%Y %H:%M:%S')+" - Encaminhamento Autorizado: "+url+"\n")
		arq.close()
		sys.exit(1) #Encerra a thread
	except socket.error, (valor, mensagem): #Mensagem de erro caso não consiga iniciar a conexão
		if internet:
			internet.close()
		if conexao:
			conexao.close()
		print "Erro: ", mensagem
		sys.exit(1) #Encerra a thread

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
