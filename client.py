import asyncio  # used for multiple threads
import hashlib  # used for hashing passwords
import json  # used for formatting
import os  # used for clearing the screen
import os.path
import subprocess
import sys  # used for exiting
from datetime import datetime  # used for timestamps
# used for inputting passwords, doesnt display the password onscreen
from getpass import getpass

import rwci
from utils import prettyoutput as po  # used for pretty output to the console

user_colors = {}

server_stat = po.custom(string="{}", color_code="red", stat_msg="[SERVER]", prn_out=False)
auth_stat = po.custom(string="{}", color_code="red", stat_msg="[AUTH]", prn_out=False)
join_stat = po.custom(string="{}", color_code="green", stat_msg="[CONNECT]", prn_out=False)
quit_stat = po.custom(string="{}", color_code="yellow", stat_msg="[DISCONNECT]", prn_out=False)
dm_stat = po.custom(string="{}", color_code="cyan", stat_msg="|{} > {}|", prn_out=False)
msg_stat = po.custom(string="{}", color_code="reset", stat_msg="<{}>", prn_out=False)

class Config:
  def __init__(self):
    self._db = {}

  def get(self, key):
    try:
      self._db = json.load(open('config.json'))
      return self._db[key]
    except FileNotFoundError:
      json.dump({}, open('config.json', 'w+'), indent=2)
    except:
      return None
    return None

  def set(self, key, value):
    self._db[key] = value
    json.dump(self._db, open('config.json', 'w+'), indent=2)

def yes_or_no(prompt, default='y'):
    this_input = input("{} [{}/{}]: ".format(prompt, default.upper(), "n" if default == "y" else "y")).lower()
    if this_input in ["y", "yes", ""]:
      return True
    return False

config = Config()
if os.path.isfile('config.json'):
  use_defaults = yes_or_no("Would you like to use your default login settings?")
else:
  use_defaults = False

if not config.get('serverAddress') or not use_defaults:
  server = input('Server Address: ')
  client = rwci.Client(gateway_url=server)
else:
  client = rwci.Client(gateway_url=config.get('serverAddress'))

if not config.get('username') or not use_defaults:  # Asks for a username if it is not already set in config.json
  login_username = input("Username: ")
else:
  login_username = config.get('username')

if not config.get('password') or not use_defaults:  # Asks for a password if it is not already set in config.json
  login_password = getpass("Password: ")
else:
  login_password = config.get('password')

if not use_defaults:
  if yes_or_no("Would you like to save these settings?"):
    config.set('username', login_username)
    config.set('password', login_password)
    config.set('serverAddress', client.gateway_url)

if config.get('colors'):
  for user in config.get('colors'):
    user_colors[user['username']] = user['color']

async def get_color(username):
  if user_colors.get(username) in po.color:
    return po.color[user_colors[username]] + username + "\033[39m"
  return username


@client.event
async def on_ready():
  print("Successfully connected to the server")
  client.current_channel = client.default_channel
  if not client.current_channel:
      print("This server does not support channels")
  else:
      print(f"Joined channel #{client.current_channel}")
  asyncio.ensure_future(input_message())

@client.event
async def on_message(message):
  if not client.default_channel: pass
  elif not message.channel == client.current_channel: return
  client.message = message
  if config.get('blocked'):
    if message.author in config.get('blocked'): return
  message.content = message.content.replace(f'@{client.username}', po.color.get('red') + "@" + client.username + po.color.get('reset'))
  print(msg_stat.format(await get_color(message.author), message.content))


@client.event
async def on_user_list(user_list):
  if not len(client.users) == 0:
    print("Online Users:\n{}".format(', '.join(client.users)))
  else:
    print("No one is online :(")


@client.event
async def on_join(username):
  if config.get('blocked'):
    if username in config.get('blocked'): return
  print(join_stat.format(await get_color(username)))


@client.event
async def on_quit(username):
  if config.get('blocked'):
    if username in config.get('blocked'): return
  print(quit_stat.format(await get_color(username)))


@client.event
async def on_broadcast(message):
  print(server_stat.format(message))


@client.event
async def on_direct_message(message):
  if config.get('blocked'):
    if message.author in config.get('blocked'): return
  print(dm_stat.format(await get_color(message.author), await get_color(client.username), message.content))


async def parse_command(message):
  """
  For parsing client-side comamnds.

  Takes a message that is a comamnd as a parameter and returns the output of that message.
  """
  if not config.get('command_prefix'):
    prefix = "/"
  else:
    prefix = config.get('command_prefix')
  if not message.startswith(prefix):
    return False
  if message.split()[0] == f"{prefix}w":  # private messages
    try:
      user = [user for user in client.users if user.startswith(message.split()[1])][0]
    except IndexError:
      print("That user is not online!")
    else:
      if user in client.users and not user == client.username:
        message_content = " ".join(message.split()[2:])
        await client.send_dm(message_content, user)
        print(dm_stat.format(await get_color(client.username), await get_color(user), message_content))
      elif user == client.username:
        print("You can't send a private message to yourself!")
  elif message.split()[0] == f"{prefix}raw":  # raw formatted messages
    JSONOutput = json.dumps(json.loads(' '.join(message.split()[1:])))
    await client.ws.send(JSONOutput)
  elif message.split()[0] == f"{prefix}users":  # user list
    print("Online Users:\n{}".format(', '.join(client.users)))
  elif message.split()[0] == f"{prefix}clear":  # clears the chat
    os.system("cls" if os.name == "nt" else "clear")
  elif message.split()[0] == f"{prefix}eval":  # evaluates python code
    try:
      this_message = message
      message = client.message
      print(eval(' '.join(this_message.split()[1:])))
    except Exception as e:
      print("{}: {}".format(type(e).__name__, e))
  elif message.split()[0] == f"{prefix}exec":
    try:
      output = subprocess.run(' '.join(message.split()[1:]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='Latin-1')
      if output.stderr == '':
        print(output.stdout)
      else:
        print(output.stdout)
    except Exception as e:
      print("{}: {}".format(type(e).__name__, e))
  elif message.split()[0] == f"{prefix}quit" or message.split()[0] == f"{prefix}q":  # disconnect from the chat
    sys.exit()
  elif message.split()[0] == f"{prefix}help":
    print("Commands:\n\t{0}w <user> <message>\n\t\tsend a private message\n\t{0}raw <raw_json>\n\t\tsend raw json\n\t{0}users\n\t\tshow online users\n\t{0}eval <code>\n\t\tevaluate python code\n\t{0}exec <command>\n\t\texecutes bash commands\n\t{0}clear\n\t\tclears the chat\n\t{0}quit\n\t\tdisconnect from the server\n\t{0}shrug\n\t\tappends ¯\_(ツ)_/¯ to your message\n\t{0}block <user>\n\t\tblocks a user\n\t{0}unblock <user>\n\t\tunblocks a user\n\t{0}join <channel>\n\t\tjoins a channel\n\t{0}channels\n\t\tlists the channels on the server\n".format(prefix))
  elif message.split()[0] == f"{prefix}shrug":
    await client.send(' '.join(message.split()[1:]) + " ¯\_(ツ)_/¯")
  elif message.split()[0] == f"{prefix}block":
    if not config.get('blocked'):
      config.set('blocked', [])
    block_list = config.get('blocked')
    try:
      user = [user for user in client.users if user.startswith(message.split()[1])][0]
    except IndexError:
      user = message.split()[1]
    block_list.append(user)
    config.set('blocked', block_list)
    print(f"{message.split()[1]} has been added to the block list")
  elif message.split()[0] == f"{prefix}unblock":
    block_list = config.get('blocked')
    try:
      user = [user for user in client.users if user.startswith(message.split()[1])][0]
    except IndexErrpr:
      user = message.split()[1]
    block_list.remove(user)
    config.set('blocked', block_list)
    print(f"{message.split()[1]} has been removed from the block list")
  elif message.split()[0] == f"{prefix}join":
    if len(message.split()) == 1:
      client.current_channel = client.default_channel
      print(f"Joined channel #{client.default_channel}")
      return True
    try:
      new_channel = [channel for channel in client.channels if channel.startswith(message.split()[1])][0]
    except IndexError:
      print("That channel doesn't exist")
    else:
      client.current_channel = new_channel
      print(f"Joined channel #{new_channel}")
  elif message.split()[0] == f"{prefix}channels":
    print("This server does not support channels" if not client.channels else ', '.join(client.channels))
  elif message.split()[0] == f"{prefix}afk":
    await client.send(" * afk * ", client.current_channel)
  else:
    print("Unknown command: {}".format(message.split()[0]))
  return True

async def input_message():  # main coroutine for accepting input for sending messages
  while True:
    # takes message input
    message = await client.loop.run_in_executor(None, sys.stdin.readline)
    # removes line break at the end of message
    message = ' '.join(message.split('\n')[:len(message.split('\n')) - 1])
    if not await parse_command(message):
      await client.send(message, client.current_channel)

try:
  # runs the two main loops until stopped by the user
  client.run(login_username, login_password)
except (SystemExit, KeyboardInterrupt):
  print("\nDisconnected from server")
  sys.exit()
except Exception as e:
  print("{}: {}".format(type(e).__name__, e))
  sys.exit()
