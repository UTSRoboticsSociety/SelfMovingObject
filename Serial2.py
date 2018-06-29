import serial
import time
import serial.tools.list_ports


class Serial2(object):
    def __init__(self, port, baud, bytesize, parity, stopbits, timeout,
                 xonxoff, rtscts, writetimeout,
                 dstdtr, intercharttimeout, usingSerial):
        self.usingSerial = usingSerial  # To disable serial functionality
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

        #self.openSerial("{\"data\":[1800,40]}", 11)
        self.openSerial("{\"Mode\":\"Drive\",\"Throttle\":\"50\",\"Driection\":\"1\",\"Steering\":\"90\"}", 63)

    def openSerial(self, message, length):
        print("opening the serial...")
        if(self.usingSerial):
            try:
                # ports = list(serial.tools.list_ports.comports())
                # for p in ports:
                #     if 'Arduino' in p.description:
                #         self.port = p

                # open serial port
                # self.ser = serial.Serial(self.port,
                #                          self.baud,
                #                          self.bytesize,
                #                          self.parity,
                #                          self.stopbits,
                #                          self.timeout,
                #                          self.xonxoff,
                #                          self.rtscts,
                #                          self.writetimeout,
                #                          self.dstdtr,
                #                          self.intercharttimeout)

                self.ser = serial.Serial(self.port,self.baud, timeout = self.timeout)

                # check which port was really used
                print(self.ser.portstr+" opened")
                print("Port %s set to %d %s%s%s (%ds timeout)" %
                      (self.port,
                       self.baud,
                       self.bytesize,
                       self.parity,
                       self.stopbits,
                       self.timeout))

                print("sending '%s'" % message)
                # write a string
                self.ser.write(bytes(message, encoding="ascii"))

            except serial.SerialException:
                print(serial.SerialException)
                print("failed to open %s" % self.port)
                print("Likely you are trying to open a port \
                      that is already open (hasnt been closed properly)")
                print("possible fix is to unplug COM8")
                pass

    def sendMessage(self, message, length):
        print("Tset")
        if(self.usingSerial):
            try:
                # print ("Port %s set to %d %s%s%s (%ds timeout)" %
                # (self.port,self.baud,self.bytesize,
                # self.parity,self.stopbits,self.timeout))
                print ("sending '%s'"%message)
                # write a string
                self.ser.write(bytes(message, encoding="ascii"))
                time.sleep(0.015)
            except serial.SerialException as e:
                print(e.errno)
                print(e.strerror)
                print("failed to open %s" % self.port)
                pass
        print("test")
