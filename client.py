import time
import traceback
import sys
import requests
import re
import json

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'
RESET = '\u001b[0m'

def colorit(item, typ):
  if typ == 'mention':
    n = RED
  elif typ == 'gt':
    n = GREEN
  elif typ == 'time':
    n = BLUE
  else:
    n = ''
  return n + str(item) + RESET

def format_data(req_type, ctime, uname, content='', key=None):
  data = {}
  try:
    assert req_type in ['message', 'retrieve', 'doc', 'shutdown', 'debug'] #Valid `req_type`
  except:
    return 0

  if req_type == 'message':
    try:
      assert content != '' #Message is not empty
      assert len(content.split(' ')) != 0 #Message is not only spaces
    except:
      return 1


  if req_type == 'retrieve':
    try:
      int(content) #String contains only numbers
      inttype = True
    except:
      inttype = False
      if content == '': #String is a blank string
        inttype = True
    try:
      assert inttype
    except:
      return 2
    try:
      assert type(ctime) is int #ctime must be int
      assert type(uname) is str #uname must be str
    except:
      return 3
    try:
      assert uname != '' #uname not empty
      assert len(uname.split(' ')) != 0 #uname not space
    except:
      return 4
    
  data['mtype'] = req_type
  data['contents'] = content
  data['from'] = uname
  data['time'] = ctime
  if req_type == 'shutdown':
    data['key'] = key

  return data

def format_messages(data):
  fstr = '%s: (%s) %s [ %s ]'
  index_pad = ' '*(6-len(str(data[0]))) + str(data[0])
  if data[3].startswith('>'):
    text = colorit(data[3], 'gt')
  elif re.search('@[a-zA-Z0-9]+', data[3]):
    t = re.search('@[a-zA-Z0-9]+', data[3]).group()
    text = data[3].replace(t, colorit(t, 'mention'))
  else:
    text = data[3]
  return fstr % (index_pad, data[2], text, colorit(data[1], 'time'))

def download_chat(floattime, uname, server):
  data = format_data('retrieve', int(floattime), str(uname))
  try:
    r = requests.post(server, data=data)
  except Exception as e:
    return False, e

  d = json.loads(r.text)['contents']
  mstring = '[*] %s messages in %ss' % (len(d), str(time.time()-floattime))
  v = [format_messages(x) for x in d]
  v.reverse()
  return mstring, v
  


def main():
  not_valid = True

  while not_valid:
    print('Server URL: ')
    server = input('> ')
    if re.match(regex, server):
      not_valid = False
    elif server == 'exit':
      sys.exit()
    else:
      print('INVALID URL...')
      
  while True:
    print('What is your username? (may not exceed 16 chars, \nalphanumeric only and no spaces')
    uname = input('> ')
    if len(uname) > 16:
      print('username exceeds 16 chars')
    else:
      not_allowed = False
      for x in uname:
        if x not in [x for x in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789']:
          not_allowed = True
          break
      if not_allowed:
        print('username contains character that may not be used.')
      else:
        break

  print('Display how many messages at a time? ')
  try:
    num = int(input('> '))
    if num < 1:
      num = 1
  except:
    num = 15


  floattime = time.time()
  ctime = int(floattime)

  print('Downloading Chat history....')
  mstring, history = download_chat(floattime, uname, server)
  if mstring == False:
    print('ERROR: %s' % history)
    sys.exit(1)
  print(mstring)
  if history != None:
    for x in history[-num:]:
      print(x)

  while True:
    payload = input('> ')
    floattime = time.time()
    ctime = int(floattime)

    #Shutdown Block

    if payload == '$shutdown':
      print('Enter Password')
      passwd = input('> ')
      floattime = time.time()
      ctime = int(floattime)
      data = format_data('shutdown', str(ctime), uname, key=passwd)
    
    elif payload == '$doc':
      data = format_data('doc', str(ctime), uname)

    elif payload == '$debug':
      data = format_data('debug', str(ctime), uname)
      print(data)
    elif payload == '$quit':
      print('Goodbye')
      sys.exit(0)

    else:
      data = format_data('message', str(ctime), uname, content=payload)

    r = requests.post(server, data=data)
    try:
      d = json.loads(r.text)
      if d.get('isdoc'):
        print('===== DOC =====')
        print(d['contents'])
      elif d.get('isdebug'):
        print('===== DEBUG =====')
        for x in d['contents']:
          print(x)
    except:
      print(r.text)

    floattime = time.time()
    ctime = int(floattime)

    mstring, history = download_chat(floattime, uname, server)
    if mstring == False:
      print('ERROR: %s' % history)
      sys.exit(1)
    print(mstring)
    for x in history[-num:]:
      print(x)
    

main()
