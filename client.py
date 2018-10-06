# ICS226 Network Programming Lab 1 Solution
# Andrew Bishop
# Sept. 20 /18

import sys
import socket
from urllib.parse import urlparse

URL = sys.argv[1]
parsed_url = urlparse(URL)
host = parsed_url.netloc
resource = parsed_url.path
html2textHost = 'rtvm.cs.camosun.bc.ca'

if not resource:
  resource = "/"

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# now connect to the web server on port 80
s.connect((host, 80))
request = "GET " + resource + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
s.send(request.encode())

# connect to html2text server until the server is expecting bytes of HTML code
s2.connect((html2textHost, 10010))
data2 = s2.recv(1024)
data_str2 = data2.decode("utf-8")

if data_str2 == 'READY':
  state = 1
  previousBlock = ''
  while state != 4:

    # read in headers from web server, looking for <HTML>. When <HTML> is read, move to state 2
    if state == 1:
      currentBlock = s.recv(1024).decode("utf-8")
      if "<HTML>" in currentBlock.upper():
        if "</HTML>" in currentBlock.upper():
          start = currentBlock.index("<HTML>")
          end = currentBlock.index("</HTML>") + 7
          s2.send(currentBlock[start:end].encode())
          state = 3
        else:
          start = currentBlock.index("<HTML>")
          previousBlock = currentBlock[start:]
          state = 2

    # read in blocks from web server, sending to html2text server
    if state == 2:
      currentBlock = s.recv(1024).decode("utf-8")
      if "</HTML>" in previousBlock + currentBlock:
        if "</HTML>" in previousBlock:
          s2.send(previousBlock.encode())
          previousBlock = ''
          state = 3
        else:
          both = previousBlock + currentBlock
          end = (both).find("</HTML") + 7
          currentBlock = both[:end]
          previousBlock = ''
          s2.send(currentBlock.encode())
          state = 3
      else:
        s2.send(previousBlock.encode())
        previousBlock = currentBlock

    # receive from html2text server, printing blocks
    if state == 3:
      currentBlock = s2.recv(1024).decode("utf-8")
      if 'ICS 226 HTML CONVERT COMPLETE' in previousBlock.upper() + currentBlock.upper():
          if 'ICS 226 HTML CONVERT COMPLETE' in previousBlock.upper():
            previousBlock = previousBlock.rstrip('ICS 226 HTML CONVERT COMPLETE')
            print(previousBlock, end = "")
            state = 4
          else:
            bothBlocks = previousBlock + currentBlock
            bothBlocks = bothBlocks.rstrip("ICS 226 HTML CONVERT COMPLETE")
            print(bothBlocks, end="")
            state = 4
      else:
        print(previousBlock, end = "")
        previousBlock = currentBlock
      

# close the two sockets
s.close
s2.close


