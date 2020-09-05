import numpy as np
import math
from time import sleep
import serial
import subprocess
import os
import signal
#p=subprocess.Popen(["python /home/pi/Desktop/retrievAngle.py"],shell=True)

def getfile(filename,results):

   f = open(filename)
   filecontents = f.readlines()

   for line in filecontents:
        if len(line) > 0:
                foo = line.strip('\n')
                results.append(foo)
                continue
   return results

def retrievangle():
#   global pitch_angle,yaw_angle
      if ser.is_open:
        global received_data
        received_data = ser.read()              #read serial port
        sleep(0.05)
        data_left = ser.inWaiting()             #check for remaining byte
        received_data += ser.read(data_left)
        received_data=received_data.split('N')[0]
        if received_data.strip():
       # line is not empty or just blanks
            toks = received_data.split(",")
    #       print len(toks) 
            if len(toks)==2:
           # unpack safely
                   a,b = toks
                   try:
                        global pitch_angle,yaw_angle
                        pitch_angle=float(a)
                        yaw_angle=float(b)
                   except ValueError, e:
#                        print 'Line {i} is corrupt!'
                        pitch_angle=0
                        yaw_angle=0

            else:
#                   print("unable to parse {}".format(received_data))      
                   pitch_angle=0
                   C=0
        else:
            pitch_angle=0
            yaw_angle=0
#      print "pitch:",pitch_angle
#      print "yaw:",yaw_angle
def computeTgtGps():
        global lat_deg,lng_deg
        coordinates=[]
        getfile('/home/pi/Desktop/Onboard-SDK-3.7/build/bin/coordinates.txt',coordinates)
        print coordinates
#        pitchAngle=float(angles[0])
#   yawAngle=float(angles[1])
        if len(coordinates)==10: 
            airHead=float(coordinates[0]) #float(30)
            yawAngle=float(yaw_angle)
            pitchAngle=float(pitch_angle)
            airLat=float(coordinates[1]) #float(12.678)
            airLong=float(coordinates[2]) #float(80.565457)
            airAlt=float(coordinates[4])
           
            gpsStatus=(coordinates[3])
        else:
#                print("unable to parse {}".format(coordinates)) 
                airHead=0
                yawAngle=0
                pitchAngle=0
                airLat=0
                airLong=0
                airAlt=0
                gpsStatus=0
    
	global i
        if i<=3:
            global alt
            alt=airAlt
            if alt<0:
                alt=0
        temp = airHead +yawAngle;
        if temp<0:
           temp=360+temp
        tgtHead=math.fmod((temp),360.0)

        aL=math.radians(airLat)
        aO=math.radians(airLong)
        aT=math.radians(tgtHead)
        sleep(0.05)
        height=airAlt-alt
        if height<0:
            height=0
        tgtDist=(math.tan(math.radians(pitchAngle))*(height))
    #   tgtDist=(math.tan(pitchAngle)*(airAlt))
        tD=tgtDist/(1000*(6378.1))
        tL =math.asin(math.sin(aL)*math.cos(tD) + math.cos(aL)*math.sin(tD)*math.cos(aT));
        tO = aO + math.atan2(math.sin(aT)*math.sin(tD)*math.cos(aL) , math.cos(tD)-math.sin(aL)*math.sin(tL));

        tarLat=math.degrees(tL)
        tarLong=math.degrees(tO)
        lat_deg = to_deg(tarLat, ["S", "N"])
        lng_deg = to_deg(tarLong, ["W", "E"])
     
#        print "dist:",tgtDist
#        print "tgtHead:",tgtHead
#        print "tarLat:", lat_deg
#        print "tarLong:",lng_deg
#        print "Altitude:",height
        
        ser.write("A")
        data=','+(str(tgtHead))[0:6]+','+(str(airLat))[0:8]+','+(str(airLong))[0:8]+','+(str(lat_deg))[0:8]+','+(str(lng_deg))[0:8]+','+(str(tgtDist))[0:8]+','+(str(height))[0:8]+','
        print data
    #    for i in range(4):
    #         print coordinatesData[i]	   
        ser.write(data)
        ser.write("B")
#        sleep(1)
        
        i=i+1
#    else:
#        print "GPS is not fixed! Waiting for GPS fix"
#   print IntAlt
def to_deg(value, loc):
      if value < 0:
        loc_value = loc[0]
        value=str(value)+" "+loc_value
      elif value > 0:
        loc_value = loc[1]  
        value=str(value)+" "+loc_value
      else:
        loc_value = ""
#     abs_value = abs(value)
      #abs_value = (value)
#     deg =  int(abs_value)
      #deg =  (abs_value)
#     t1 = (abs_value-deg)*60
#     min = int(t1)
#     sec = round((t1 - min)* 60, 5)
#     return (deg, min, sec, loc_value)
      return (value)

ser = serial.Serial ("/dev/ttyS0", 115200)
i=0
while True:
#    sleep(1)
    retrievangle()
    computeTgtGps()
#os.killpg(os.getpgid(p.pid),signal.SIGTERM)

