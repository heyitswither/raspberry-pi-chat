import websockets # used for websocket connection
import asyncio # used for multiple threads
import json # used for formatting
import sys # used for exiting
import os # used for clearing the screen
import hashlib # used for hashing passwords
from getpass import getpass # used for inputting passwords, doesnt display the password onscreen
from datetime import datetime # used for timestamps

with open('config.json') as fileIn:
  config = json.load(fileIn) # imports config.json as config

if config['custom'] == False: # used for making sure the user has looked over config.json
  print("Please read and change any necessary options in the config.json file")
  print("If you are happy with the configuration, please change 'custom' to true")
  sys.exit()

previousMsg = "" # the previosu message received, for spam prevention
users_list = [] # list of online users
loggedIn = False

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

async def connect(): # connect to the server
  global config
  if not config['serverAddress'] == None: # Check if the server address is already set in config.json, if not, ask for a server
    ws = asyncio.get_event_loop().run_until_complete(websockets.connect(config['serverAddress']))
  else:
    server = input('Server Address: ')
    ws = asyncio.get_event_loop().run_until_complete(websockets.connect(server))

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

async def receive_message(): # main coroutine for receiving messages and parsing the output
  global ws
  global loggedIn
  global previousMsg
  global users_list
  if not loggedIn:
    await auth()
  while loggedIn:
    rawInput = await ws.recv() # receives new messages
    JSONInput = json.loads(rawInput) # converts raw messages to json
    if "type" in JSONInput: # checks the type of each messages and changes the output based on it
      if JSONInput['type'] == "broadcast": # server broadcast messages
        InputMsg = "[BROADCAST] {}".format(JSONInput["message"])
      elif JSONInput['type'] == "join": # user join message
        if not JSONInput["username"] in users_list or not JSONInput['username'] == username:
          InputMsg = "[CONNECT] {}".format(JSONInput["username"])
          users_list.append(JSONInput['username'])
      elif JSONInput['type'] == "quit": # user quit messages
        if JSONInput["username"] in users_list:
          InputMsg = "[DISCONNECT] {}".format(JSONInput["username"])
          users_list.remove(JSONInput['username'])
      elif JSONInput['type'] == "direct_message": # private message
        InputMsg = "|{} > {}| {}".format(JSONInput['author'], username, JSONInput['message'])
      elif JSONInput['type'] == "auth": # authentication message
        if JSONInput['new_account'] == False and JSONInput['success'] == True:
          InputMsg = "[AUTH] Successfully authenticated with an existing account"
        elif JSONInput['new_account'] == False and JSONInput['success'] == False:
          InputMsg = "[AUTH] There was an error authenticating, please check your password"
        elif JSONInput['new_account'] == True:
          InputMsg = "[AUTH] New account created successfully"
      elif JSONInput['type'] == "user_list": # user list
        InputMsg = "user_list"
        for user in JSONInput['users']:
          users_list.append(user)
        print("Online Users:\n{}".format(', '.join(users_list)))
      elif JSONInput['type'] == "message": # normal messages
        InputMsg = "<{}> {}".format(JSONInput['author'], JSONInput['message'])
    if not InputMsg == previousMsg and not InputMsg == "user_list" and not InputMsg == "": # filters out repeat messages and blank emssages
      print(datetime.now().strftime("%H:%M"), InputMsg) # prints the message on the screen, with its author and a timestamp
      previousMsg = InputMsg

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
# except Exception as e:
#   print("{}: {}".format(type(e).__name__, e))
#   sys.exit()
loop.close()
