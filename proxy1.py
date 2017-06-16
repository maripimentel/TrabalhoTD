import socket
import thread
import sys

def extraiURL (conexao, cliente, pedido):
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
		proxy (url_completa, url_raiz, url, porta, conexao, cliente, pedido)
	except Exception, e:
		pass	

def proxy (url_completa, url_raiz, url, porta, conexao, cliente, pedido):
	for i in range(0, len(blacklist)):
		print "blacklist: ", blacklist[i]
		print "url: ", url
		print "comparacao: ", (blacklist[i] in url)
		if blacklist[i] in url:
			print "Site na blacklist: ", url
			#conexao.send("HTTP/1.1 400 Connection Denied\n")
			conexao.close()
			sys.exit(1)
	IP_raiz = socket.gethostbyname(url_raiz)
	print 'IP raiz: ', IP_raiz
	try:
		internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		internet.connect((IP_raiz, porta))
		internet.send(pedido)
		while True:
			resposta = internet.recv(maximo_dados)
			if resposta:
				conexao.send(resposta)
			else:
				break
		servidor.close()
		conexao.close()
	except socket.error, (valor, mensagem):
		if internet:
			internet.close()
		if conexao:
			conexao.close()
		print "Erro: ", mensagem
		sys.exit(1)

IP = 'localhost'
porta_proxy = 2048
porta_destino = 80
maximo_dados = 1024
conexao_pendente = 20
timeout = 1000
blacklist = ["gaia.cs.umass.edu", "www.youtube.com", "aprender.unb.br"]

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
		thread.start_new_thread( extraiURL, (conexao, cliente, pedido, ) )
	except KeyboardInterrupt:
		if servidor:
			servidor.close()
		if conexao:
			conexao.close()
		print '\nFinalizando conexao do cliente ', cliente
		sys.exit(1)
