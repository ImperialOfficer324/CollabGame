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

with open('levels/t2.json', 'r') as level_file:
    for line in level_file:
        file_contents+=str(line)
level=json.loads(file_contents)
print(level)

gamedata = {
    "level":level,
    "players":[{"x":level["player_x"], "y":level["player_y"], "image":"assets/players/player1.png","y_vel":0},
    {"x":level["player_x"], "y":level["player_y"], "image":"assets/players/player2.png","y_vel":0}]
}

gamedata_string = json.dumps(gamedata)

zero = "0"
one = "1"

game_state = 1
def listen_to_client(client,other_client,player_id):
    global gamedata
    global game_state
    gravity_counter = 0
    while game_state:
        # # apply gravity to player
        # player_y_vel = gamedata["players"][player_id]["y_vel"]
        # if player_y_vel!=0:
        #     new_y = (gamedata["players"][player_id]["y"]+player_y_vel)+50
        #     player_x = gamedata['players'][player_id]["x"]

        #     tile_1 = gamedata['level']['grid'][new_y//50][player_x//50]
        #     tile_2 = 0

        #     if tile_1 != 1 and tile_2 != 1:
        #         gamedata["players"][player_id]["y"]+=player_y_vel
        #         messages.send_message(f"move y {player_id} {player_y_vel} ",client)
        #         messages.send_message(f"move y {player_id} {player_y_vel} ",other_client)
        #     else:
        #         player_y_vel = 0
        # gravity_counter+=1

        # if gravity_counter>=4:
        #     gravity_counter = 0
        #     player_y_vel+=2
        #     # player_y_vel = 1

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

client1_thread = threading.Thread(target = lambda:listen_to_client(client1,client2,0))
client2_thread = threading.Thread(target = lambda:listen_to_client(client2,client1,1))
client1_thread.start()
client2_thread.start()

client1.sendall(zero.encode())
client2.sendall(one.encode())