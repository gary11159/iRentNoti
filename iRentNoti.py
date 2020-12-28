from math import *
import requests
import json
import time
import sched
import reserve
s = sched.scheduler(time.time, time.sleep)
requests.packages.urllib3.disable_warnings()

now_lat = 25.046699
now_long = 121.582297
radius = 0.5

dataiRent = {
	"Latitude": now_lat,
	"Longitude": now_long,
	"Radius": radius,
	"ShowALL": 0
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
    r = requests.post('https://irentcar-app.azurefd.net/api/AnyRent', json=dataiRent, headers=header, verify=False)
    data = json.loads(r.text)
    data = data['Data']['AnyRentObj']
    if len(data) > 0 :
        print('有車囉')
        sent_message = "附近" + str(radius) + "公里內有車囉，有以下車號:" + "\n"
        for car in data:
            sent_message += car['CarNo'] + "\n"
        send_notice('notify', sent_message)
        # 自動預約
        reserve.init(data[0]['CarNo'])
    else :
        s.enter(10, 0, run)

# 每10秒定時器
s.enter(10, 0, run)
s.run()

run()

    
    