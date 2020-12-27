from math import *
import requests
import json
import time
import sched
s = sched.scheduler(time.time, time.sleep)
requests.packages.urllib3.disable_warnings()

carNo = "RCR-6907"
orderNo = "H7212876"
tryTime = 0
authorToken = "8BEBA1F1EC009D2F011375E2316C245D9064151F94BF1D6767CCD50108E73185"

reserveCarInfo = {
	"CarNo": carNo,
	"EDate": "",
	"CarType": "PRIUSC",
	"StationID": "",
	"SDate": "",
	"ProjID": "P621",
	"Insurance": 0
}

header = {
    "content_type": "application/json",
    "authorization": "Bearer " + authorToken,
    "deviceid": "FAD0E2D9-E8A0-4281-9863-963EAC3A5E4B",
    "charset": "UTF-8",
    "content-type": "application/json; charset=UTF-8",
    "content-length": "106",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/4.2.2",
    "pragma": "no-cache",
    "cache-control": "no-cache"
}

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
    global orderNo
    global tryTime
    r = requests.post('https://irentcar-app.azurefd.net/api/Booking', json=reserveCarInfo, headers=header, verify=False)
    data = json.loads(r.text)
    if data['ErrorMessage'] == 'Success':
        print('預約成功!')
        send_notice('notify', 'iRent，' + str(carNo) + '預約成功!')
        orderNo = data['Data']['OrderNo']
        # 等待25分鐘後取消預約並重新預約
        time.sleep(1500)
        cancelReserve()
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
            send_notice('notify', 'iRent預約失敗已超過3次，停止自動預約')

# 取消預約
def cancelReserve():
    r = requests.post('https://irentcar-app.azurefd.net/api/BookingCancel', json={"OrderNo": orderNo}, headers=header, verify=False)
    data = json.loads(r.text)
    if data['ErrorMessage'] == 'Success':
        print('取消預約成功!')
        # 3秒過後重新預約
        time.sleep(3)
        reserve()
    else :
        print('取消預約失敗，失敗原因:' + str(data['ErrorMessage']))
        send_notice('notify', 'iRent取消預約失敗，失敗原因: ' + str(carNo) + str(data['ErrorMessage']))

if __name__ == "__main__":
    cancelReserve()

    
    