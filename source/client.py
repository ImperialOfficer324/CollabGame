#imports
import socket
import pygame

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

#setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

while game_state != 0:
    if game_state == 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.close()
                pygame.quit()
                quit()
        pygame.display.update()

#close client
client.close()