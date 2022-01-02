from math import *
import requests
import json
import time
import sched
from datetime import datetime
import reserve
s = sched.scheduler(time.time, time.sleep)
requests.packages.urllib3.disable_warnings()

# 同站租還.py


now_lat = 25.046699
now_long = 121.582297
radius = 0.5
stationID = "X1IG"
SDate = "2021-12-18 11:00:00"
EDate = "2021-12-18 21:00:00"
# SDate為開始時間  格式為:YYYY-MM-DD HH:MM:SS
# EDate為結束時間
# StationID: {"X0MW": "大樹藥局"}
# StationID: {"X1IG": "明峰街"}
dataiRent = {
	"Latitude": now_lat,
	"Longitude": now_long,
    "Mode": 0,
    "CarType": "",
    "SDate": SDate,
    "StationID": stationID,
    "EDate": EDate,
    "CarTypes": [
    ],
    "Radius": 2.5
}

header = {
    "content_type": "application/json",
    "authorization": "Bearer",
    "deviceid": "148012fc50db73b42a8291648681c177b",
    "charset": "UTF-8",
    "content-type": "application/json; charset=UTF-8",
    "content-length": "86",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/4.2.2",
    "pragma": "no-cache",
    "cache-control": "no-cache"
}

def Distance1(Lat_A,Lng_A,Lat_B,Lng_B): # 經緯度算距離
    ra=6378.140 #赤道半徑
    rb=6356.755 #極半徑 （km）
    flatten=(ra-rb)/ra  #地球偏率
    rad_lat_A=radians(Lat_A)
    rad_lng_A=radians(Lng_A)
    rad_lat_B=radians(Lat_B)
    rad_lng_B=radians(Lng_B)
    pA=atan(rb/ra*tan(rad_lat_A))
    pB=atan(rb/ra*tan(rad_lat_B))
    xx=acos(sin(pA)*sin(pB)+cos(pA)*cos(pB)*cos(rad_lng_A-rad_lng_B))
    c1=(sin(xx)-xx)*(sin(pA)+sin(pB))**2/cos(xx/2)**2
    c2=(sin(xx)+xx)*(sin(pA)-sin(pB))**2/sin(xx/2)**2
    dr=flatten/8*(c1-c2)
    distance=ra*(xx+dr)
    return distance

def send_notice(event_name, value1):  # 以下通知IFTTT設定
    key = 'drnDqtzIelml7xzdgqNAlA'
    query_1 = {
        'value1': value1
    }
    url = "https://maker.ifttt.com/trigger/"+event_name+"/with/key/"+key+""
    response = requests.post(url, data=query_1, verify=False)
    print(response.text)

def run():
    r = requests.post('https://irentcar-app.azurefd.net/api/GetProject', json=dataiRent, headers=header, verify=False)
    data = json.loads(r.text)
    isRent = data['Data']['GetProjectObj'][0]['IsRent']
    if ( "Y" == isRent ) :
        print('爽啦，飆車囉')
        stationName = ""
        if ( "X0MW" == stationID ):
            stationName = "大樹藥局"
        elif( "X1IG" == stationID ):
            stationName = "明峰街"
        sent_message = "同站租還" + "\"" + stationName + "\"" + "已有車囉！" + "\n"
        send_notice('notify', sent_message)
        exit()
    else:
        print("已在" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "時間無找到車")
        # 3分鐘後再搜尋一次
        s.enter(10, 0, run)

s.enter(1, 0, run)
s.run()


    
    