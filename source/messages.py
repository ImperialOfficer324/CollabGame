def send_message(event,client):
    client.sendall(event.encode())

def parse_message(message,game_data):
    if "move " in message:
        message = message.replace("move ","")
        player_id = int(message.split(" ")[0])
        val = int(message.split(" ")[1])
        game_data["players"][player_id]["x"]+=val
    return game_data