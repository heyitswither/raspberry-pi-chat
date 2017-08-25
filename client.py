import asyncio  # used for multiple threads
import hashlib  # used for hashing passwords
import json  # used for formatting
import os  # used for clearing the screen
import subprocess
import sys  # used for exiting
from datetime import datetime  # used for timestamps
# used for inputting passwords, doesnt display the password onscreen
from getpass import getpass

import rwci
from utils import prettyoutput as po  # used for pretty output to the console

previousMsg = None  # the previosu message received, for spam prevention
users_list = []  # list of online users
loggedIn = False
user_colors = {}

server_stat = po.custom(string="{}", color_code="red",
                        stat_msg="[SERVER]", prn_out=False)
auth_stat = po.custom(string="{}", color_code="red",
                      stat_msg="[AUTH]", prn_out=False)
join_stat = po.custom(string="{}", color_code="green",
                      stat_msg="[CONNECT]", prn_out=False)
quit_stat = po.custom(string="{}", color_code="yellow",
                      stat_msg="[DISCONNECT]", prn_out=False)
dm_stat = po.custom(string="{}", color_code="cyan",
                    stat_msg="|{} > {}|", prn_out=False)
msg_stat = po.custom(string="{}", color_code="reset",
                     stat_msg="<{}>", prn_out=False)

try:
  with open('config.json') as fileIn:
    config = json.load(fileIn)  # imports config.json as config
except FileNotFoundError:  # creates config if not found
  with open('config.json', 'w+') as fileIO:
    config = {"custom": False, "serverAddress": None, "username": None, "password": None,
              "useSHA512": False, "colors": [{"username": "username", "color": "color"}]}
    json.dump(config, fileIO, indent=2)

if not config['custom']:  # used for making sure the user has looked over config.json
  print("Please read and change any necessary options in the config.json file.")
  print("You must also have read the README.md file to the format of the options.")
  print("If you have done these things, please change custom to true in the config.json file.")
  sys.exit()

for user in config['colors']:
  user_colors[user['username']] = user['color']

if not config['serverAddress'] is None:
  client = rwci.Client(gateway_url=config['serverAddress'])
else:
  server = input('Server Address: ')
  client = rwci.Client(gateway_url=server)


async def get_color(username):
  if username in user_colors:
    if not user_colors[username] in po.color:
      raise ValueError(f'{user_colors[username]} is not a valid color')
    return po.color[user_colors[username]] + username + "\033[39m"
  else:
    return username


@client.event
async def on_ready():
  print("Successfully connected to the server")
  asyncio.ensure_future(input_message())


@client.event
async def on_message(message):
  print(msg_stat.format(await get_color(message.author), message.content))


@client.event
async def on_user_list(user_list):
  if not len(client.user_list) == 0:
    print("Online Users:\n{}".format(', '.join(client.user_list)))
  else:
    print("No one is online :(")


@client.event
async def on_join(username):
  print(join_stat.format(await get_color(username)))


@client.event
async def on_quit(username):
  print(quit_stat.format(await get_color(username)))


@client.event
async def on_broadcast(message):
  print(server_stat.format(message))


@client.event
async def on_direct_message(message):
  print(dm_stat.format(await get_color(message.author), await get_color(client.username), message.content))


async def parse_command(message):
  """
  For parsing client-side comamnds.

  Takes a message that is a comamnd as a parameter and returns the output of that message.
  """
  if message.split()[0] == "|w":  # private messages
    if message.split()[1] in client.user_list and not message.split()[1] == client.username:
      message_content = " ".join(message.split()[2:])
      message_recipient = message.split()[1]
      await client.send_dm(message_content, message_recipient)
    elif message.split()[1] == client.username:
      print("You can't send a private message to yourself!")
    else:
      print("That user is not online!")
  elif message.split()[0] == "|raw":  # raw formatted messages
    JSONOutput = json.dumps(json.loads(' '.join(message.split()[1:])))
    await client.ws.send(JSONOutput)
  elif message.split()[0] == "|users":  # user list
    print("Online Users:\n{}".format(', '.join(client.user_list)))
  elif message.split()[0] == "|clear":  # clears the chat
    os.system("cls" if os.name == "nt" else "clear")
  elif message.split()[0] == "|eval":  # evaluates python code
    try:
      print(eval(' '.join(message.split()[1:])))
    except Exception as e:
      print("{}: {}".format(type(e).__name__, e))
  elif message.split()[0] == "|exec":
    try:
      output = subprocess.run(' '.join(message.split()[
                              1:]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='Latin-1')
      if output.stderr == '':
        print(output.stdout)
      else:
        print(output.stdout)
    except Exception as e:
      print("{}: {}".format(type(e).__name__, e))
  elif message.split()[0] == "|quit" or message.split()[0] == "|q":  # disconnect from the chat
    sys.exit()
  elif message.split()[0] == "|help":
    print("Commands:\n\t|w <user> <message>\n\t\tsend a private message\n\t|raw <raw_json>\n\t\tsend raw json\n\t|users\n\t\tshow online users\n\t|eval <code>\n\t\tevaluate python code\n\t|exec <command>\n\t\executes bash commands\n\t|clear\n\t\tclears the chat\n\t|quit\n\t\tdisconnect from the server")
  else:
    print("Unknown command: {}".format(message.split()[0]))


# Checks if sending message is a command, if it is print output, if not, send message
async def send_message_queue(outputMsg):
  if outputMsg.startswith('|'):
    await parse_command(outputMsg)
  else:
    await client.send(outputMsg)


async def input_message():  # main coroutine for accepting input for sending messages
  while True:
    # takes message input
    message = await client.loop.run_in_executor(None, sys.stdin.readline)
    # removes line break at the end of message
    message = ' '.join(message.split('\n')[:len(message.split('\n')) - 1])
    await send_message_queue(message)

if config['username'] is None:  # Asks for a username if it is not already set in config.json
  login_username = input("Username: ")
else:
  login_username = config['username']

if config['password'] is None:  # Asks for a password if it is not already set in config.json
  rawPass = getpass("Password: ").encode('utf-8')
else:
  rawPass = config['password'].encode('utf-8')

if config['useSHA512']:  # Hashed password if useSHA512 is set to true in config.json
  hash_object = hashlib.sha512(rawPass)
  login_password = hash_object.hexdigest()
else:
  login_password = rawPass.decode('utf-8')

try:
  # runs the two main loops until stopped by the user
  client.run(login_username, login_password)
except (SystemExit, KeyboardInterrupt):
  print("\nDisconnected from server")
  sys.exit()
except Exception as e:
  print("{}: {}".format(type(e).__name__, e))
  sys.exit()
