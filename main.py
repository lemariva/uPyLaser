import gc
import time
import socket
from uos import uname
from uPySensors.vl53l0x import VL53L0X

# creating object distance sensor
sensor = VL53L0X(i2c=0)

if (uname().sysname == 'WiPy'):
    from machine import RTC
else:
    from ESP32MicroPython.timeutils import RTC

rtc = RTC()
rtc.ntp_sync("pool.ntp.org")

# minimal webserver
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('', 80))
soc.listen(0)
while True:
    conn, addr = soc.accept()
    try:
        print("Got a connection from %s" % str(addr))
        distance = sensor.read()
        print("Distance: %d" % distance)
        request = conn.recv(1024)
        conn.sendall('HTTP/1.1 200 OK\nConnection: close\nServer: nanoWiPy\nContent-Type: text/html\n\n')
        request = str(request)
        ib = request.find('Val=')
        up = request.find('update=yes')
        if ib > 0:
            #print("ib")
            ie = request.find(' ', ib)
            Val = request[ib+4:ie]
            conn.send(Val)
        elif up > 0:
            #print("up")
            conn.send(str(distance))
        else:
            #print("else")
            with open('lib/webpage.py', 'r') as html:
                lt = time.localtime()
                vs = html.read().replace('$DATA_DATE$', str(lt[0]) + '-' + str(lt[1]) + '-' + str(lt[2]) + ' ' + str(lt[3]) + ':' + str(lt[4]) + ':' + str(lt[5]))
                conn.send(vs)
        conn.sendall('\n')
    except OSError as ex:
        print('ERROR getting distance:', ex)
    finally:
        conn.close()
    print("Connection wth %s closed" % str(addr))
    gc.collect()
