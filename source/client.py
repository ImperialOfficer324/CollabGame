#imports
import socket
import pygame
import json
import os
import messages
import threading
import time

# constants
WIDTH = 1000
HEIGHT = 700

tile_size = 76

anim_speed = 7

#setup connection with server
# server_address=("localhost", 6789)
IP = 'localhost'
port = 6789

temp_ip = input(f"IP Address ({IP}): ")
if temp_ip!="":
    try:
        IP = int(temp_ip)
    except ValueError:
        IP = temp_ip

temp_port = input(f"Port ({port}): ")
if temp_port!="":
    port = int(temp_port)

server_address = (IP,port)

max_size=1000000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
#data=client.recv(max_size)


#setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

player_id = int(client.recv(28).decode().split("|")[1])

time.sleep(0.5)

tiles = [pygame.transform.scale(pygame.image.load("assets/tiles/sky.png"),(tile_size,tile_size)),
        pygame.transform.scale(pygame.image.load("assets/tiles/ground.png"),(tile_size,tile_size)),
        pygame.transform.scale(pygame.image.load("assets/tiles/gate.png"),(tile_size,tile_size))]

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(650,100)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(650,100))]

freeze_vfx_img = pygame.transform.scale(pygame.image.load("assets/misc/freeze.png"),(100,50))
freeze_vfx = []
freeze_vfx_1 = pygame.Surface((50, 50))
freeze_vfx_1.set_colorkey((0,0,0))
freeze_vfx_1.blit(freeze_vfx_img, (0, 0), (0, 0, 50, 50))
freeze_vfx_2 = pygame.Surface((50, 50))
freeze_vfx_2.set_colorkey((0,0,0))
freeze_vfx_2.blit(freeze_vfx_img, (0, 0), (50, 0, 50, 50))

freeze_vfx.append(freeze_vfx_1)
freeze_vfx.append(freeze_vfx_2)

# all five frames of the attack are in this image
freeze_attack = pygame.transform.scale(pygame.image.load("assets/misc/attack_freeze.png"),(175*2,70))

# creating a list allows us to have as many freezes as we need on the screen. When they're gone, they simply get removed from the list
# this information is organized as [x,y,state]
freezes = []

def display_tiles():
    window.fill((0,0,0));
    for row_count,row in enumerate(game_data["level"]["grid"]):
        for col_count,column in enumerate(row):
            window.blit(tiles[column],((col_count * tile_size)-x_offset,(row_count * tile_size)-y_offset))
    return 1


def display_win_screen():
    global winner
    global x_offset, y_offset
    fadeout = pygame.Surface((WIDTH,HEIGHT))
    fadeout = fadeout.convert()
    fadeout.fill((0,0,0))
    fadeout.set_alpha(250)
    displaying_anim = True
    fireworks = pygame.transform.scale(pygame.image.load("assets/misc/fireworks.png"),(3040,380))
    crown = pygame.transform.scale(pygame.image.load('assets/misc/crown.png'),(250,300))
    firework_state = 0
    counter = 0
    darkness = 0
    fade = -1
    fw = pygame.Surface((380, 380))
    fw.set_colorkey((0,0,0))
    while displaying_anim:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                quit()
        # x_offset =
        display_tiles()
        display_players()
        window.blit(fadeout,(0,0))
        if darkness>0 and fade==1:
            darkness-=1
            fadeout.set_alpha(darkness)
        elif fade==-1 and darkness<250:
            darkness+=1
            fadeout.set_alpha(darkness)
        elif darkness<=0 and fade == 1:
            fade = 0
        elif darkness>=250 and fade == -1:
            displaying_anim = False
        elif fade == 0:
            counter+=1
            if counter>50:
                fade = -1
        pygame.display.update()

    display_winner = True
    counter = 0
    p1 = pygame.Surface((250, 250))
    p1.set_colorkey((0,0,0))
    p1.blit(pygame.transform.scale(players[1],(250*13,500)), (0, 0), (0, 0, 250, 250))
    p0 = pygame.Surface((250, 250))
    p0.set_colorkey((0,0,0))
    p0.blit(pygame.transform.scale(players[0],(250*13,500)), (0, 0), (0, 0, 250, 250))
    while display_winner:
        clock.tick(60)
        window.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                quit()
        window.blit(p0,(200,250))
        window.blit(p1,(550,250))
        if winner == 0:
            window.blit(crown,(200,200))
        else:
            window.blit(crown,(550,200))
        fw.fill((0,0,0,0))
        if firework_state<9:
            fw.blit(fireworks, (0, 0), ((firework_state) * 380, 0, 380, 380))
            if winner == 0:
                window.blit(fw,(200-65,250-65))
            else:
                window.blit(fw,(550-65,250-65))
            counter+=1
            if counter>anim_speed:
                firework_state+=1
                counter = 0
        pygame.display.update()

frozen = 0
freeze_counter = 0
freeze_duration = 30

def display_players():
    p1 = pygame.Surface((50, 50))
    p1.set_colorkey((0,0,0))
    p1.blit(players[1], (0, 0), ((player2_animation_state) * 50, (game_data["players"][1]["facing"]) * 50, 50, 50))
    p0 = pygame.Surface((50, 50))
    p0.set_colorkey((0,0,0))
    p0.blit(players[0], (0, 0), ((player1_animation_state) * 50, (game_data["players"][0]["facing"]) * 50, 50, 50))
    if player_id == 0:
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        if game_data["players"][1]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][1]["facing"]],(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        if game_data["players"][0]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][0]["facing"]],(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
    else:
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        if game_data["players"][0]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][0]["facing"]],(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        if game_data["players"][1]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][1]["facing"]],(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))

freezes_counter = 0
def update_freezes():
    global freezes_counter
    freezes_counter+=1
    img = pygame.Surface((70, 70))
    img.set_colorkey((0,0,0))
    for fr in freezes:
        img.blit(freeze_attack, (0, 0), (fr[2] * 70, 0, 70, 70))
        window.blit(img,(fr[0]-x_offset,fr[1]-y_offset))
        if freezes_counter>anim_speed//2:
            fr[2]+=1
            if fr[2]>4:
                freezes.remove(fr)
    if freezes_counter>anim_speed//2:
        freezes_counter = 0

def listen_to_server(client):
    global player1_animation
    global player2_animation
    global player1_animation_state
    global player2_animation_state
    global player1_animation_direction
    global player2_animation_direction
    global game_data
    global game_state
    global winner
    global frozen
    global freeze_counter
    global freezes
    while game_state:
        msg = client.recv(max_size)
        if(str(msg,"utf-8") == "quit"):
            print("quit")
            game_state = 0
        game_data,anim_data,win_data, freeze_data = messages.parse_message(msg,game_data)
        if anim_data[0]==1:
            if anim_data[1]==0:
                player1_animation = game_data["players"][0]["anim"][0]
                player1_animation_state = game_data["players"][0]["anim"][1]
                player1_animation_direction = game_data["players"][0]["anim"][2]
            else:
                player2_animation = game_data["players"][1]["anim"][0]
                player2_animation_state = game_data["players"][1]["anim"][1]
                player2_animation_direction = game_data["players"][1]["anim"][2]
        if win_data[0]==1:
            winner = win_data[1]
            game_state = 0

        if game_data["players"][player_id]["frozen"] and not frozen:
            # print("I got frozen")
            frozen = 1
            freeze_counter = 0

        # print(freeze_data[0])
        if freeze_data[0]==1: # if we need to play the animation
            print("initiating freeze")
            freezes.append([freeze_data[1],freeze_data[2],0])

game_data["countdown"] = 7
server_listener = threading.Thread(target=lambda:listen_to_server(client))
server_listener.start()

player_width = 50
player_height = 50

countdown_font = pygame.font.Font("assets/fonts/mainfont.ttf",120)

def print_text(text,font,color,coordinates,center = False,anti_alias = True):
    text_surface = font.render(text,anti_alias,color)
    if center:
        text_rect = text_surface.get_rect()
        text_rect.center = (coordinates)
        window.blit(text_surface,text_rect)
    else:
        window.blit(text_surface,coordinates)


display_win_screen()

#close client
client.close()
pygame.quit()
quit()
