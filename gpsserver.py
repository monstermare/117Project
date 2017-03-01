#!/usr/bin/env python3

"""
this server assumes the client gets its own geocode.
once clients are connected to the server, the server sends back those following requests from the server
    1. update client's location (geocode).
    2. update client's status (interesting, habit, etc).
    3. request to find other people have same interesting
    4. request posting party
data that you can fetch from the database will be:
    1. userid
    2. geocode
    3. connection(online/offline)
    4. time(recent connection made)
    5. status
"""
#TWISTED module for asynchronous server network
from twisted.internet import reactor, protocol, endpoints
from twisted.web.client import getPage #
from twisted.logger import Logger

#for mariadb(mysql)
import pymysql

import math
import time
import sys
import linecache
import logging
import logging.handlers

#server information
import serverstatus as ss

def deferror():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))   

class MyError(Exception):
    def __init__(self,msg):
        self.msg=msg

    def __str__(self):
        return self.msg

class database():
    def __init__(self,cdata,table,category):
        self.data=cdata
        self.table = table
        self.ca="("
        self.val="("
        try:
            for element in category:
                self.ca+=str(element)+","
                self.val+="%s,"
            self.ca=self.ca[:-1]+")"
            self.val=self.val[:-1]+")"
        except:
            raise MyError(deferror())
    
    def insertdata(self,data):
        """data format must be tuple"""
        con = pymysql.connect(host=self.data[0], user=self.data[1], password=self.data[2],
                           port=self.data[3], db=self.data[4], charset=self.data[5])
        try:
            with con.cursor() as curs:
                sql = "insert into "+self.table+self.ca+" values "+self.val
                curs.execute(sql, data)
            con.commit()
        except:
            raise MyError(deferror())
        finally:
            con.close()
    
    def fetchdata(self,data,select='*',diction=False):
        """data contains SELECT statement
        default selection is all"""
        con = pymysql.connect(host=self.data[0], user=self.data[1], password=self.data[2],
                           port=self.data[3], db=self.data[4], charset=self.data[5])
        try:
            if(diction):
                with con.cursor(pymysql.cursors.DictCursor) as curs:
                    sql = "select "+select+" from "+self.table+" where "+data
                    curs.execute(sql)
                    raw = curs.fetchall()
            else:
                with con.cursor() as curs:
                    sql = "select "+select+" from "+self.table+" where "+data
                    curs.execute(sql)
                    raw = curs.fetchall()
        except:
            raise MyError(deferror())
        finally:
            con.close()
            return raw
    
    def updatedata(self,key,data):
        """data is 'set' part and key is 'where' part"""
        con = pymysql.connect(host=self.data[0], user=self.data[1], password=self.data[2],
                           port=self.data[3], db=self.data[4], charset=self.data[5])
        try:
            with con.cursor() as curs:
                sql = "update "+self.table+" set "+data+" where "+key
                logger.debug("<SYSTEM> "+sql)
                curs.execute(sql)
            con.commit()
        except:
            raise MyError(deferror())
        finally:
            con.close()
    
    def deletedata(self,key):
        con = pymysql.connect(host=self.data[0], user=self.data[1], password=self.data[2],
                           port=self.data[3], db=self.data[4], charset=self.data[5])
        try:
            with con.cursor() as curs:
                sql = "delete from "+self.table+" where "+key
                curs.execute(sql)
            con.commit()
        except:
            raise MyError(deferror())
        finally:
            con.close()


class Interpreter():
    def __init__(self,sql):
        self.sql = sql

    def gpsdist(self, la1, lo1, la2, lo2):
        la1 = math.radians(la1)
        lo1 = math.radians(lo1)
        la2 = math.radians(la2)
        lo2 = math.radians(lo2)
        dla = la2 - la1 
        dlo = lo2 - lo1 
        a = math.sin(dla/2)**2 + math.cos(la1) * math.cos(la2) * math.sin(dlo/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 3956 #mile
        return c * r

    def update_geocode(self,data):
        try:
            i=int(data[1])
            a=float(data[2])
            o=float(data[3])
            t=float(data[4])
            key = ss.category[0]+"="+str(i)
            data = ss.category[1]+"="+str(a)+","+ss.category[2]+"="+str(o)+","+ss.category[4]+"="+str(t)
            self.sql.updatedata(key,data)
        except:
            raise MyError(deferror())
        finally:
            return "geocode has been updated"

    def update_connection(self,data):
        try:
            i=int(data[1])
            c=int(data[2])
            key = ss.category[0]+"="+str(i)
            data = ss.category[1]+"="+str(c)
            self.sql.updatedata(key,data)
        except:
            raise MyError(deferror())
        finally:
            return "connection status has been updated"

    def update_status(self,data):
        try:
            i=int(data[1])
            s=str(data[2])
            key = ss.category[0]+"="+str(i)
            data = ss.category[1]+"="+str(s)
            self.sql.updatedata(key,data)
        except:
            raise MyError(deferror())
        finally:
            return "status has been updated"

    def get_connected_user(self,data):
        try:
            i=int(data[1])
            data = "userid!="+str(i)+" AND connection!=0"
            select = "userid"
            info = self.sql.fetchdata(data,select)
            return list(info)
        except:
            MyError(deferror())

    def get_user_info(self,data,personal=False):
        try:
            i=int(data[1])
            s=str(data[2])
            data = "userid="+str(i)
            info = self.sql.fetchdata(data,s,True)
            if(personal):
                info = info[0]
            return info
        except:
            MyError(deferror())

    def get_user_geocode(self,data,personal=False):
        try:
            i=int(data[1])
            s=float(data[2])
            select = "userid,geocode_la,geocode_lo"
            data = "userid="+str(i)
            info = self.sql.fetchdata(data,select)
            if(personal):
                info = info[0]
            return list(info)
        except:
            MyError(deferror())

    def get_user_dist(self,data,pivot):
        try:
            i=int(data[1])
            s=float(data[2])
            select = "userid,geocode_la,geocode_lo"
            data = "connection!=0"
            raw = self.sql.fetchdata(data,select)
            satisfied = []
            la1 = pivot[1]
            lo1 = pivot[2]
            for element in raw: # (userid,la,lo)
                la2 = element[1]
                lo2 = element[2]
                if(s>=self.gpsdist(la1,lo1,la2,lo2)):
                    satisfied.append(list(element))
            return satisfied
        except:
            MyError(deferror())
                

class Receiver(protocol.Protocol):
    """
    this receives request and data from the client and process it
    the data should have following form:
    <USERNAME> <REQUEST TYPE> <DATA> (like r-type instructions)
    i.e. 1 2261287 37.423021 -122.083739 1487452563.178123
    2261287 = userid \ 1 = update geocode(has three parameters: latitude, longitude, and time(see time.time()) )
    the receiving data will be split by white spaces
    """
    sql=database(ss.connectiondata,ss.table,ss.category)
    def __init__(self):
        self.i = Interpreter(self.sql)

    def connectionMade(self):
         logger.debug("<SYSTEM> opening connection")

    def dataReceived(self, data):
        decoded = data.decode('utf-8')
        self.data = decoded.split()
        self.com = self.data[0]
        msg = ""
        try:
            if(len(self.data)==0):
                raise MyError("null") #this checks if data is either null or only containing whte space
            if(type(self.com) is int):
                raise MyError("incorrect command format")
            elif(self.com=='1'): #update geocode and time (i.e. 1 2261287 37.423021 -122.083739 1487452563.178123)
                if(len(self.data)==5):
                    logger.info("<SYSTEM> data received from "+self.data[1]+": Update geocode")
                    msg = self.i.update_geocode(self.data)+"\r\n"
                else:
                    raise MyError("Invalid arguments")
            elif(self.com=='2'): #update connection status (i.e. 2 2261287 1)
                if(len(self.data)==3):
                    logger.info("<SYSTEM> data received from "+self.data[1]+": Update connection status")
                    msg = self.i.update_connection(self.data)+"\r\n"
                else:
                    raise MyError("Invalid arguments")
            elif(self.com=='3'): #update status (i.e. 3 2261287 I have a dream) -> (3,2261287,'I have a dream')
                if(len(self.data)>3):
                    logger.info("<SYSTEM> data received from "+self.data[1]+": Update status")
                    modified = [self.data[0],self.data[1],' '.join(self.data[2:])]
                    msg = self.i.update_status(modified)
                else:
                    raise MyError("Invalid arguments")
            elif(self.com=='11'): #fetch user information (i.e. 11 2261287)
                if(len(self.data)==2):
                    logger.info("<SYSTEM> data received from "+self.data[1]+": Get user info")
                    self.data.append("*")
                    info = self.i.get_user_info(self.data,True)
                    msg = str(info)+"\r\n"
                else:
                    raise MyError("Invalid arguments")
            elif(self.com=='12'): #fetch list of users are near to you (i.e. 12 2261287 10000)
                if(len(self.data)==3):
                    logger.info("<SYSTEM> data received from "+self.data[1]+": Get user list "+self.data[2]+" away from the point")
                    lst = []
                    pivot = self.i.get_user_geocode(self.data,True)
                    lst = self.i.get_user_dist(self.data,pivot)
                    msg = "FORMAT: USERID/LATITUDE/LONGITUDE\r\n"
                    for element in lst:
                        for supelement in element:
                            msg+=str(supelement)+" "
                        msg+="\r\n"
                else:
                    raise MyError("Invalid arguments")
            elif(self.com=='13'): #fetch list of users are currently connected (i.e. 13 2261287)
                if(len(self.data)==2):
                    logger.info("<SYSTEM> data received from "+self.data[1]+": Get logged-on user list")
                    lst = self.i.get_connected_user(self.data)
                    msg = ""
                    for element in lst:
                        for supelement in element:
                            msg+=str(supelement)+" "
                        msg+="\r\n"
                else:
                    raise MyError("Invalid arguments")
            else:
                raise MyError("unknown command")
        except MyError as e:
            err = "<ERROR>"+str(e)
            logger.error(err)
            err +="\r\n"
            self.transport.write(err.encode('utf-8'))
            #self.transport.loseConnection()
        except:
            err = "<CRITICAL> Undefined Error:"+deferror()
            logger.critical(err)
            err="unable to process your request\r\n"
            self.transport.write(err.encode('utf-8'))
            #self.transport.loseConnection()
        finally:
            self.transport.write(msg.encode('utf-8'))
    
    def urlFormat(self,la,lo,rad):
            url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='
            url+=str(la)+','+str(lo)+'&radius='
            url+=str(rad)+'&key='
            url+=conf.API_KEY
            return url

class gpsserver(protocol.Protocol):
    def __init__(self,msg): #initialization
        self.msg = msg

    def connectionMade(self): # when the client is connected to the server
        self.transport.write(self.msg)

    def connectionLost(self, reason): # when the client is disconnected from the server
        logger.debug("<SYSTEM> connection lost From Server")

    def dataReceived(self,data): # when the server receives data from the clients
        logger.info("<SYSTEM> data received: "+data)
        self.transport.loseConnection()

class echoserver(protocol.Factory):
    def buildProtocol(self,addr):
        return Receiver()

class ClientFactory(protocol.ClientFactory):
    def __init__(self,msg):
        self.msg = msg

    def buildProtocol(self,addr):
        return gpsserver(self.msg)

logger = logging.getLogger('log')
filename = "./test.log"
filehandler = logging.FileHandler(filename)
streamhandler = logging.StreamHandler()
formatter = logging.Formatter('(%(asctime)s)%(lineno)s:%(filename)s $[%(levelname)s] %(message)s')
# (11-30-2016 18:21:35,200)262:server.py $[INFO] <SYSTEM> message
filehandler.setFormatter(formatter)
streamhandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)


