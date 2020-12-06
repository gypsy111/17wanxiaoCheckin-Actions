import time
import datetime
import json
import logging
import requests

from login import CampusCard


def initLogging():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")


def get_token(username, password):
    user_dict = CampusCard(username, password).user_info
    if not user_dict['login']:
        return None
    return user_dict["sessionId"]


def get_post_json(token, jsons):
    retry = 0
    while retry < 3:
        try:
            res1 = requests.post(url="https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': token}).json()
            res = requests.post(url="https://reportedh5.17wanxiao.com/sass/api/epmpics", json=jsons, timeout=10).json()
        except BaseException:
            retry += 1
            logging.warning('获取完美校园打卡post参数失败，正在重试...')
            time.sleep(1)
            continue
        if res['code'] != '10000':
            return None
        data = json.loads(res['data'])
        # print(data)
        post_dict = {
            "areaStr": data['areaStr'],
            "deptStr": {"deptStr":res1['userInfo']["classId"],"text":res1['userInfo']["classDescription"]},
            "deptid": res1['userInfo']["classId"],
            "customerid": res1['userInfo']['customerId'],
            "userid": res1['userInfo']['userId'],
            "username": res1['userInfo']['username'],
            "stuNo": res1['userInfo']['stuNo'],
            "phonenum": "13711278768",    #该项为本人的联系号码
            "templateid": "orderFood",
            "updatainfo": [{"propertyname":"tm1","value":"36.4"},{"propertyname":"heaithinfo","value":"A.正常，无症状"},{"propertyname":"sshealth","value":"A.健康"},{"propertyname":"todayhealth","value":"B.偶有情绪波动但能自我调节"},{"propertyname":"iseating","value":"否"},{"propertyname":"isoutschool","value":""},{"propertyname":"seject","value":""}],
        }
        logging.info('获取完美校园打卡post参数成功')
        return post_dict
    return None


def healthy_check_in(username, token, post_dict):
    check_json = {"businessType": "epmpics", "method": "submitUpInfo",
                  "jsonData": {"deptStr": post_dict['deptStr'], "areaStr": post_dict['areaStr'],
                               "reportdate": round(time.time() * 1000), "customerid": post_dict['customerid'],
                               "deptid": post_dict['deptid'], "source": "app",
                               "templateid": post_dict['templateid'], "stuNo": post_dict['stuNo'],
                               "username": post_dict['username'], "phonenum": username,
                               "userid": post_dict['userid'], "updatainfo": post_dict['updatainfo'],
                               "gpsType": 0, "token": token},
                  }
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json).json()   #打卡
    except BaseException:
        errmsg = f"```打卡请求出错```"
        logging.warning(errmsg)
        return dict(status=0, errmsg=errmsg)

    # 以json格式打印json字符串
    if res['code'] != '10000':
        logging.warning(res)
        return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type='healthy')
    else:
        logging.info(res)
        return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type='healthy')



def check_in(username, password):
    # 登录获取token用于打卡
    token = get_token(username, password)
    # print(token)
    check_dict_list = []

    if not token:
        errmsg = f"{username[:4]}，获取token失败，打卡失败"
        logging.warning(errmsg)
        return False

    # 获取健康打卡的参数
    json1 = {"businessType": "epmpics",
             "jsonData": {"templateid": "orderFood", "token": token},
             "method": "userComeApp"}
    post_dict = get_post_json(token, json1)
    if not post_dict:
        errmsg = '获取完美校园打卡post参数失败'
        logging.warning(errmsg)
        return False

    # 健康打卡
    healthy_check_dict = healthy_check_in(username, token, post_dict)
    check_dict_list.append(healthy_check_dict)

    return check_dict_list


def server_push(sckey, desp):
    send_url = f"https://sc.ftqq.com/{sckey}.send"
    params = {
        "text": "健康打卡推送通知",
        "desp": desp
    }
    # 发送消息
    res = requests.post(send_url, data=params)
    # {"errno":0,"errmsg":"success","dataset":"done"}
    # logging.info(res.text)
    try:
        if not res.json()['errno']:
            logging.info('Server酱推送服务成功')
        else:
            logging.warning('Server酱推送服务失败')
    except:
        logging.warning("Server酱不起作用了，可能是你的sckey出现了问题")



def run():
    initLogging()
    now_time = datetime.datetime.now()
    bj_time = now_time + datetime.timedelta(hours=8)
    test_day = datetime.datetime.strptime('2020-12-26 00:00:00', '%Y-%m-%d %H:%M:%S')
    date = (test_day - bj_time).days

    username_list = input().split(',')
    password_list = input().split(',')
    sckey = input()
    for username, password in zip([i.strip() for i in username_list if i != ''],
                                  [i.strip() for i in password_list if i != '']):
        check_dict = check_in(username, password)
        if not check_dict:
            return
        else:
                message_content=f"""
{check_dict}

"""
                server_push(sckey,message_content)



if __name__ == '__main__':
    run()
