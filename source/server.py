import socket

server_address = ("localhost",6789)
max_size = 1000

print("Starting the Server")
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(server_address)

client,addr = server.accept()
data = client.recv(max_size)

print(f"{client} says {data}")
client.sendall(b"hello")
client.close()
server.close()