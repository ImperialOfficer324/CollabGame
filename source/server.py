import socket

address = ('localhost',6789)
max_size = 1000

print("starting the server")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

server.listen(5)

client,addr = server.accept()
data = client.recv(max_size)

print(data)

client.sendall(b'Hullo')
client.close()
server.close()