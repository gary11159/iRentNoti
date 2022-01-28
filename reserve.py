from math import *
import requests
import json
import time
requests.packages.urllib3.disable_warnings()

carNo = ""
orderNo = ""
tryTime = 0

reserveCarInfo = {
	"CarNo": carNo,
	"EDate": "",
	"CarType": "PRIUSC",
	"StationID": "",
	"SDate": "",
	"ProjID": "R321",
	"Insurance": 0
}

header = {
    "content_type": "application/json",
    "authorization": "Bearer ",
    "deviceid": "FAD0E2D9-E8A0-4281-9863-963EAC3A5E4B",
    "charset": "UTF-8",
    "content-type": "application/json; charset=UTF-8",
    "content-length": "106",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/4.2.2",
    "pragma": "no-cache",
    "cache-control": "no-cache"
}

def init(sched_Param, val, token):
    global carNo
    global sched
    sched = sched_Param
    carNo = val
    reserveCarInfo['carNo'] = carNo
    header['authorization'] = "Bearer " + token
    reserve()

def send_notice(event_name, value1):  # 以下通知IFTTT設定
    key = 'drnDqtzIelml7xzdgqNAlA'
    query_1 = {
        'value1': value1
    }
    url = "https://maker.ifttt.com/trigger/"+event_name+"/with/key/"+key+""
    response = requests.post(url, data=query_1, verify=False)
    print(response.text)

# 預約
def reserve():
    if sched.get_job('autoReserve') != None:
        sched.remove_job('autoReserve')
    global orderNo
    global tryTime
    r = requests.post('https://irentcar-app.azurefd.net/api/Booking', json=reserveCarInfo, headers=header, verify=False)
    data = json.loads(r.text)
    print('預約Token', header['authorization'])
    if data['ErrorMessage'] == 'Success':
        print('預約成功!')
        send_notice('notify', 'iRent，' + str(carNo) + '預約成功!')
        orderNo = data['Data']['OrderNo']
        # 等待25分鐘後取消預約並重新預約
        sched.add_job(cancelReserve, 'interval', seconds=1500, id='cancelReserve')
    else :
        print('預約失敗，失敗原因:' + str(data['ErrorMessage']))
        if tryTime == 0 :
            send_notice('notify', 'iRent預約失敗，失敗原因: ' + str(carNo) + str(data['ErrorMessage']))
        # 五秒後重新嘗試預約
        time.sleep(5)
        tryTime += 1
        if tryTime < 3 :
            reserve()
        else :
            print('iRent預約失敗已超過3次，停止自動預約')
            print(header, reserveCarInfo)
            send_notice('notify', 'iRent預約失敗已超過3次，停止自動預約')
            sched.shutdown(wait=False)

# 取消預約
def cancelReserve():
    if sched.get_job('cancelReserve') != None:
        sched.remove_job('cancelReserve')
    r = requests.post('https://irentcar-app.azurefd.net/api/BookingCancel', json={"OrderNo": orderNo}, headers=header, verify=False)
    data = json.loads(r.text)
    if data['ErrorMessage'] == 'Success':
        print('取消預約成功!')
        # 3秒過後重新預約
        sched.add_job(reserve, 'interval', seconds=3, id='autoReserve')
    else :
        print('取消預約失敗，失敗原因:' + str(data['ErrorMessage']))
        send_notice('notify', 'iRent取消預約失敗，失敗原因: ' + str(carNo) + str(data['ErrorMessage']))
        sched.shutdown(wait=False)




    
    