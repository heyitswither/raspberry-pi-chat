
# raspberry-pi-chat

This is a websocket client for the raspberry pi group chat. You can join the discord [here](http://discord.io/raspberrypi).

You can find the documentation for the specifications of packet format and other details for creating your own client [here](https://gist.github.com/AnonymousDapper/33f45f7bf27151542330ce3a67658ba0)

## Installation

1. Clone this repository to your computer using `git clone http://github.com/heyitswither/raspberry-pi-chat`
2. `cd raspberry-pi-chat`
2. Run `pip install -r requirements.txt` to install dependancies
3. Edit `config.json` with your credentials and the server address
4. Any option, besides useSHA512 or custom, can be set to null to prompt everytime
5. Run with `python client.py`

## Configuration

Here is an example of how to use the config file

You should not need to edit this file as all settings can be changed from the client.

These values can be set from inside the client with the command `/eval config.set(setting, value)` but serverAddress, username, and password require you to restart the client for it to change.

```json
{
  "serverAddress": "ws://localhost:5000",
  "username": "test",
  "password": "test",
  "blocked": [
    "Cyberbriiian"
  ],
  "command_prefix": "/"
}
```

"serverAddress" is a string that holds the websocket server Address

"username" is a string that holds your username on the chat

"password" is a string that holds your password on the chat

"blocked" is a list of blocked users

"command_prefix" is the prefix for client commands

Any of these values can be set to `null` to prompt every time

## Client Commands

- `/w <user> <message>`
    send a private message
- `/raw <raw_json>`
    send raw json
- `/users`
    show online users
- `/eval <code>`
    evaluate python code
- `/exec <command>`
    executes bash commands
- `/clear`
    clears the chat
- `/quit`
    disconnect from the server
- `/shrug`
    appends ¯\\\_(ツ)\_/¯ to your message
- `/block <user>`
    blocks a user
- `/unblock <user>`
    unblocks a user
- `/join <channel>`
    joins a channel
- `/channels`
    lists the channels on the server
- `/help`
    shows these commands

The prefix '/' is the default, but can be changed with the command `/eval config.set('command_prefix', 'your_prefix_here')` and does not require a restart.

## Dependencies

[Pretty Output](https://github.com/Aareon/prettyoutput)
[RWCI.py](https://github.com/heyitswither/rwci.py)
