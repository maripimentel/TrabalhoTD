import socket
import thread
import sys

def extraiURL (objeto, cliente, texto):
	try:
		linha = texto.split('\n')[0]
		url = linha.split(' ')[1]
		posicao = url.find('://')
		url_completa = url[(posicao+3):]
		posicao = url_completa.find('/')
		if posicao == -1:
			posicao = len(url_completa)
		porta = 80
		url_raiz = url_completa[:posicao]
		proxy (url_completa, url_raiz, porta, objeto, cliente, texto)
	except Exception, e:
		pass	

def proxy (url_completa, url_raiz, porta, objeto, cliente, texto):
	IP_raiz = socket.gethostbyname(url_raiz)
	print 'IP raiz: ', IP_raiz
	servidor.close()
	objeto.close()




#internet.send(texto)


IP = 'localhost'
porta_proxy = 2048
porta_destino = 80
timeout = 1000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((IP, porta_proxy))
servidor.listen(5)
#internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#internet.connect(("www.mecajun.com", porta_destino))
while True:
		(objeto, cliente) = servidor.accept()
		print 'Conectado por: ', cliente
		try:
			texto = objeto.recv(1024)
			if not texto: break
			print texto
			thread.start_new_thread( extraiURL, (objeto, cliente, texto, ) )
		except KeyboardInterrupt:
			servidor.close()
			objeto.close()
			print 'Finalizando conexao do cliente ', cliente
			sys.exit(1)



#servidor.close()