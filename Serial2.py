import serial
import time
import serial.tools.list_ports


class Serial2(object):
    def __init__(self, port, baud, bytesize, parity, stopbits, timeout, xonxoff, rtscts, writetimeout, dstdtr, intercharttimeout):
        self.usingSerial = True #so we can turn serial functionality off
        self.port = port
        self.baud = baud
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.writetimeout = writetimeout
        self.dstdtr = dstdtr
        self.intercharttimeout = intercharttimeout
        self.ser = None

        self.openSerial("{\"sensor\":\"gps\",\"time\":1351824120,\"data\":[1800,40]}", 11)

    def openSerial (self,message,length):
        if(self.usingSerial):
            try:
                ports = list(serial.tools.list_ports.comports())
                for p in ports:
                    if 'Arduino' in p.description:
                        self.port = p

                self.port = "/dev/ttyUSB0"
                self.ser = serial.Serial(self.port,self.baud,8,self.parity,self.stopbits,self.timeout,self.xonxoff,self.rtscts,self.writetimeout,self.dstdtr,self.intercharttimeout)  # open serial port
                print (self.ser.portstr+" opened")       # check which port was really used
                print ("Port %s set to %d %s%s%s (%ds timeout)" % (self.port,self.baud,self.bytesize,self.parity,self.stopbits,self.timeout))
                print ("sending '%s'"%message)
                self.ser.write(bytes(message, encoding="ascii"))      # write a string

            except serial.SerialException:
                print(serial.SerialException)
                print("failed to open %s"%self.port)
                print("Likely you are trying to open a port that is already open (hasnt been closed properly)")
                print("ez fix is to unplug COM8")
                pass

    def sendMessage(self, message,length):
        if(self.usingSerial):
            try:
                print ("Port %s set to %d %s%s%s (%ds timeout)" % (self.port,self.baud,self.bytesize,self.parity,self.stopbits,self.timeout))
                print ("sending '%s'"%message)
                self.ser.write(bytes(message, encoding="ascii"))      # write a string
                time.sleep(0.015)
            except serial.SerialException:
                print("failed to open %s"%self.port)
                pass






    # Might be needed at the end of open serial:
    # s=ser.read(length)
    # print(str(s,"ascii"))
    # ser.close()             # close port
    # print ("port closed")



    #-----------------------------------------------------------------------
    # def main():
    #
    #     value = str(90)
    #
    #     message =  "{\"sensor\":\"gps\",\"time\":1351824120,\"data\":[1800," + value + "]}"
    #     print("Opening Serial and Sending Message:")
    #     print(message)
    #     ser = openSerial('COM8',9600,8,serial.PARITY_NONE,1,2,False,True,2,False,None,message,11)
    #
    #     #raspberrypi
    #     for x in range(1000):
    #         for i in range(40,130, 3):
    #         #value = str((i * 10) % 180)
    #             value = str(i)
    #             message =  "{\"sensor\":\"gps\",\"time\":1351824120,\"data\":[1800," + value + "]}";
    #             print("Sending Message:")
    #             print(message)
    #             sendMessage('COM8',9600,8,serial.PARITY_NONE,1,2,False,True,2,False,None,message,11 ,ser)
    #             print("sleeping")
    #
    #             time.sleep(0.16)
        #openSerial('COM3',9600,8,serial.PARITY_NONE,1,2,False,False,2,True,None,'^WHORU$',11)

    #-----------------------------------------------------------------------
    #if __name__=="__main__":
    #    main()
