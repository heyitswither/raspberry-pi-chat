
# raspberry-pi-chat

This is a websocket client for the raspberry pi group chat. You can join the discord [here](http://discord.io/raspberrypi).

You can find the documentation for the specifications of packet format and other details for creating your own client [here](http://rwci.ml)

~~My old, non-working clients have been moved to the [old-version branch](https://github.com/heyitswither/raspberry-pi-chat/tree/old-version)~~

I privated my old repo due to it not having a license.

## Installation

1. Clone this repository to your computer using `git clone http://github.com/heyitswither/raspberry-pi-chat`
2. Run `python3.5 -m pip install -r requirements.txt` to install dependancies
3. Edit `config.json` with your credentials and the server address
4. Any option, besides useSHA512 or custom, can be set to null to prompt everytime
5. Run with `python3.5 client.py`

## Client Commands

- `|w <user> <message>` sends a private message
- `|quit` disconnects from the server
- `|users` shows the online users
- `|raw <raw_json>` sends raw json to the server
- `|clear` clears the chat
- `|eval <python_code>` evalutes python code
- `|basheval <baash_code>` evalutes bash code
- `|help` show these commands

## Future Plans

- a server to compliment my client
- a light version of the server and client (light as in it won't do much, the server and client are already light on resources) 
