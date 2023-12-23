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

def now():
    return datetime.datetime.now()

def query_req_total_of(time):
    url = 'http://us.arloor.dev:9099/api/v1/query'  # Replace with your target URL
    form_data = {
        'query': 'sum(increase(req_from_out_total{path="all"}[1d])) by ()',
        'time': time.timestamp(),
    }

    response = requests.post(url, data=form_data)
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
    now=now()
    req_count=query_req_total_of(now)
    # 从环境变量获取 bot_token tg_chat_id 
    bot_token = os.environ.get('bot_token')
    tg_chat_id = os.environ.get('tg_chat_id')
    send_telegram_message(tg_chat_id, f" \n\
    ```Report \n\
    {now.strftime('%m-%d %H:%M')} 报告： \n\
    最近24小时访问量: {req_count} \n\
    ```
    """, bot_token)

