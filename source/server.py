import socket
import json

address = ('localhost',6789)
max_size = 1000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

server.listen(5)

client1,addr1 = server.accept()
client2,addr2 = server.accept()
#data = client.recv(max_size)

file_contents = ""

with open('levels/test_level.json', 'r') as level_file:
    for line in level_file:
        file_contents+=str(line)
level=json.loads(file_contents)
print(level)

gamedata = {
    "level":level,
    "players":[{"x":level["player_x"], "y":level["player_y"], "image":"assets/players/player1.png"},{"x":level["player_x"], "y":level["player_y"], "image":"assets/players/player2.png"}]
}

gamedata_string = json.dumps(gamedata)

zero = "0"
one = "1"

#client1.sendall(zero.encode())
client1.sendall(bytes(gamedata_string,"utf-8"))
#client2.sendall(one.encode())
client2.sendall(bytes(gamedata_string,"utf-8"))

client1.close()
client2.close()
server.close()
