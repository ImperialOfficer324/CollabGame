import socket
import json
import threading
import messages

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
    "players":[{"x":level["player_x"], "y":level["player_y"], "image":"assets/players/player1.png"},
    {"x":level["player_x"], "y":level["player_y"], "image":"assets/players/player2.png"}]
}

gamedata_string = json.dumps(gamedata)

zero = "0"
one = "1"

game_state = 1
def listen_to_client(client,other_client):
    global gamedata
    global game_state
    while game_state:
        msg_bytes = client.recv(max_size)
        msg = msg_bytes.decode('utf-8')
        if msg == "quit":
            other_client.sendall(msg_bytes)
            client1.close()
            client2.close()
            server.close()
            game_state = 0
            quit()
        gamedata = messages.parse_message(msg_bytes,gamedata)
        other_client.sendall(msg_bytes)

client1.sendall(bytes(gamedata_string,"utf-8"))
client2.sendall(bytes(gamedata_string,"utf-8"))

client1_thread = threading.Thread(target = lambda:listen_to_client(client1,client2))
client2_thread = threading.Thread(target = lambda:listen_to_client(client2,client1))
client1_thread.start()
client2_thread.start()

client1.sendall(zero.encode())
client2.sendall(one.encode())