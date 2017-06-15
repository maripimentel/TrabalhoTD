import socket
import thread

IP = 'localhost'
porta_proxy = 2048
porta_destino = 80
timeout = 1000
texto = 0

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((IP, porta_proxy))
servidor.listen(5)

internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
internet.connect((IP, porta_destino))

def servidorListen (servidor):
	while True:
		(objeto, cliente) = servidor.accept()
		print 'Conectado por: ', cliente
		while True:
			texto = objeto.recv(1024)
			if not texto: break
			print texto
		print 'Finalizando conexao do cliente ', cliente
		objeto.close()

def internetSend (internet):
	#mensagem = raw_input()
	while (texto != 0):
		internet.send(texto)
		texto = 0
		#mensagem = raw_input()
	internet.close()

try:
	thread.start_new_thread( servidorListen, (servidor, ) )
	thread.start_new_thread( internetSend, (internet, ) )
except:
	print "Erro."
while 1:
	pass

#servidor.close()