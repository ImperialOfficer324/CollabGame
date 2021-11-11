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
        pygame.transform.scale(pygame.image.load("assets/tiles/ground.png"),(50,50))]

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(450,100)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(450,100))]

def display_tiles():
    for row_count,row in enumerate(game_data["level"]["grid"]):
        for col_count,column in enumerate(row):
            window.blit(tiles[column],(col_count * 50,row_count * 50))
    return 1

def display_players():
    p1 = pygame.Surface((80, 80))
    p1.blit(players[1], (0, 0), (0, 0, 50, 50))
    p0 = pygame.Surface((80, 80))
    p0.blit(players[0], (0, 0), (0, 0, 50, 50))
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
            messages.send_message(f"move {player_id} 1",client)
            #send_message("quit",client)
            game_data["players"][player_id]["x"]+=1
        if keys[pygame.K_LEFT]:
            messages.send_message(f"move {player_id} -1",client)
            #send_message("quit",client)
            game_data["players"][player_id]["x"]-=1
        display_tiles()
        display_players()
        pygame.display.update()

#close client
client.close()
