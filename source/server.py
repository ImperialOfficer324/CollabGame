import socket
import json

address = ('localhost',6789)
max_size = 1000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

server.listen(5)

client,addr = server.accept()
#data = client.recv(max_size)

file_contents=""

with open('levels/test_level.json', 'r') as level_file:
    for line in level_file:
        file_contents+=str(line)
level=json.loads(file_contents)
print(level)

gamedata={
    "level":level,
}

client.close()
server.close()
