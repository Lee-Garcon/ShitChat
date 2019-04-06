from flask import Flask, request, jsonify
import time
import hashlib
import traceback
import sys
import requests

#========= Define Functions =============

def format_log(log_lines):
  a = log_lines
  for x in a:
    data = x.split(' ')
    yield (int(data[0]), int(data[1]), data[2], data[3])

def write_chat(index, ctime, usr, contents):
  return ' '.join((str(index), str(ctime), usr, contents))


#========= Server Name and INIT =========

print('Name: ')
NAME = input('> ')
print('Host Port: ')
port = int(input('> '))
print('PASS: ')

app = Flask(NAME)

#========== Password and DATA ===========

h = hashlib.sha256()

h.update(input('>').encode('ascii'))
passwd = h.hexdigest()
print('PASSWD HASH: %s' % passwd)

f = open('./data.txt', 'w')
f.close()
f = open('./data.txt', 'r')
DATA = [x for x in format_log(f.readlines())]
f.close()
#Format: [index, time, user, content]




#============= Format var DATA ===========

INDEX = 0
if len(DATA) != 0:
  INDEX = DATA[-1][0]

curtime = time.time()

#=============== App Function ============

@app.route('/', methods=['GET', 'POST'])
def result():
  global INDEX
  global NAME
  global DATA
  global passwd
  ctime = time.time()
  int_ctime = int(ctime)

  #NOTE:
  #ctime:      FLOAT  SYS-TIME
  #int_ctime:  INT    SYS-TIME
  #mtim        INT    CLIENT-TIME


  #=========== GET request return =========

  if request.method == 'GET':
    return '<h1> %s </h1><br><h2>A chat server</h2><br><h3>POST into this</h3><h1>HI ALBERT</h1>' % NAME

    #========= POST Request Return ========

  else:
    try:

      #=========== Get Form Results =======

      request_type = request.form['mtype']
      usr = request.form['from']
      contents = request.form['contents']
      mtime = int(request.form['time'])

      #====== Print Request Details =======

      print('[%s] Request: [ %s %s \'%s\' ]' % (int(ctime), usr, request_type, contents))

      #======= Message Request Type========


      if request_type == 'message':
        d = [INDEX, int_ctime, usr, contents]
        DATA.append(d)
        INDEX += 1
        return jsonify({'resp': 200})

      elif request_type == 'ping':
        r = requests.post(contents, data={'resp':200, 'pingme':True})
        if r.status_code == 400:
          print('Huh?')
        return '', 200

      #====== Retrieve Message Type =======

      elif request_type == 'retrieve':
 
        if contents != '':
          try:
            checktime = mtime - int(contents)
          except:
            print('[*] Exception: ')
            traceback.print_exc()
            print('================\n')
            return jsonify({'resp': 400})

          #===== No Contents Field ========

        else:
          checktime = mtime - 86400 #1 day in the past
          print('[*] Checktime: %s' % checktime)

        #========= Get All Messages =======
        
        retr_list = []
        for x in reversed(DATA):
          if x[1] >= checktime:
            retr_list.append(x) #
          else:
            break
        return jsonify({'resp': 200, 'contents': retr_list})
      
      #======== Doc Message Type ==========

      elif request_type == 'doc':
        return jsonify({'resp':200, 'isdoc': True, 'contents': ''}) #insert docs

      #====== Shutdown Message Type =======

      elif request_type == 'shutdown':

        try:
          login = request.form['key']
        except Exception:
          return jsonify({'resp': 400})

      #======== Hash Login Field ==========

        h = hashlib.sha256()
        h.update(login.encode('ascii'))
        l = h.hexdigest()

      #========= Authentication ===========

        print(l, passwd)

        if l == passwd:
          print('[*] AUTHENTICATED: USER [ %s ]' % usr)
          auth = True
        
      #========= Not Authenticated ========

        else:
          auth = False
          print('==========\n[*] INCORRECT-AUTH: USER [ %s ]\n==========' % usr)
          return jsonify({'resp': 400})

      #====== Shutdown Commands, etc =====

        if auth:
          f = open('./data.txt', 'w')
          d = ''
          for x in reversed(DATA):
            a = ' '.join([str(y) for y in x]) + '\n'
            d += a
          f.write(' '.join([str(y) for y in x]) + '\n')
          f.close()
          sys.exit() 
        return jsonify({'resp': 200})

      elif request_type == 'debug':
        return jsonify({'resp':200, 'contents':DATA, 'isdebug': True})

      #=======     Exceptions    ==========
    
    except Exception as e:
      print('[*] Exception: ')
      traceback.print_exc()
      print('================\n')
      return 'Error: %s' % e, 400

      #====================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
