
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

## Configuration

Here is an example of how to use the config file

```json
{
  "custom": true,
  "serverAddress": "ws://chat.rwci.ml:5000",
  "username": "test",
  "password": "",
  "useSHA512": true,
  "colors": [
    {
      "username": "wither",
      "color": "cyan"
    },
    {
      "username": "zach",
      "color": "red"
    }
  ]
}
```

"custom" is to prove that you changed values in the config file
"serverAddress" is a string that holds the websocket server Address, can be set to null
"username" is a string that holds your username on the chat, can be set to null
"password" is a string that holds your password on the chat, can be set to null
"useSHA512" is for toggling the use of SHA512 for password hashing
"colors" is an array of users and their colors (displayed in chat)

"color" is "colors" array must be one of the following: "black", "red", "green", "yellow", "blue", "magenta", or "cyan"

Any value (that is able to be set to null) can be set to null to prompt you every time.

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
