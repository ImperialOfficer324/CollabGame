#imports
import socket
import pygame
import json
import os

#constants
WIDTH = 1000
HEIGHT = 700

#setup connection with server
server_address=("localhost", 6789)
max_size=1000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
#data=client.recv(max_size)

#game variables
game_state = 1
gamedata_string = str(client.recv(max_size), "utf-8")
game_data = json.loads(gamedata_string)
print(game_data)

#setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock() 
#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

tiles = [pygame.transform.scale(pygame.image.load(f"assets/tiles/sky.png"),(50,50)),
        pygame.transform.scale(pygame.image.load(f"assets/tiles/ground.png"),(50,50))]

def display_tiles():
    for row_count,row in enumerate(game_data["grid"]):
        for col_count,column in enumerate(row):
            print(column)
            window.blit(tiles[column],(col_count * 50,row_count * 50))
    return 1

while game_state != 0:
    clock.tick(60)
    if game_state == 1: # main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.close()
                pygame.quit()
                quit()
        display_tiles()
        pygame.display.update()

#close client
client.close()
