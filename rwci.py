"""
classes for use in rwci client
"""

import json


class User:
  def __init__(self, **kwargs):
    self.messages = []
    with open('config.json', 'r') as fileIn:
      self.config = json.load(fileIn)
    if not 'username' in kwargs:
      raise ValueError('A username must be specified')
    self.username = kwargs['username']
    if 'color' in kwargs:
      self.color = kwargs['color']
    if 'joined_at' in kwargs:
      self.joined_at = kwargs['joined_at']

  def dm(self, message):
    pass # need to do stuff here

class Client:
  def __init__(self):
    self.joined_at = datetime.now().timestamp()
    self.messages = []
    with open('config.json', 'r') as fileIn:
      self.config = json.load(fileIn)
    if self.config['username'] in [colorobj['username'] for colorobj in self.config['colors']]:
      self.user = User(username=self.config['username'], color=[colorobj['color'] for colorobj in self.config['colors'] if colorobj['username'] == self.config['username']][0])
    else:
      self.user = User(username=self.config['username'])
    self.users = []
    if len(self.config['colors']) > 0:
      for user in self.config['colors']:
        self.users.append(User(username=user['username'], color=user['color']))

class Message:
  def __init__(self, content, m_type, author):
    self.content = content
    self.type = m_type
    self.author = User()
    self.timestamp = datetime.now().timestamp()
