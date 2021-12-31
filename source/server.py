import socket
import json
import threading
import messages
import time
import os

IP = 'localhost'
port = 6789
address = ('localhost',6789)
max_size = 1000

temp_ip = input("IP Address: ")
if temp_ip!="":
    try:
        IP = int(temp_ip)
    except ValueError:
        IP = temp_ip

temp_port = input("Port: ")
if temp_port!="":
    port = int(temp_port)

player1_skin = "player1"
temp = input("Player 1 Appearance: ")
if temp+'.png' in os.listdir("assets/players/"):
    player1_skin = temp

player2_skin = "player2"
temp = input("Player 2 Appearance: ")
if temp+'.png' in os.listdir("assets/players/"):
    player2_skin = temp

level = "level1"
temp = input("Level: ")
if temp+'.json' in os.listdir("levels/"):
    level = temp

address = (IP,port)

game_state = 1
gamedata = {}

def load_server(address,max_size):
    global gamedata
    global level
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)

    server.listen(5)

    client1,addr1 = server.accept()
    client2,addr2 = server.accept()
    #data = client.recv(max_size)

    file_contents = ""

    with open(f'levels/{level}.json', 'r') as level_file:
        for line in level_file:
            file_contents+=str(line)
    level=json.loads(file_contents)
    print(level)

    gamedata = {
        "level":level,
        "players":[{"x":level["player_x"],"y":level["player_y"],"image":f"assets/players/{player1_skin}.png","y_vel":0,"anim":"idle","facing":0},
        {"x":level["player_x"],"y":level["player_y"],"image":f"assets/players/{player2_skin}.png","y_vel":0,"anim":"idle","facing":0}]
    }
    print(type(gamedata))

    gamedata_string = json.dumps(gamedata)

    zero = "0|"
    one = "1|"

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
            gamedata,anim_data,win_data = messages.parse_message(msg_bytes,gamedata)
            other_client.sendall(msg_bytes)
            if(win_data[0]==1):
                print("someone reached the end")                
                game_state = 0
                server.close()

    client1.sendall(bytes(gamedata_string,"utf-8"))
    client2.sendall(bytes(gamedata_string,"utf-8"))

    time.sleep(0.1);

    client1_thread = threading.Thread(target = lambda:listen_to_client(client1,client2,0))
    client2_thread = threading.Thread(target = lambda:listen_to_client(client2,client1,1))

    client1.sendall(zero.encode())
    client2.sendall(one.encode())

    time.sleep(0.1);

    client1_thread.start()
    client2_thread.start()

load_server(address,max_size)
