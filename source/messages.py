import socket
def send_message(event,client):
    client.sendall(bytes(event,"utf-8"))

def parse_message(message,game_data):
    message = message.decode("utf-8")
    anim_data = [0,0]
    for i in message.split("|"):
        game_data, temp = _parse_message(i,game_data)
        if temp[0]!=0:
            anim_data = temp
    return game_data, anim_data

def _parse_message(message,game_data):
    anim_changed = 0
    player_id = 0
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
    elif "freeze " in message:
        message = message.replace("freeze ","")
        player_id = int(message.split(" ")[0])
        game_data["players"][player_id]["frozen"]=1
    return game_data, [anim_changed,player_id]
