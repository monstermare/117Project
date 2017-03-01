from gpsserver import *

serverport = 1234
hostname = 'localhost'
endpoints.serverFromString(reactor,"tcp:{}".format(serverport)).listen(echoserver())
reactor.run()
