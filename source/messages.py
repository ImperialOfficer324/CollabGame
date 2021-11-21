import socket
def send_message(event,client):
    client.sendall(bytes(event,"utf-8"))

def parse_message(message,game_data):
    message = message.decode("utf-8")
    for i in message.split("|"):
        game_data = _parse_message(i,game_data)
    return game_data

def _parse_message(message,game_data):
    print(f'parsing message {message}')
    if "move " in message:
        message = message.replace("move ","")
        if "y" in message:
            message = message.replace("y ","")
            player_id = int(message.split(" ")[0])
            val = int(message.split(" ")[1])
            game_data["players"][player_id]["y"]+=val

            print(game_data["players"][player_id]["y"])
        else:
            player_id = int(message.split(" ")[0])
            val = int(message.split(" ")[1])
            game_data["players"][player_id]["x"]+=val
    return game_data