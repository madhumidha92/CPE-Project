from socket import *
import sys
import os
import re
import ssl
import base64
import dropbox
import time
import thread
import xml.etree.ElementTree as ET
import datetime
import urllib2
import sqlite3
import select
import thread
import threading


from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText

app_key = 'unauq6c7gbgzn59'
app_secret = '2q6hwhmtpw0c7pa'
databaseName = 'Users.db'
tableName = 'subscribedUsers'
Chat = 'CHAT'
Terminate = 'TERMINATE'
friend = 'friend'
Name = []
HOST = gethostname()
PORT1 = 12001
PORT2 = 12002
mailserver = 'smtp.gmail.com' 
sender =''
destination =''
tcpConnections = []
PASSWORD = ""
inputEntered = ['NO']
link = ['0']
Terminate = 'TERMINATE'
flag = []
UserId = []

text_subtype = 'plain'

content=""

subject="Sent from Python"
# Choose a mail server and call it mailserver

serverPort = 587


class Chat_Listen(threading.Thread):
        #Initialization
        def __init__(self):
            threading.Thread.__init__(self)
            self.running = -1
            self.sock = None
            self.addr = None
            self.data = 'initialValue'
            self.tcpPort = 0000
        #Start
        def run(self):
            HOST = ''
            PORT = int(self.tcpPort)
            s = socket(AF_INET, SOCK_STREAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            try:
                s.bind((HOST,PORT))
            except:
                print '\n Port is already in Use'
            s.listen(1)
            #Wait to get TCP connection
            while 1 : 
                self.sock, self.addr = s.accept()
                message = self.sock.recv(1024)
                print message
              
                #Run until TERMINATE is entered while in the chat
                while (self.data.find(Terminate) == -1):
                    select.select ([self.sock],[self.sock],[])
                    self.data = self.sock.recv(1024)
                    if self.data:
                          if self.data.find(friend)!=-1 or self.data.find(friend.lower())!=-1:
                             msg = self.data
                             msg = msg.translate(None,"(),")
                             msg = msg.split()
                             conn = sqlite3.connect(databaseName)
                             c = conn.cursor()
                             c.execute("INSERT INTO %s VALUES ('%s','%s', '%s',%d,%d )" %(tableName,msg[2],msg[1],'ListenConnection',0,0))
                             conn.commit()
                             conn.close()
                             self.sock.send('\nConfirm ' + Name[0])
                          else:
                             print '\n' + self.data
                    else:
                        break
                    time.sleep(0)
                
                print "Chat ended Listening."
                self.sock.close()

        def kill(self):
            self.running = 0


class Chat_Connect(threading.Thread):
        #Initialization
        def __init__(self):
            threading.Thread.__init__(self)
            self.host = None
            self.sock = None
            self.running = 1
            self.data = 'initialValue'
            self.tcpPort = 00000
        #Start
        def run(self): 
            self.sock = socket(AF_INET, SOCK_STREAM)
            try:
                self.sock.connect((self.host, int(self.tcpPort)))
            except:
                print '\n Could not Connect to Specified Address'

            #Send a message on connection
            self.sock.send('\n' + 'We are now connected!')
            friendreq = raw_input('\nSent Friend Request with your location link: ')
            self.sock.send('\n' + friendreq)

            #Run until TERMINATE command is entered
            while (self.data.find(Terminate) == -1): 
                select.select ([self.sock],[self.sock],[])
                self.data = self.sock.recv(1024)
                if self.data:
                    print '\n' + self.data
                else:
                    break
                time.sleep(0)
            
            print "Chat ended connection."
            self.sock.close()



        def kill(self):
            self.running = 0


def updateLocationXML():

    currentTime = str(datetime.datetime.now()) 
    tree = ET.parse('location.xml')
    root = tree.getroot()
    
    #Find address node in xml to find ip and time ultimately
    for address in root.findall('address'):
      ip =  address.find('IP')
      #port = address.find('port')
      time = address.find('time')

    time.text = currentTime
    #Find link node in xml file and ultimately times
    for address in root.findall('links'):
      time = address.find('time')
    time.text = currentTime

    tree.write('location.xml')


def connectWithOtherUser(xmlLink,UserId):
   
    tree = ET.parse('location.xml')
    root = tree.getroot()
    ip = ''
    port = ''
    publicLink = ''
    contentLink = ''

    #Parse ip and port no from local copy of location.xml file
    for address in root.findall('address'):
      ip =  address.find('IP')
      port = address.find('port')
      id = address.find('ID')

    for link in root.findall('links'):
      publicLink = link.find('public')
      contentLink = link.find('content')
    

    try:
        conn = sqlite3.connect(databaseName)
        c = conn.cursor()
        c.execute("INSERT INTO %s VALUES ('%s','%s', '%s',%d,%d )" %(tableName,xmlLink[len(UserId)],id.text,ip.text,int(port.text), len(UserId)))
        conn.commit()
        conn.close()
    except:
        print 'Can not connect to database '

    #Start connection
    chat_connect = Chat_Connect()
    tcpConnections.append(chat_connect)
    tcpConnections[len(UserId)].host = ip.text
    tcpConnections[len(UserId)].tcpPort = int(port.text)
    tcpConnections[len(UserId)].start()


def getLocationFileData(check_Input,cloudProvider):
    
    #If dropbox selected
    if cloudProvider==str(1):
        print 'Cloud Provider: DropBox'
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        authorize_url = flow.start()
        print '1. Go to: ' + authorize_url
        print '2. Click "Allow" (you might have to log in first)'
        print '3. Copy the authorization code.'
        code = raw_input("Enter the authorization code here: ").strip()
        
        # This will fail if the user enters an invalid authorization code
        access_token, user_id = flow.finish(code)

        client = dropbox.client.DropboxClient(access_token)
        #write content to local location.xml file
        g = open('location.xml','w')
        f = client.get_file('/location.xml')
        g.write(f.read())
        g.close()


    #If google drive selected
    elif cloudProvider==str(2):
        print 'Cloud Provider: Google Drive'
        flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print 'Go to the following link in your browser: ' + authorize_url
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
        drive_service = build('drive', 'v2', http=http)


        drive_file = drive_service.files().get(fileId='0Bzqdt8FrCHz-UDFPbjhqWVB5Mzg').execute()
        download_url = drive_file['downloadUrl']
        #print download_url
        if download_url:
          resp, content = drive_service._http.request(download_url)
          if resp.status == 200:
            #print 'Status: %s' % resp
            g = open('location.xml','w') 
            g.write(content)
            g.close()
          else:
            print 'An error occurred: %s' % resp
            return None
        else:
          # The file doesn't have any content stored on Drive.
          print 'nothing in there'
          return None

    #parse location file
    tree = ET.parse('location.xml')
    root = tree.getroot()
    ip = ''
    port = ''


    #Parse ip and port no from local copy of location.xml file
    for address in root.findall('address'):
        id = address.find('ID')
        port = address.find('port')

    check_Input.append(port.text)
    check_Input.append(client)
    check_Input.append(id.text)
    print port.text
    print 'verifying...'
    print 'Location Updated!'
    

def loadXML(link):
    #print "loadxml"
    tempLink = raw_input('Enter the link to location.xml file:')
    link.append(tempLink)

    replacedString = tempLink.replace('www','dl')
    replacedString2 = replacedString.replace('dropbox','dropboxusercontent')
    #get content of location file
    file = urllib2.urlopen(replacedString2)

    html = file.read()
    output = open('location.xml','wb')
    output.write(html)
    output.close()


def uploadLocation(client):
    #update the location file in dropbo
    g = open('location.xml')
    response = client.put_file('/location.xml',g,overwrite=True)
    g.close()

def sendEmail(check_Input):
    
    # Create socket called clientSocket and establish a TCP connection with mailserver
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((mailserver, serverPort))

    recv = clientSocket.recv(1024)
    print recv
    if recv[:3] != '220':
        print '220 reply not received from server.'

    # Send HELO command and print server response.
    heloCommand = 'HELO localhost\r\n'
    clientSocket.send(heloCommand)
    recv1 = clientSocket.recv(1024)
    print recv1
    if recv1[:3] != '250':
        print '250 reply not received from server.'

    #TLS
    starttlsCommand = 'STARTTLS \r\n'
    clientSocket.send(starttlsCommand)
    recv10 = clientSocket.recv(1024)
    print recv10

    #SSL wrap
    ssl_sock = ssl.wrap_socket(clientSocket, ssl_version=ssl.PROTOCOL_TLSv1)

    #Send HELO again
    heloCommand = 'HELO \r\n'
    ssl_sock.send(heloCommand)
    recv15 = ssl_sock.recv(1024)
    print recv15
    if recv15[:3] != '250':
        print '2nd HELO reply not received from server.'

    # Send AUTH command and print server response.
    authCommand = 'AUTH LOGIN \r\n'
    ssl_sock.send(authCommand)
    recv11 = ssl_sock.recv(1024)
    print recv11
    if recv11[:3] != '334':
        print 'LOGIN reply not received from server.'

#USERNAME
    a = raw_input('Enter Sender Email Address: ')
    a_encoded = base64.b64encode(a)
    username = a_encoded + '\r\n'
#username = raw_input('Provide Username: ')
    ssl_sock.send(username)
    recv20 = ssl_sock.recv(1024)
    print recv20

#PASSWORD
    b = raw_input('Enter Password: ')
    b_encoded = base64.b64encode(b)
    password = b_encoded + '\r\n'
    #password = raw_input('Provide Password: ')
    ssl_sock.send(password)
    recv30 = ssl_sock.recv(1024)
    print recv30

    # Send MAIL FROM command and print server response.
    mailfromCommand = 'MAIL FROM: <' + a + '>\r\n'
    ssl_sock.send(mailfromCommand)
    recv2 = ssl_sock.recv(1024)
    print recv2
    if recv2[:3] != '250':
        print 'MAIL FROM reply not received from server.'

# Send RCPT TO command and print server response.
    rcpttoCommand = 'RCPT TO: <'+ raw_input('Enter Recepient Email Address:  ')+'>\r\n'
    ssl_sock.send(rcpttoCommand)
    recv3 = ssl_sock.recv(1024)
    print recv3
    if recv3[:3] != '250':
     print '250 reply not received from server.'

# Send DATA command and print server response.
    dataCommand = 'DATA  \r\n'
    ssl_sock.send(dataCommand)
    recv4 = ssl_sock.recv(1024)
    print recv4
    if recv4[:3] != '354':
        print '354 reply not received from server.'

# Send message data.
    c = raw_input('Enter your message:  ')
    msg = "\r\n" + c
    ssl_sock.send(msg)

# Message ends with a single period.
    endmsg = "\r\n.\r\n"
    ssl_sock.send(endmsg)
    recv6 = ssl_sock.recv(1024)
    print recv6
    if recv6[:3] != '250':
        print '250 reply not received from server.'



def updateStatus(check_Input,client):
    
    print "Enter all fields, enter 'None' for a field that doesn't applies"
    statusType = ''
    statusTime = ''
    statusInfo = ''
    statusTag = ''
    statusItem = ''

    #Get User Input
    statusType = raw_input('Enter status type:')
    statusTime = str(datetime.datetime.now())
    statusInfo = raw_input('Enter status information:')
    statusTag = raw_input('Enter tags separated by commas:')
    statusItem = raw_input('Enter status item:')
    print 'Updating Status...'

    tree = ET.parse('location.xml')
    root = tree.getroot()
    content = ''

    #Parse ip and port no from local copy of location.xml file
    for address in root.findall('links'):
        content = address.find('content')

    contentText = content.text

    replacedString = contentText.replace('www','dl')
    replacedString2 = replacedString.replace('dropbox','dropboxusercontent')
    #print replacedString2
    file = urllib2.urlopen(replacedString2)
    statuses = file.read()


    versionCount = statuses.count('version')

    #Create xml tree
    content = ET.Element('content')
    version = ET.SubElement(content,'version')
    version.text = str(versionCount/2 + 1)
    if statusType.find('None')==-1:
        type = ET.SubElement(version, 'type')
        type.text = statusType
    if statusTag.find('None')==-1:
        tag = ET.SubElement(version,'tag')
        tag.text = statusTag
    time = ET.SubElement(version,'time')
    time.text = str(datetime.datetime.now())
    if statusItem.find('None')==-1:
        item = ET.SubElement(version,'item')
        item.text = statusItem
    if statusInfo.find('None')==-1:
        info = ET.SubElement(version,'info')
        info.text = statusInfo

    tree = ET.ElementTree(content)

    tree.write('tempTree.xml')

    treeFile = open('tempTree.xml','r')
   
    #append it to local content file
    g = open('content.xml','a')
    g.write('\n')
    g.write(treeFile.read())
    g.close()
    treeFile.close()
    
    #update the content file in dropbox
    g =open('content.xml','r')

    response = client.put_file('/content.xml',g,overwrite=True)

    g.close()
   
    print 'Status Updated!'



def main():

        f =open(databaseName,'w')
        conn = sqlite3.connect(databaseName)
        c = conn.cursor()
        print 'Creating databaase....'
        c.execute("DROP TABLE IF EXISTS %s"%(tableName))
        c.execute("CREATE TABLE %s (locationLink text, user_ID char, user_IP char, user_tcpPort int, ConnectionArrayOffset int)" %(tableName))
        print 'Done Creating Database'
        conn.close()

        cloudProvider = ''
        print '1. Dropbox'
        print '2. Google Drive'
        cloudProvider = raw_input('Chose a cloud provider to test:')


        if cloudProvider==str(1) or cloudProvider==str(2):
            getLocationFileData(inputEntered,cloudProvider)
            Name.append(inputEntered[3]) 

        else:
            print 'Invalid Input'
     
        chat_Listen = Chat_Listen()
        tcpConnections.append(chat_Listen)
        tcpConnections[0].tcpPort = inputEntered[1]
       
        tcpConnections[0].start()
        # chat_Listen.start()
        UserId.append('U')

        updateLocationXML()
        uploadLocation(inputEntered[2]) 

        while 1:
            print '1. Send Email (To initiate friendship).'
            print '2. Update Status'
            print '3. Enter link received in mail client to connect to others.'
            print '4. Send Chat Message'
            val = raw_input('Chose an option: ')
        
            if val==str(1):
            #thread.start_new_thread(sendEmail,(inputEntered,))
                sendEmail(inputEntered)

            elif val==str(2):
            #thread.start_new_thread(updateStatus,(inputEntered,))
                updateStatus(inputEntered,inputEntered[2])

            elif val==str(3):

                try:
                   loadXML(link)
                except:
                   print "loadxml no"

                try: 
                   connectWithOtherUser(link,UserId)

                except:
                   print 'no connectionwith'


                UserId.append('U')

            elif val==str(4):
                time.sleep(1)
                print 'Note: If you are chatting with this user for first time, start by sending friend command'
                msg = raw_input('Type your name followed by your message (e.g Jacob Hi there): ')
                s = msg
                s = s.split()
                conn = sqlite3.connect(databaseName)
                c = conn.cursor()
                try:
                    c.execute("SELECT ConnectionArrayOffset from %s WHERE user_ID='%s'" %(tableName,s[0]))
                    result = str(c.fetchone()).translate(None, "(),")
                    index = int(result)
                    tuple1,tuple2,tuple3 = msg.partition(s[0])
                    tcpConnections[index].sock.sendall(Name[0] + ':' + tuple3 )
                    print 'DELIVERED ' + s[0] + '\n'
                except:
                    print "\nNo connection with " + s[0]
                conn.close()

            else:
                print 'Wrong Input. Enter again'


if __name__ == "__main__":
    main()


