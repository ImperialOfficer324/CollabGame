#imports
import socket
import pygame
import json
import os
import messages
import threading

#constants
WIDTH = 1000
HEIGHT = 700

tile_size = 76

#setup connection with server
server_address=("localhost", 6789)
max_size=10000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
#data=client.recv(max_size)

#game variables
game_state = 1
#player_id = 0
gamedata_string = str(client.recv(max_size), "utf-8")
game_data = json.loads(gamedata_string)
print(game_data)

x_offset = 0
y_offset = 0

#setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

player_id = int(client.recv(28).decode())

tiles = [pygame.transform.scale(pygame.image.load("assets/tiles/sky.png"),(tile_size,tile_size)),
        pygame.transform.scale(pygame.image.load("assets/tiles/ground.png"),(tile_size,tile_size)),
        pygame.transform.scale(pygame.image.load("assets/tiles/gate.png"),(tile_size,tile_size))]

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(450,100)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(450,100))]

def display_tiles():
    for row_count,row in enumerate(game_data["level"]["grid"]):
        for col_count,column in enumerate(row):
            window.blit(tiles[column],((col_count * tile_size)-x_offset,(row_count * tile_size)-y_offset))
    return 1

player1_animation = "idle"
player2_animation = "idle"
player1_animation_state = 0
player2_animation_state = 0
player1_animation_direction = 1
player2_animation_direction = 1
animation_counter = 0

player_y_vel = 0
gravity_counter = 0

def display_players():
    offset = 0
    if player1_animation == "idle":
        offset = 0
    p1 = pygame.Surface((50, 50))
    p1.set_colorkey((0,0,0))
    p1.blit(players[1], (0, 0), ((player2_animation_state + offset) * 50, 0, 50, 50))
    p0 = pygame.Surface((50, 50))
    p0.set_colorkey((0,0,0))
    p0.blit(players[0], (0, 0), ((player1_animation_state + offset) * 50, 0, 50, 50))
    if player_id == 0:
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
    else:
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))

def listen_to_server(client):
    global game_data
    global game_state
    while game_state:
        msg = client.recv(max_size)
        if(str(msg,"utf-8") == "quit"):
            print("quit")
            game_state = 0
        game_data = messages.parse_message(msg,game_data)
        # print(f'recieved message {str(msg,"utf-8")}')

server_listener = threading.Thread(target=lambda:listen_to_server(client))
server_listener.start()

while game_state != 0:
    clock.tick(60)
    if game_state == 1: # main game loop
        x_offset = int(game_data["players"][player_id]["x"])//2
        y_offset = int(game_data["players"][player_id]["y"])//2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                messages.send_message("quit",client)
                pygame.quit()
                client.close()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if player_id==0:
                        player1_animation = "jump"
                        player1_animation_state = 3
                        player1_animation_direction = 1
                    else:
                        player2_animation = "jump"
                        player2_animation_state = 3
                        player2_animation_direction = 1
                    player_y_vel -= 10
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            new_x = (game_data["players"][player_id]["x"]+1)+50
            player_y = game_data['players'][player_id]["y"]

            tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
            tile_2 = 0
            if player_y % tile_size != 0:
                tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

            if tile_1 != 1 and tile_2 != 1:
                game_data["players"][player_id]["x"]+=1
                messages.send_message(f"move {player_id} 1|",client)
        elif keys[pygame.K_LEFT]:
            new_x = (game_data["players"][player_id]["x"]-1)
            player_y = game_data['players'][player_id]["y"]

            tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
            tile_2 = 0
            if player_y % tile_size != 0:
                tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

            if (tile_1 != 1 and tile_2 != 1) and new_x>0:
                game_data["players"][player_id]["x"]-=1
                messages.send_message(f"move {player_id} -1|",client)

        # apply gravity to player
        if player_y_vel!=0:
            new_y = (game_data["players"][player_id]["y"]+player_y_vel)+50
            player_x = game_data['players'][player_id]["x"]

            tile_1 = game_data['level']['grid'][new_y//tile_size][player_x//tile_size]
            tile_2 = 0
            if player_x % tile_size != 0:
                tile_2 = game_data['level']['grid'][new_y//tile_size][(player_x+50)//tile_size]

            if tile_1 != 1 and tile_2 != 1:
                game_data["players"][player_id]["y"]+=player_y_vel
                messages.send_message(f"move y {player_id} {player_y_vel}|",client)
            else:
                player_y_vel = 0
        gravity_counter+=1
        if gravity_counter>=2:
            gravity_counter = 0
            player_y_vel+=1
            # player_y_vel = 1

        animation_counter += 1
        if animation_counter == 10:
            if player1_animation == "idle":
                if player1_animation_state == 2:
                    player1_animation_direction = -1
                if player1_animation_state == 0:
                    player1_animation_direction = 1
                player1_animation_state += player1_animation_direction
            elif player1_animation == "jump":
                if player1_animation_state == 5:
                    player1_animation_direction = -1
                if player1_animation_state < 3:
                    player1_animation = "idle"
                player1_animation_state += player1_animation_direction


            if player2_animation == "idle":
                if player2_animation_state == 2:
                    player2_animation_direction = -1
                if player2_animation_state == 0:
                    player2_animation_direction = 1
                player2_animation_state += player2_animation_direction
            elif player2_animation == "jump":
                if player2_animation_state == 5:
                    player2_animation_direction = -1
                if player2_animation_state < 3:
                    player2_animation = "idle"
                player2_animation_state += player2_animation_direction
            animation_counter = 0

        display_tiles()
        display_players()
        pygame.display.update()

#close client
client.close()
pygame.quit()
quit()
