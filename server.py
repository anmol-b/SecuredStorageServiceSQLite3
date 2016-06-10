# Created by Anmol Bhargava

import os
import swiftclient
import keystoneclient
import pyDes
import sqlite3
import hashlib

from flask import Flask, request, render_template

app = Flask(__name__)
k = pyDes.des(b"DESCRYPT", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

connDB = sqlite3.connect("storage_db")
c = connDB.cursor()

def md5(file):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
      hash_md5.update(chunk)
    return hash_md5.hexdigest()

usernameForm = ""

sqlite_file = 'storage_db.sqlite'    # name of the sqlite database file
table_name1 = 'users'  # name of the table to be created
table_name2 = 'files'  # name of the table to be created
id_user_field = 'id_user'
username_field = 'username'

id_file_field = 'id_file'
username_f_field = 'username'
filename_field = 'filename'
filecontent_filed = 'filecontent'
fileversion_field = 'fileversion'

field_type1 = 'TEXT'  # column data type
field_type2 = 'INTEGER'
field_type3 = 'BLOB'

try:
  c.execute('CREATE TABLE IF NOT EXISTS {tn} ({n1f} {f1t} PRIMARY KEY, {n2f} {f2t}, {n3f} {f3t})'\
        .format(tn=table_name1, n1f=id_user_field, f1t=field_type2, n2f=username_field, f2t=field_type1, n3f=password_field, f3t=field_type1))

  c.execute('CREATE TABLE IF NOT EXISTS {tn} ({n1f} {f1t} PRIMARY KEY, {n2f} {f2t}, {n3f} {f3t}, {n4f} {f4t}, {n5f} {f5t})'\
        .format(tn=table_name2, n1f=id_file_field, f1t=field_type2, n2f=username_f_field, f2t=field_type1, n3f=filename_field, f3t=field_type1, n4f=filecontent_filed, f4t=field_type1, n5f=fileversion_field, f5t=field_type2))
except sqlite3.Error as er:
  print ('er:', er)

try:
    c.execute("INSERT OR REPLACE INTO {tn} ({n1f}, {n2f}, {n3f}) VALUES (1, 'john', 'pass@1')".\
        format(tn=table_name1, n1f=id_user_field, n2f=username_field, n3f=password_field))
    c.execute("INSERT OR REPLACE INTO {tn} ({n1f}, {n2f}, {n3f}) VALUES (2, 'amy', 'pass@2')".\
        format(tn=table_name1, n1f=id_user_field, n2f=username_field, n3f=password_field))
    c.execute("INSERT OR REPLACE INTO {tn} ({n1f}, {n2f}, {n3f}) VALUES (3, 'penny', 'pass@3')".\
        format(tn=table_name1, n1f=id_user_field, n2f=username_field, n3f=password_field))
    c.execute("INSERT OR REPLACE INTO files (id_file,username,filename,filecontent,fileversion) VALUES (0, 'xx', 'xx', 'xx', 'xx')")
except sqlite3.IntegrityError:
    print('ERROR: ID already exists in PRIMARY KEY column {}'.format(id_column))


@app.route('/')
def Welcome():
  return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def Authenticate():
  if request.method=='POST':
    global usernameForm
    usernameForm = request.form['user_name']
    passwordForm = request.form['password']

    print (usernameForm, passwordForm)
    
    try:
      c.execute("SELECT id_user FROM users WHERE username=?",(usernameForm,))
      user_exists = c.fetchone()
      
      c.execute("SELECT id_user FROM users WHERE username=? AND password=?",(usernameForm, passwordForm,))
      pass_match = c.fetchone()
    except Exception as e:
      print (e)
      return '<h1>Invalid Credentials! Try again.</h1><br><form action="../"><input type="submit" value="Go Back"></form>'

    if user_exists and pass_match:
      return render_template("index.html")
    else:
      return '<h1>Invalid Credentials! Try again.</h1><br><form action="../"><input type="submit" value="Go Back"></form>'
      
@app.route('/index')
def Index():
  return render_template("index.html")

@app.route('/upload',methods=['GET','POST'])
def Upload():
  if request.method=='POST':
    message = 'Awesome! Files uploaded.'
    file= request.files['file_upload']
    
    filename=file.filename
    content=file.read()

    try:
      c.execute("SELECT * FROM files WHERE username=? AND filename=?",(usernameForm,filename,))
      file_exists = c.fetchone()
    except Exception as e:
      print(e)
      file_exists = False

    if file_exists:
      print("In file upload if_exists")
      try:
        c.execute("SELECT id_file, fileversion FROM files WHERE username=? AND filename=? ORDER BY id_file DESC LIMIT 1",(usernameForm,filename,))
        row = c.fetchone()
        
        curr_id = row[0]
        fileversion = row[1]
        new_f_id2 = int(curr_id)+1
        new_version = int(fileversion) + 1
        
        c.execute("INSERT INTO files (id_file,username,filename,filecontent,fileversion) VALUES (?,?,?,?,?)",(new_f_id2,usernameForm,filename,content,new_version,))
        message = message + "<br>File already existed<br>New File version is : " + str(new_version)
      except Exception as e:
        print(e)
        message = 'Oops!! Something went worng :/'
    else:
      print("In file upload else")
      try:
        c.execute("SELECT id_file FROM files ORDER BY id_file DESC LIMIT 1")
        curr_id = c.fetchone()[0]
        new_f_id = int(curr_id)+1
        version = 1
        c.execute("INSERT INTO files (id_file,username,filename,filecontent,fileversion) VALUES (?,?,?,?,?)",(new_f_id,usernameForm,filename,content,version,))
      except Exception as e:
        print(e)
        message = 'Oops!! Something went worng :/'

    return '<h1>'+ message +'</h1><br><form action="../index"><input type="Submit" value="Lets go back"></form>'

@app.route('/download',methods=['GET','POST'])
def Download():
    if request.method=='POST':
      filename = request.form['file_download']
      fileversion = request.form['file_version']
      fileContents = "File not found :/"
      try:
        c.execute("SELECT filecontent FROM files WHERE username=? AND filename=? AND fileversion=?",(usernameForm,filename,fileversion,))
        fileContents = str(c.fetchone()[0])
      except Exception as e:
         print(e)
    return '<h3>The File is,</h3><br><br>' + fileContents + '<br><br><form action="../index"><input type="Submit" value="Lets go back"></form>'

@app.route('/delete',methods=['GET','POST'])
def Delete():
    if request.method=='POST':
      filename = request.form['file_delete']
      fileversion = request.form['file_d_version']
      try:
        c.execute("DELETE FROM files WHERE username=? AND filename=? AND fileversion=?",(usernameForm,filename,fileversion,))
      except Exception as e:
        print(e)
      return '<h3>The File '+str(filename)+' with version '+str(fileversion)+' has been successfully deleted,</h3><br><br><form action="../index"><input type="Submit" value="Lets go back"></form>'

@app.route('/list')
def List():
  listOfFiles = ""
  try:
    c.execute('SELECT filename, fileversion FROM files WHERE username=? LIMIT 10',(usernameForm,))
    row_data = c.fetchall()
    if row_data == []:
      listOfFiles = listOfFiles + "<i> No files are currently present on Cloud.</i><br>"
    else:
      for row in row_data:
        listOfFiles = listOfFiles + "<li> File : " + str(row[0]) + ", Version : " + str(row[1]) 
  except sqlite3.Error as er:
    print ('er:', er)

  return '<h3>The files currently on cloud are </h3><br><br><ol>' + listOfFiles + '<br><form action="../index"><input type="Submit" value="Lets go back"></form><br><br>'

# Port Specified according to IBM Bluemix Environment
port = os.getenv('PORT', '8000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
