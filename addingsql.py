#!/usr/bin/env python3

import gpsserver
import serverstatus as ss
import random

la = random.random()
lo = random.random()
a = gpsserver.database(ss.connectiondata,ss.table,ss.category)
for x in range(2261288,2261295):
    b = (x,la,lo,1,0,'a')
    a.insertdata(b)
#a.updatedata("userid=2261287","geocode_la=1,geocode_lo=2,time=3")
