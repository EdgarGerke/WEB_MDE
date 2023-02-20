import asyncio
import websockets
import time
import json
import serial.tools.list_ports
import serial
import random

clear_axes=False
async def senddata(websocket, path):
    global clear_axes

    while True:
        i=0
        portnamex = ""
        portnamey = ""
        for port in serial.tools.list_ports.comports():
            if port.description == "E201 USB Encoder Interface" and i == 0:
                portdevx = port.device
                i += 1
            elif port.description == "E201 USB Encoder Interface" and i == 1 and port.name != portnamex:
                portdevy = port.device
                # print(port.device)
                i += 1
            # elif port.name == "ttyUSB0":
            #     portdevx = port.name
            #     i = 2
        if i == 2:
            break
        else:
            time.sleep(0.3)

    messinterface_x = serial.Serial(portdevx, timeout=1, rtscts=True, baudrate=115200);
    messinterface_y = serial.Serial(portdevy, timeout=1, rtscts=True, baudrate=115200)
    messinterface_x.write("r".encode("utf-8"));
    TempValue_x = messinterface_x.read(8).decode("utf-8");
    messinterface_y.write("r".encode("utf-8"));
    TempValue_y = messinterface_y.read(8).decode("utf-8");
    TempValue_x = TempValue_x.replace("\r", "")
    TempValue_y = TempValue_y.replace("\r", "")

    SN_1_axis = TempValue_x[:6]
    SN_2_axis = TempValue_y[:6]
    stoplooping=False
    clear_axes = False
    while stoplooping != True:
        # if geometryfunction==False:
        messinterface_x.write("?".encode("utf-8"));
        TempValue_x_ = messinterface_x.read_until('\r'.encode('utf-8')).decode("utf-8");
        messinterface_y.write("?".encode("utf-8"));
        TempValue_y_ = messinterface_y.read_until('\r'.encode('utf-8')).decode("utf-8");
        TempValue_y_ = TempValue_y_.strip()
        TempValue_x_ = TempValue_x_.strip()
        if ":" not in TempValue_x_ or ":" not in TempValue_y_:
            TempValue_x_ = TempValue_x_.replace("  ", ":")
            TempValue_y_ = TempValue_y_.replace("  ", ":")

        TempValue_x_ = TempValue_x_.replace(" ", "")
        TempValue_y_ = TempValue_y_.replace(" ", "")
        # print(TempValue_x_,TempValue_y_)
        index_y = TempValue_y_.index(":");
        index_x = TempValue_x_.index(":");
        if " " in TempValue_y_ or " " in TempValue_x_:
            TempValue_x_ = TempValue_x_.replace(" ", "")
            TempValue_y_ = TempValue_y_.replace(" ", "")


        x = float(float(TempValue_y_[0:index_y])) / 10000.
        y = float(float(TempValue_x_[0:index_x])) / 10000.

        x = random.uniform(-10.5, 20.5)
        y = random.uniform(-10.5, 20.5)
        # print(calibval_y)
        if clear_axes == True:
            messinterface_x.write("z".encode("utf-8"));
            # messinterface_x.waitForBytesWritten(300);
            messinterface_y.write("z".encode("utf-8"))
            clear_axes = False
            print("clearrrrrr")

        event = {"encoder":[{"serial_number": SN_1_axis,"value": x}, {"serial_number": SN_2_axis,"value": y}], "SN_Mikroskop": "0408002"}
        await websocket.send(json.dumps(event))
        time.sleep(.02)




async def getdata(websocket, path):
    global clear_axes
    print("clearrrrrr")
    data = await websocket.recv()
    print("clearrrrrr1")
    clear_axes=True

start_server = websockets.serve(senddata, "localhost", 8000)
start_server2 = websockets.serve(getdata, "localhost", 8001)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(start_server2)
asyncio.get_event_loop().run_forever()

