import websockets # used for websocket connection
import asyncio # used for multiple threads
import json # used for formatting
import sys # used for exiting
import os # used for clearing the screen
import hashlib # used for hashing passwords
from getpass import getpass # used for inputting passwords, doesnt display the password onscreen
from datetime import datetime # used for timestamps
from utils import prettyoutput as po # used for pretty output to the console

with open('config.json') as fileIn:
  config = json.load(fileIn) # imports config.json as config

if config['custom'] == False: # used for making sure the user has looked over config.json
  print("Please read and change any necessary options in the config.json file.")
  print("You must also have read the README.md file to the format of the options.")
  print("If you have done these things, please change custom to true in the config.json file.")
  sys.exit()

previousMsg = None # the previosu message received, for spam prevention
users_list = [] # list of online users
loggedIn = False
user_colors = {}

server_stat = po.custom(string="{}", color_code="red", stat_msg="[SERVER]", prn_out=False)
auth_stat = po.custom(string="{}", color_code="red", stat_msg="[AUTH]", prn_out=False)
join_stat = po.custom(string="{}", color_code="green", stat_msg="[CONNECT]", prn_out=False)
quit_stat = po.custom(string="{}", color_code="yellow", stat_msg="[DISCONNECT]", prn_out=False)
dm_stat = po.custom(string="{}", color_code="cyan", stat_msg="|{} > {}|", prn_out=False)
msg_stat = po.custom(string="{}", color_code="reset", stat_msg="<{}>", prn_out=False)

if config['username'] == None: # Asks for a username if it is not already set in config.json
  username = input("Username: ")
else:
  username = config['username']

if config['password'] == None: # Asks for a password if it is not already set in config.json
  rawPass = getpass("Password: ").encode('utf-8')
else:
  rawPass = config['password'].encode('utf-8')

if config['useSHA512'] == True: # Hashed password if useSHA512 is set to true in config.json
  hash_object = hashlib.sha512(rawPass)
  hashedPass = hash_object.hexdigest()
else:
  hashedPass = rawPass.decode('utf-8')

for user in config['colors']:
  user_colors[user['username']] = user['color']

async def connect(): # connect to the server
  global config
  global ws
  if not config['serverAddress'] == None: # Check if the server address is already set in config.json, if not, ask for a server
    ws = await websockets.connect(config['serverAddress'])
  else:
    server = input('Server Address: ')
    ws = await websockets.connect(server)

async def auth():
  global loggedIn
  global ws
  await connect() # calls the connect function
  JSONAuth = json.dumps({"type": "auth", "username": username, "password": hashedPass}) # formats the auth messages
  await ws.send(JSONAuth) # sends the auth messages
  loggedIn = True

async def is_command(message):
  if message.startswith("|"):
    return True
  else:
    return False

async def send_message(message):
  global ws
  JSONOutput = json.dumps({"type": "message", "message": message.strip("\n")})
  await ws.send(JSONOutput)

async def parse_command(message):
  global username
  global ws
  if message.split()[0] == "|w": # private messages
    if message.split()[1] in users_list and not message.split()[1] == username:
      JSONOutput = json.dumps({"type": "direct_message", "recipient": message.split()[1], "message": " ".join(message.split()[2:])})
      await ws.send(JSONOutput)
    elif message.split()[1] == username:
      print("You can't send a private message to yourself!")
    else:
      print("That user is not online!")
  elif message.split()[0] == "|raw": # raw formatted messages
    JSONOutput = json.dumps(json.loads(message[5:]))
    await ws.send(JSONOutput)
  elif message.split()[0] == "|users": # user list
    print("Online Users:\n{}".format(', '.join(users_list)))
  elif message.split()[0] == "|clear": # clears the chat
    os.system("clear")
  elif message.split()[0] == "|eval": # evaluates python code
    try:
      print(eval(' '.join(message.split()[1:])))
    except Exception as e:
      print("{}: {}".format(type(e).__name__, e))
  elif message.split()[0] == "|basheval":
    try:
      print(os.popen(' '.join(message.split()[1:])).read())
    except Exception as e:
      print("{}: {}".format(type(e).__name__, e))
  elif message.split()[0] == "|quit": # disconnect from the chat
    sys.exit()
  elif message.split()[0] == "|help":
    print("Commands:\n\t|w <user> <message>\n\t\tsend a private message\n\t|raw <raw_json>\n\t\tsend raw json\n\t|users\n\t\tshow online users\n\t|eval <python_code>\n\t\tevaluate python code\n\t|basheval <bash_code>\n\t\tevaluate bash code\n\t|clear\n\t\tclears the chat\n\t|quit\n\t\tdisconnect from the server")
  else:
    print("Unknown commandd: {}".format(outputMsg.split()[0]))

async def send_message_queue(outputMsg): # Checks if sending message is a command, if it is print output, if not, send message
  if await is_command(outputMsg):
    await parse_command(outputMsg)
  else:
    await send_message(outputMsg)

async def get_color(username):
  if username in user_colors:
    return po.color[user_colors[username]] + username + "\033[39m"
  else:
    return username

async def print_out(m_type, message):
  global username
  global previousMsg
  if not message == previousMsg:
    previousMsg = message
    if m_type == "message":
      print(msg_stat.format(await get_color(message['author']), message['message']))
    elif m_type == "broadcast":
      print(server_stat.format(message['message']))
    elif m_type == "join":
      print(join_stat.format(await get_color(message['username'])))
    elif m_type == "quit":
      print(quit_stat.format(message['username']))
    elif m_type == "direct_message":
      print(dm_stat.format(await get_color(message['author']), await get_color(username), message['message']))
    elif m_type == "auth":
      if message['new_account']:
        print(auth_stat.format("New account created successfully."))
      elif not message['new_account'] and message['success']:
        print(auth_stat.format("Successfully authenticated with an existing account."))
      elif not message['new_account'] and not message['success']:
        print(auth_stat.format("There was an error authenticating, please check your password."))
    elif m_type == "user_list":
      if not users_list == []:
        print("Online Users:\n{}".format(', '.join(users_list)))
      else:
        print("No one is online.")

async def parse_message(message):
  global previousMsg
  global users_list
  if "type" in message: # checks the type of each messages and changes the output based on it
    if message['type'] == "broadcast": # server broadcast messages
      await print_out("broadcast", message)
    elif message['type'] == "join": # user join message
      if not message["username"] in users_list or not message['username'] == username:
        await print_out("join", message)
        users_list.append(message['username'])
    elif message['type'] == "quit": # user quit messages
      if message["username"] in users_list:
        await print_out("quit", message)
        users_list.remove(message['username'])
    elif message['type'] == "direct_message": # private message
      await print_out("direct_message", message)
    elif message['type'] == "auth": # authentication message
      await print_out("auth", message)
    elif message['type'] == "user_list": # user list
      for user in message['users']:
        users_list.append(user)
        await print_out("user_list", message)
    elif message['type'] == "message": # normal messages
      await print_out("message", message)

async def receive_message(): # main coroutine for receiving messages and parsing the output
  global ws
  global loggedIn
  if not loggedIn:
    await auth()
  while loggedIn:
    rawInput = await ws.recv() # receives new messages
    JSONInput = json.loads(rawInput) # converts raw messages to json
    await parse_message(JSONInput)

async def input_message(): # main coroutine for accepting input for sending messages
  while True:
    message = await loop.run_in_executor(None, sys.stdin.readline) # takes message input
    await send_message_queue(message) # calls send message function

loop = asyncio.get_event_loop()
try:
  loop.run_until_complete(asyncio.gather(receive_message(), input_message())) # runs the two main loops until stopped by the user
except (SystemExit, KeyboardInterrupt, websockets.exceptions.ConnectionClosed):
  print("\nDisconnected from server")
  sys.exit()
except Exception as e:
  print("{}: {}".format(type(e).__name__, e))
  sys.exit()
loop.close()
