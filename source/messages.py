import socket
def send_message(event,client):
    client.sendall(bytes(event,"utf-8"))

def parse_message(message,game_data):
    message = message.decode("utf-8")
    anim_data = [0,0]
    win_data = [0,0]
    freeze_data = [0,0,0]
    for i in message.split("|"):
        game_data, temp, win_data_temp, freeze_data_temp = _parse_message(i,game_data)
        if temp[0]!=0:
            anim_data = temp
        if win_data_temp[0]!=0:
            win_data = win_data_temp
        if freeze_data_temp[0]!=0:
            freeze_data = freeze_data_temp
    return game_data, anim_data, win_data, freeze_data

def _parse_message(message,game_data):
    anim_changed = 0
    player_id = 0
    win = 0
    is_freeze = 0
    freeze_x = 0
    freeze_y = 0
    # print(f'parsing message {message}')
    if "move " in message:
        message = message.replace("move ","")
        if "y" in message:
            message = message.replace("y ","")
            player_id = int(message.split(" ")[0])
            val = int(message.split(" ")[1])
            game_data["players"][player_id]["y"]+=val

            # print(game_data["players"][player_id]["y"])
        else:
            player_id = int(message.split(" ")[0])
            val = int(message.split(" ")[1])
            game_data["players"][player_id]["x"]+=val
    elif "anim " in message:
        message = message.replace("anim ","")
        player_id = int(message.split(" ")[0])
        anim = str(message.split(" ")[1])
        state = int(message.split(" ")[2])
        direction = int(message.split(" ")[3])
        game_data["players"][player_id]["anim"] = [anim, state, direction]
        anim_changed = 1
    elif "face " in message:
        message = message.replace("face ","")
        player_id = int(message.split(" ")[0])
        val = int(message.split(" ")[1])
        game_data["players"][player_id]["facing"]=val
    elif "win" in message:
        message = message.replace("win ","")
        win = 1
        player_id = int(message.split(" ")[0])
    elif "freeze " in message:
        message = message.replace("freeze ","")
        player_id = int(message.split(" ")[0])
        frozen = int(message.split(" ")[1])
        game_data["players"][player_id]["frozen"]=frozen
    elif "fr_attack " in message: # this conrols the animation for the freeze attack
        message = message.replace("fr_attack ","");
        is_freeze = 1
        freeze_x = int(message.split(" ")[0])
        freeze_y = int(message.split(" ")[1])
    return game_data, [anim_changed,player_id], [win,player_id], [is_freeze,freeze_x,freeze_y]