import socket

server_address=("localhost", 6789)
max_size=1000
print("starting the client")
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
client.sendall(b"Hello World")
data=client.recv(max_size)
client.close()
