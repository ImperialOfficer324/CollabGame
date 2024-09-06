#5121
from ctypes import sizeof
import socket
import pygame
import json
import threading
import messages
import time
import os

# Server
IP = 'localhost'
port = 6789
address = ('localhost',6789)
max_size = 1000

temp_ip = input(f"IP Address ({IP}): ")
if temp_ip!="":
    try:
        IP = int(temp_ip)
    except ValueError:
        IP = temp_ip

temp_port = input(f"Port ({port}): ")
if temp_port!="":
    port = int(temp_port)

player1_skin = "player1"
temp = input(f"Player 1 Appearance ({player1_skin}): ")
if temp+'.png' in os.listdir("assets/players/"):
    player1_skin = temp

player2_skin = "player2"
temp = input(f"Player 2 Appearance ({player2_skin}): ")
if temp+'.png' in os.listdir("assets/players/"):
    player2_skin = temp

level = "level1"
temp = input(f"Level ({level}): ")
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

    gamedata = {
        "level":level,
        "players":[{"x":level["player_x"],"y":level["player_y"],"image":f"assets/players/{player1_skin}.png","y_vel":0,"x_vel":0,"anim":"idle","facing":0,"frozen":0,"countdown":5},
        {"x":level["player_x"],"y":level["player_y"],"image":f"assets/players/{player2_skin}.png","y_vel":0,"x_vel":0,"anim":"idle","facing":0,"frozen":0, "countdown":5}]
    }
    print(type(gamedata))

    gamedata_string = json.dumps(gamedata)
    print(gamedata_string)

    zero = "|0|"
    one = "|1|"

    # Game
    # These are duplicated across server and client, very bad
    WIDTH = 1000
    HEIGHT = 700

    tile_size = 76

    anim_speed = 7

    # game variables
    game_state = -1
    # player_id = 0
    gamedata_string = str(client.recv(max_size), "utf-8")
    print(gamedata_string)
    game_data = json.loads(gamedata_string)
    # time.sleep(0.1)
    # print(game_data)
    print(type(game_data["players"]))

    x_offset = 0
    y_offset = 0

    player1_animation = "idle"
    player2_animation = "idle"
    player1_animation_state = 0
    player2_animation_state = 0
    player1_animation_direction = 1
    player2_animation_direction = 1
    animation_counter = 0
    on_ground = 0
    # set this to the number of times the players are able to jump without touching the ground
    num_jumps = 3
    jumps = num_jumps

    player_y_vel = 0
    game_data["players"][player_id]["x_vel"] = 0
    gravity_counter = 0
    friction_counter = 0
    friction_speed = 8
    max_x_vel = 7
    x_vel_change = 1

    punch_range = 50
    punch_speed = 10

    winner = 0

    level_width = len(game_data["level"]['grid'][0]) * tile_size
    level_height = len(game_data["level"]['grid']) * tile_size
    if level_width >= WIDTH:
        max_x_offset = level_width - WIDTH
    else:
        max_x_offset = 0
    if level_width >= HEIGHT:
        max_y_offset = level_height - HEIGHT
    else:
        max_y_offset = 0
    max_char_x = level_width - player_width
    max_char_y = level_height - player_height

    def listen_to_client(client,other_client):
        # Todo: change client function calls to messages
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
            gamedata,anim_data,win_data, freeze_data = messages.parse_message(msg_bytes,gamedata)
            other_client.sendall(msg_bytes)
            if(win_data[0]==1):
                print("someone reached the end")
                game_state = 0
                server.close()


            while game_state != 0:
                clock.tick(60)
                if game_state == -1: # game_data["countdown"]
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                    display_tiles()
                    display_players()
                    if game_data["countdown"] == -1:
                        game_state = 1
                    elif game_data["countdown"] == 0:
                        print_text("GO!",countdown_font,(255,255,255),(WIDTH//2,HEIGHT//2),True,False)
                    elif game_data["countdown"] > 5:
                        print_text("Ready!",countdown_font,(255,255,255),(WIDTH//2,HEIGHT//2),True,False)
                    else:
                        print_text(str(game_data["countdown"]),countdown_font,(255,255,255),(WIDTH//2,HEIGHT//2),True,False)
                    pygame.display.update()
                elif game_state == 1: # main game loop
                    x_offset = int(((int(game_data["players"][player_id]["x"])) / max_char_x) * max_x_offset)
                    y_offset = int(((int(game_data["players"][player_id]["y"])) / max_char_y) * max_y_offset)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            messages.send_message("quit",client)
                            pygame.quit()
                            client.close()
                            quit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP or event.key == pygame.K_w:
                                if not frozen:
                                    if jumps>0:
                                        jumps-=1
                                        if player_id==0:
                                            player1_animation = "jump"
                                            player1_animation_state = 3
                                            player1_animation_direction = 1
                                            messages.send_message("anim 0 jump 3 1|",client)
                                        else:
                                            player2_animation = "jump"
                                            player2_animation_state = 3
                                            player2_animation_direction = 1
                                            messages.send_message("anim 1 jump 3 1|",client)
                                        player_y_vel -= 10
                            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                if not frozen:
                                    messages.send_message(f'fr_attack {game_data["players"][player_id]["x"]-10} {game_data["players"][player_id]["y"]-10}|',client)
                                    freezes.append([game_data["players"][player_id]["x"]-10,game_data["players"][player_id]["y"]-10,0])
                                    if player_id == 0:
                                        if (abs((game_data['players'][0]["x"]) - (game_data['players'][1]["x"])) <= player_width*1.5) and (abs((game_data['players'][0]["y"]) - (game_data['players'][1]["y"])) <= player_height*1.5):
                                            #print("froze a player 1")
                                            messages.send_message(f"freeze 1 1|",client)
                                            game_data['players'][1]["frozen"] = 1;
                                    if player_id == 1:
                                        if (abs((game_data['players'][1]["x"]) - (game_data['players'][0]["x"])) <= player_width*1.5) and (abs((game_data['players'][1]["y"]) - (game_data['players'][0]["y"])) <= player_height*1.5):
                                            #print("froze a player 0")
                                            messages.send_message(f"freeze 0 1|",client)
                                            game_data['players'][0]["frozen"] = 1;
                            if event.key == pygame.K_SPACE:
                                if not frozen:
                                    if player_id == 0:
                                        player1_animation = "punch"
                                        player1_animation_state = 9
                                        player1_animation_direction = 1
                                        messages.send_message("anim 0 punch 9 1|",client)
                                        if game_data['players'][0]['facing'] == 0:
                                            new_x = game_data["players"][player_id]["x"]+player_width
                                            player_y = game_data['players'][player_id]["y"]
                                            if ((new_x + punch_range > game_data['players'][1]["x"]) and (game_data['players'][1]["x"] > game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][1]["y"] - player_height) and (player_y < game_data['players'][1]["y"] + player_height)):
                                                messages.send_message(f"punch 1 {punch_speed}|",client)
                                                player2_animation = "hit"
                                                player2_animation_state = 12
                                                player2_animation_direction = 1
                                                messages.send_message("anim 1 hit 12 1|",client)
                                        elif game_data['players'][0]['facing'] == 1:
                                            new_x = game_data["players"][player_id]["x"]
                                            player_y = game_data['players'][player_id]["y"]
                                            if ((new_x - punch_range < game_data['players'][1]["x"]+player_width) and (game_data['players'][1]["x"] < game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][1]["y"] - player_height) and (player_y < game_data['players'][1]["y"] + player_height)):
                                                messages.send_message(f"punch 1 -{punch_speed}|",client)
                                                player2_animation = "hit"
                                                player2_animation_state = 12
                                                player2_animation_direction = 1
                                                messages.send_message("anim 1 hit 12 1|",client)
                                    if player_id == 1:
                                        player2_animation = "punch"
                                        player2_animation_state = 9
                                        player2_animation_direction = 1
                                        messages.send_message("anim 1 punch 9 1|",client)
                                        if game_data['players'][1]['facing'] == 0:
                                            new_x = (game_data["players"][player_id]["x"])+player_width
                                            player_y = game_data['players'][player_id]["y"]
                                            if ((new_x + punch_range > game_data['players'][0]["x"]) and (game_data['players'][0]["x"] > game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][0]["y"] - player_height) and (player_y < game_data['players'][0]["y"] + player_height)):
                                                messages.send_message(f"punch 0 {punch_speed}|",client)
                                                player1_animation = "hit"
                                                player1_animation_state = 12
                                                player1_animation_direction = 1
                                                messages.send_message("anim 0 hit 12 1|",client)
                                        elif game_data['players'][1]['facing'] == 1:
                                            new_x = game_data["players"][player_id]["x"]
                                            player_y = game_data['players'][player_id]["y"]
                                            if ((new_x - punch_range < game_data['players'][0]["x"]+player_width) and (game_data['players'][0]["x"] < game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][0]["y"] - player_height) and (player_y < game_data['players'][0]["y"] + player_height)):
                                                messages.send_message(f"punch 0 -{punch_speed}|",client)
                                                player1_animation = "hit"
                                                player1_animation_state = 12
                                                player1_animation_direction = 1
                                                messages.send_message("anim 0 hit 12 1|",client)

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        if not frozen:
                            if game_data["players"][player_id]["x_vel"] < max_x_vel:
                                game_data["players"][player_id]["x_vel"] += x_vel_change
                            # new_x = (game_data["players"][player_id]["x"]+player_move_speed)+50
                            # player_y = game_data['players'][player_id]["y"]
                            #
                            # if new_x<(len(game_data["level"]['grid'][0])*tile_size):
                            #     tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                            #     tile_2 = 0
                            #     if player_y % tile_size != 0:
                            #         tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]
                            #
                            #     if tile_1 != 1 and tile_2 != 1:
                            #         game_data["players"][player_id]["x"]+=player_move_speed
                            #         messages.send_message(f"move {player_id} {player_move_speed}|",client)
                            # if player_id == 0:
                            #     game_data["players"][player_id]["facing"] = 0
                            # if player_id == 1:
                            #     game_data["players"][player_id]["facing"] = 0
                            # messages.send_message(f"face {player_id} 0 |",client)
                    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        if not frozen:
                            if game_data["players"][player_id]["x_vel"] > -max_x_vel:
                                game_data["players"][player_id]["x_vel"] -= x_vel_change
                            # new_x = (game_data["players"][player_id]["x"]-player_move_speed)
                            # if new_x>0:
                            #     player_y = game_data['players'][player_id]["y"]
                            #
                            #     tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                            #     tile_2 = 0
                            #     if player_y % tile_size != 0:
                            #         tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]
                            #
                            #     if tile_1 != 1 and tile_2 != 1:
                            #         game_data["players"][player_id]["x"]-=player_move_speed
                            #         messages.send_message(f"move {player_id} -{player_move_speed}|",client)
                            #         if tile_1==2 or tile_2==2:
                            #             print("reached the end")
                            #             messages.send_message(f"win {player_id}|",client)
                            #             winner = player_id
                            #             game_state = 0
                            #         if player_id == 0:
                            #             game_data["players"][player_id]["facing"] = 1
                            #         if player_id == 1:
                            #             game_data["players"][player_id]["facing"] = 1
                            #         messages.send_message(f"face {player_id} 1 |",client)
                    # apply gravity to player
                    if player_y_vel>0:
                        new_y = (game_data["players"][player_id]["y"]+player_y_vel)+50
                        if new_y>len(game_data["level"]["grid"])*tile_size:
                            player_y_vel = 0
                            messages.send_message(f'move y {player_id} {game_data["level"]["player_y"]-game_data["players"][player_id]["y"]}|',client)
                            messages.send_message(f'move {player_id} {game_data["level"]["player_x"]-game_data["players"][player_id]["x"]}|',client)
                            game_data["players"][player_id]["y"] = game_data["level"]["player_y"]
                            game_data["players"][player_id]["x"] = game_data["level"]["player_x"]
                        else:
                            player_x = game_data['players'][player_id]["x"]

                            tile_1 = game_data['level']['grid'][new_y//tile_size][player_x//tile_size]
                            tile_2 = 0
                            if player_x % tile_size != 0:
                                tile_2 = game_data['level']['grid'][new_y//tile_size][(player_x+50)//tile_size]

                            if tile_1 != 1 and tile_2 != 1:
                                game_data["players"][player_id]["y"]+=player_y_vel
                                messages.send_message(f"move y {player_id} {player_y_vel}|",client)
                                on_ground = 0
                                if tile_1==2 or tile_2==2:
                                    print("reached the end")
                                    messages.send_message(f"win {player_id} |",client)
                                    winner = player_id
                                    game_state = 0
                            else:
                                player_y_vel = 0
                                if on_ground == 0:
                                    if player_id == 0:
                                        player1_animation = "land"
                                        player1_animation_state = 6
                                        player1_animation_direction = 1
                                        messages.send_message("anim 0 land 6 1|",client)
                                    else:
                                        player2_animation = "land"
                                        player2_animation_state = 6
                                        player2_animation_direction = 1
                                        messages.send_message("anim 1 land 6 1|",client)
                                on_ground = 1
                                jumps = num_jumps

                    if player_y_vel<0:
                        new_y = (game_data["players"][player_id]["y"]+player_y_vel)
                        player_x = game_data['players'][player_id]["x"]

                        tile_1 = game_data['level']['grid'][new_y//tile_size][player_x//tile_size]
                        tile_2 = 0
                        if player_x % tile_size != 0:
                            tile_2 = game_data['level']['grid'][new_y//tile_size][(player_x+50)//tile_size]

                        if tile_1 != 1 and tile_2 != 1:
                            game_data["players"][player_id]["y"]+=player_y_vel
                            messages.send_message(f"move y {player_id} {player_y_vel}|",client)
                            if tile_1==2 or tile_2==2:
                                messages.send_message(f"win {player_id} |",client)
                                winner = player_id
                                game_state = 0
                        else:
                            player_y_vel = 0

                    gravity_counter+=1
                    if gravity_counter>=2:
                        gravity_counter = 0
                        player_y_vel+=1
                        # player_y_vel = 1


                    if game_data["players"][player_id]["x_vel"]>0:
                        new_x = (game_data["players"][player_id]["x"]+game_data["players"][player_id]["x_vel"])+50

                        player_y = game_data['players'][player_id]["y"]
                        if new_x<(len(game_data["level"]['grid'][0])*tile_size):
                            tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                            tile_2 = 0
                            if player_y % tile_size != 0:
                                tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

                            if tile_1 != 1 and tile_2 != 1:
                                game_data["players"][player_id]["x"]+=game_data["players"][player_id]["x_vel"]
                                messages.send_message(f'move {player_id} {game_data["players"][player_id]["x_vel"]}|',client)
                            else:
                                game_data["players"][player_id]["x_vel"] = 0
                        if tile_1==2 or tile_2==2:
                            print("reached the end")
                            messages.send_message(f"win {player_id}|",client)
                            winner = player_id
                            game_state = 0
                        if player_id == 0:
                            game_data["players"][player_id]["facing"] = 0
                        if player_id == 1:
                            game_data["players"][player_id]["facing"] = 0
                        messages.send_message(f"face {player_id} 0 |",client)


                    if game_data["players"][player_id]["x_vel"]<0:
                        new_x = (game_data["players"][player_id]["x"]+game_data["players"][player_id]["x_vel"])

                        player_y = game_data['players'][player_id]["y"]
                        if new_x>0:
                            tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                            tile_2 = 0
                            if player_y % tile_size != 0:
                                tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

                            if tile_1 != 1 and tile_2 != 1:
                                game_data["players"][player_id]["x"]+=game_data["players"][player_id]["x_vel"]
                                messages.send_message(f'move {player_id} {game_data["players"][player_id]["x_vel"]}|',client)
                            else:
                                game_data["players"][player_id]["x_vel"] = 0
                        if tile_1==2 or tile_2==2:
                            print("reached the end")
                            messages.send_message(f"win {player_id}|",client)
                            winner = player_id
                            game_state = 0
                        if player_id == 0:
                            game_data["players"][player_id]["facing"] = 1
                        if player_id == 1:
                            game_data["players"][player_id]["facing"] = 1
                        messages.send_message(f"face {player_id} 1 |",client)


                        # new_y = (game_data["players"][player_id]["x"]+game_data["players"][player_id]["x_vel"])
                        # player_x = game_data['players'][player_id]["x"]
                        #
                        # player_y = game_data['players'][player_id]["y"]
                        #
                        # tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                        # tile_2 = 0
                        # if player_y % tile_size != 0:
                        #     tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]
                        #
                        # if tile_1 != 1 and tile_2 != 1:
                        #     game_data["players"][player_id]["x"]+=game_data["players"][player_id]["x_vel"]
                        #     messages.send_message(f"move {player_id} +{game_data["players"][player_id]["x_vel"]}|",client)
                        # else:
                        #     player_y_vel = 0
                        #     if tile_1==2 or tile_2==2:
                        #         print("reached the end")
                        #         messages.send_message(f"win {player_id}|",client)
                        #         winner = player_id
                        #         game_state = 0
                        #     if player_id == 0:
                        #         game_data["players"][player_id]["facing"] = 1
                        #     if player_id == 1:
                        #         game_data["players"][player_id]["facing"] = 1
                        #     messages.send_message(f"face {player_id} 1 |",client)

                    friction_counter+=1
                    if friction_counter>=friction_speed:
                        friction_counter = 0
                        if game_data["players"][player_id]["x_vel"] > 0:
                            game_data["players"][player_id]["x_vel"]-=1
                        elif game_data["players"][player_id]["x_vel"] < 0:
                            game_data["players"][player_id]["x_vel"]+=1


                    animation_counter += 1
                    if animation_counter == anim_speed:
                        if not game_data["players"][0]["frozen"]:
                            if player1_animation == "idle":
                                player1_animation_state += player1_animation_direction
                                if player1_animation_state == 2:
                                    player1_animation_direction = -1
                                if player1_animation_state == 0:
                                    player1_animation_direction = 1
                            elif player1_animation == "jump":
                                player1_animation_state += player1_animation_direction
                                if player1_animation_state == 5:
                                    player1_animation_direction = -1
                                if player1_animation_state < 3:
                                    player1_animation = "idle"
                                    player1_animation_state = 0
                                    player1_animation_direction = 1
                                    #messages.send_message("anim 0 idle 0 1|",client)
                            elif player1_animation == "land":
                                player1_animation_state += player1_animation_direction
                                if player1_animation_state == 8:
                                    player1_animation_direction = -1
                                if player1_animation_state < 6:
                                    player1_animation = "idle"
                                    player1_animation_state = 0
                                    player1_animation_direction = 1
                                    #messages.send_message("anim 0 idle 0 1|",client)
                            elif player1_animation == "punch":
                                player1_animation_state += player1_animation_direction
                                if player1_animation_state == 11:
                                    player1_animation_direction = -1
                                if player1_animation_state < 9:
                                    player1_animation = "idle"
                                    player1_animation_state = 0
                                    player1_animation_direction = 1
                            elif player1_animation == "hit":
                                player1_animation = "idle"
                                player1_animation_state = 0
                                player1_animation_direction = 1
                        if not game_data["players"][1]["frozen"]:
                            if player2_animation == "idle":
                                player2_animation_state += player2_animation_direction
                                if player2_animation_state == 2:
                                    player2_animation_direction = -1
                                if player2_animation_state == 0:
                                    player2_animation_direction = 1
                            elif player2_animation == "jump":
                                player2_animation_state += player2_animation_direction
                                if player2_animation_state == 5:
                                    player2_animation_direction = -1
                                if player2_animation_state < 3:
                                    player2_animation = "idle"
                                    player2_animation_state = 0
                                    player2_animation_direction = 1
                                    #messages.send_message("anim 1 idle 0 1|",client)
                            elif player2_animation == "land":
                                player2_animation_state += player2_animation_direction
                                if player2_animation_state == 8:
                                    player2_animation_direction = -1
                                if player2_animation_state < 6:
                                    player2_animation = "idle"
                                    player2_animation_state = 0
                                    player2_animation_direction = 1
                                    #messages.send_message("anim 1 idle 0 1|",client)
                            elif player2_animation == "punch":
                                player2_animation_state += player2_animation_direction
                                if player2_animation_state == 11:
                                    player2_animation_direction = -1
                                if player2_animation_state < 9:
                                    player2_animation = "idle"
                                    player2_animation_state = 0
                                    player2_animation_direction = 1
                            elif player2_animation == "hit":
                                player2_animation = "idle"
                                player2_animation_state = 0
                                player2_animation_direction = 1
                        animation_counter = 0

                    if frozen:
                        if freeze_counter > freeze_duration:
                            game_data["players"][player_id]["frozen"] = 0
                            messages.send_message(f"freeze {player_id} 0",client)
                            frozen = 0
                            freeze_counter = 0
                        freeze_counter += 1
    client1.sendall(bytes(gamedata_string,"utf-8"))
    client2.sendall(bytes(gamedata_string,"utf-8"))

    time.sleep(1.0)

    client1_thread = threading.Thread(target = lambda:listen_to_client(client1,client2,0))
    client2_thread = threading.Thread(target = lambda:listen_to_client(client2,client1,1))

    client1.sendall(zero.encode())
    client2.sendall(one.encode())

    time.sleep(0.1)

    countdown = 8
    while countdown > 0:
        time.sleep(1)
        messages.send_message("countdown|",client1)
        messages.send_message("countdown|",client2)
        countdown-=1

    client1_thread.start()
    client2_thread.start()



    # Todo: Send to client as messages
    display_tiles()
    display_players()
    update_freezes()
    pygame.display.update()

load_server(address,max_size)