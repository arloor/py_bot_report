#! /usr/bin/python3
import subprocess
import json
import requests
import datetime
import time
import os

def send_telegram_message(tg_chat_id, text,bot_token):
    body = {"chat_id": tg_chat_id, "text": text, "parse_mode": "MarkdownV2"}
    cmd = f'curl -sSL -X POST -H "Content-Type: application/json" -d \'{json.dumps(body)}\' https://api.telegram.org/bot{bot_token}/sendMessage'
    
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = pipe.stderr.read().decode()
    
    if len(err) != 0:
        print(err)
        return False
    
    res = pipe.stdout.read().decode()
    rjson = json.loads(res)
    isOk = bool(rjson.get('ok'))
    
    if not isOk:
        print(rjson.get('description'))
    else:
        print(rjson.get('result'))
    return isOk

def query_req_total_of(time,prom_add,auth_header):
    url = f'{prom_addr}/api/v1/query'  # Replace with your target URL
    form_data = {
        'query': 'sum(increase(req_from_out_total{path="all"}[1d])) by ()',
        'time': time,
    }

    response = requests.post(url, data=form_data,headers={'Authorization':auth_header})
    print(response.status_code)
    print(response.text)
    res=json.loads(response.text)
    if res.get('status') == 'success':
        if res.get('data').get('resultType')=='vector':
            result=res.get('data').get('result')
            if len(result)>0:
                value=result[0].get('value')
                if len(value)==2:
                    value=int(float(value[1]))
                    return value
            else:
                warnning='数据为空'
                print(warnning)
        else:
            warnning='数据类型不是vector'
            print(warnning)
    return None


if __name__ == "__main__":
    # 从环境变量获取
    bot_token = os.environ.get('bot_token')
    tg_chat_id = os.environ.get('tg_chat_id')
    prom_addr = os.environ.get('prom_addr')
    auth_header=os.environ.get('auth_header')

    today_0h=datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    timestamp=today_0h.timestamp()
    print(today_0h,timestamp)
    req_count=query_req_total_of(timestamp,prom_addr,auth_header)

    send_telegram_message(tg_chat_id, f"```Report\n\
{today_0h.strftime('%m-%d %H:%M')}\n\
最近24小时访问量: {req_count}\n\
```", bot_token)

