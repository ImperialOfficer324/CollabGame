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

#setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

player_id = int(client.recv(28).decode())

tiles = [pygame.transform.scale(pygame.image.load("assets/tiles/sky.png"),(50,50)),
        pygame.transform.scale(pygame.image.load("assets/tiles/ground.png"),(50,50)),
        pygame.transform.scale(pygame.image.load("assets/tiles/gate.png"),(50,50))]

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(450,100)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(450,100))]

def display_tiles():
    for row_count,row in enumerate(game_data["level"]["grid"]):
        for col_count,column in enumerate(row):
            window.blit(tiles[column],(col_count * 50,row_count * 50))
    return 1

player1_animation = "idle"
player2_animation = "idle"
player1_animation_state = 0
player2_animation_state = 0
player1_animation_direction = 1
player2_animation_direction = 1
animation_counter = 0

def display_players():
    if player1_animation == "idle":
        offset = 0
    p1 = pygame.Surface((50, 50))
    p1.set_colorkey((0,0,0))
    p1.blit(players[1], (0, 0), ((player2_animation_state + offset) * 50, 0, 50, 50))
    p0 = pygame.Surface((50, 50))
    p0.set_colorkey((0,0,0))
    p0.blit(players[0], (0, 0), ((player1_animation_state + offset) * 50, 0, 50, 50))
    if player_id == 0:
        window.blit(p1,(int(game_data["players"][1]["x"]),int(game_data["players"][1]["y"])))
        window.blit(p0,(int(game_data["players"][0]["x"]),int(game_data["players"][0]["y"])))
    else:
        window.blit(p0,(int(game_data["players"][0]["x"]),int(game_data["players"][0]["y"])))
        window.blit(p1,(int(game_data["players"][1]["x"]),int(game_data["players"][1]["y"])))

def listen_to_server(client):
    global game_data
    while game_state:
        msg = client.recv(max_size)
        game_data = messages.parse_message(msg,game_data)
        print(f'recieved message {str(msg,"utf-8")}')

server_listener = threading.Thread(target=lambda:listen_to_server(client))
server_listener.start()

while game_state != 0:
    clock.tick(60)
    if game_state == 1: # main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                messages.send_message("quit",client)
                client.close()
                pygame.quit()
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            new_x = (game_data["players"][player_id]["x"]+1)+50
            player_y = game_data['players'][player_id]["y"]

            tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//50][new_x//50]
            #tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//50][new_x//50]

            print(f"the tile at {new_x//50},{player_y//50} is {tile_1}")
            #print(f"the tile at {new_x//50},{(player_y+50)//50} is {tile_2}")

            if tile_1 != 1:# and tile_2 != 1:
                game_data["players"][player_id]["x"]+=1
                messages.send_message(f"move {player_id} 1",client)
        elif keys[pygame.K_LEFT]:
            new_x = (game_data["players"][player_id]["x"]-1)
            player_y = game_data['players'][player_id]["y"]

            tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//50][new_x//50]
            #tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//50][new_x//50]

            print(f"the tile at {new_x//50},{player_y//50} is {tile_1}")
            #print(f"the tile at {new_x//50},{(player_y+50)//50} is {tile_2}")

            if tile_1 != 1:# and tile_2 != 1:
                game_data["players"][player_id]["x"]-=1
                messages.send_message(f"move {player_id} -1",client)
            messages.send_message(f"move {player_id} 1",client)
            #send_message("quit",client)
            game_data["players"][player_id]["x"]+=1
        animation_counter += 1
        if animation_counter == 10:
            if player1_animation == "idle":
                if player1_animation_state == 2:
                    player1_animation_direction = -1
                if player1_animation_state == 0:
                    player1_animation_direction = 1
                player1_animation_state += player1_animation_direction
            if player2_animation == "idle":
                if player2_animation_state == 2:
                    player2_animation_direction = -1
                if player2_animation_state == 0:
                    player2_animation_direction = 1
                player2_animation_state += player2_animation_direction
            animation_counter = 0
            
        display_tiles()
        display_players()
        pygame.display.update()

#close client
client.close()
