import network
import socket
import struct
import _thread
from machine import Pin, I2C
import machine

from hwconfig import DISPLAY

def inet_aton(ip):
    return bytes(map(int, ip.split('.')))

def url_decode(s):
    res = ''
    i = 0
    length = len(s)
    while i < length:
        c = s[i]
        if c == '+':
            res += ' '
            i += 1
        elif c == '%':
            if i + 2 < length:
                res += chr(int(s[i+1:i+3], 16))
                i += 3
            else:
                res += c
                i += 1
        else:
            res += c
            i += 1
    return res

def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='Desk Buddy')
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
    DISPLAY.clear()
    DISPLAY.text("Connect to me", 0, 0, 1, 0, 128, 64, 1)
    DISPLAY.text("to set me up", 0, 8, 1, 0, 128, 64, 1)
    DISPLAY.text("WiFi Name:", 0, 16, 1, 0, 128, 64, 1)
    DISPLAY.text(" Desk Buddy", 0, 24, 1, 0, 128, 64, 1)
    DISPLAY.text("((i))", 0, 40, 1, 0, 128, 64, 1)
    DISPLAY.text("|", 0, 48, 1, 0, 128, 64, 1)
    DISPLAY.text("[o_o]", 0, 56, 1, 0, 128, 64, 1)
    DISPLAY.show()

def web_page():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Desk Buddy Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            display: flex;
            flex-direction: column;
            height: 100vh;
            justify-content: center;
            align-items: center;
            background-color: #f0f8ff; 
            font-family: Arial, sans-serif; 
        }
        h1 { color: #333; }
        form { 
            display: flex;
            flex-direction: column;
            align-items: center; 
            max-width: 300px; 
            width: 100%; 
            background-color: #fff; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        input[type=text], input[type=password] { 
            width: 80%; 
            padding: 10px; 
            margin: 5px 0 15px 0; 
            border: none; 
            background: #f1f1f1; 
            border-radius: 5px;
        }
        input[type=submit] { 
            width: 80%; 
            background-color: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            cursor: pointer; 
            border-radius: 5px;
        }
        input[type=submit]:hover { 
            background-color: #45a049; 
        }
        .emoji { font-size: 48px; }
    </style>
</head>
<body>
    <div class="emoji">🤖</div>
    <h1>Register your Desk Buddy!</h1>
    <form action="/" method="post">
        <label for="username">WiFi Name</label><br />
        <input type="text" id="username" name="username" required/><br />
        <label for="password">WiFi Password</label><br />
        <input type="password" id="password" name="password" required/><br />
        <input type="submit" value="Connect" />
    </form>
</body>
</html>"""

def start_web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print('Web server started on port 80')
    while True:
        conn, addr = s.accept()
        print('Connection from', addr)
        request = conn.recv(1024).decode()
        print('Request content:', request)

        # Handle request path
        if 'POST' in request:
            try:
                post_data = request.split('\r\n\r\n')[1]
                post_data = url_decode(post_data)
                params = dict(pair.split('=') for pair in post_data.split('&'))
                username = params.get('username', '')
                password = params.get('password', '')
                with open('wifi_config.py', 'w') as f:
                    f.write(f"ssid = '{username}'\nssid_password = '{password}'\n")
                response = """<h1>Thank you! You're all set!</h1>"""
                machine.soft_reset()
            except Exception as e:
                print('Error parsing POST data:', e)
                response = web_page()
        elif '/generate_204' in request:
            response = ''
        else:
            response = web_page()

        conn.sendall('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'.encode() + response.encode())
        conn.close()

def start_dns_server():
    ip = '192.168.4.1'
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(('', 53))
    print('DNS Server started on port 53')
    while True:
        try:
            data, addr = udps.recvfrom(1024)
            dns_response = data[:2] + b'\x81\x80' + data[4:6]*2 + b'\x00\x00\x00\x00' + data[12:] + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04' + inet_aton(ip)
            udps.sendto(dns_response, addr)
        except Exception as e:
            print('DNS server error:', e)

def main():
    setup_ap()
    _thread.start_new_thread(start_web_server, ())
    start_dns_server()

main()
