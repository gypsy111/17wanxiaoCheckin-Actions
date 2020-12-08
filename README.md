# 🌈17wanxiaoCheckin-Actions of huanyuan
适用于广东环境保护工程职业技术学院的完美校园自动打卡

 
欢迎大家 fork 测试使用，如果可用的话。

感谢 [@zhongbr](https://github.com/zhongbr) 的完美校园逆向登录分析代码的分享：[完美校园模拟登录](https://github.com/zhongbr/wanmei_campus)

抓包部署教程请前往：[完美校园抓包打卡](https://github.com/ReaJason/17wanxiaoCheckin-Actions/blob/master/README_LAST.md)

非常感谢[@ReaJason](https://github.com/ReaJason/17wanxiaoCheckin-Actions)的分享，膜拜!!!!

通过修改[@ReaJason](https://github.com/ReaJason/17wanxiaoCheckin-Actions)的项目，实现了环院的完美校园签到。

**消息推送做的很拉跨，欢迎各位大佬来做美化

以下是原项目的食用教程。
## Q&A

**1、fork之后，修改README.md并没有触发actions**？

请进入 Actions，Enable workflow

![enable](https://cdn.jsdelivr.net/gh/LingSiKi/images/img/enable.png)



**1、修改部分代码 环院与大佬的学校数据请求不一致**

原代码，
```def get_post_json(token, jsons):
    retry = 0
    while retry < 3:
        try:
            # 如果不请求一下这个地址，token就会失效
            requests.post("https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': token})
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
            "deptStr": data['deptStr'],
            "deptid": 208119,    #data['deptStr']['deptid'],
            "customerid": data['customerid'],
            "userid": data['userid'],
            "username": data['username'],
            "stuNo": data['stuNo'],
            "phonenum": data['phonenum'],
            "templateid": data['templateid'],
            "updatainfo": [{"propertyname": i["propertyname"], "value": i["value"]} for i in
                           data['cusTemplateRelations']],
            "checkbox": [{"description": i["decription"], "value": i["value"]} for i in
                         data['cusTemplateRelations']],
        }
        # print(json.dumps(post_dict, sort_keys=True, indent=4, ensure_ascii=False))
        # 在此处修改字段
        logging.info('获取完美校园打卡post参数成功')
        return post_dict
    return None 
 ```
 
 修改后
 ```
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
 ```



**2、自动运行的时间该怎么修改**

进入.github/workflows/run.yml修改时间

```python
"""
这里的cron就是脚本运行时间，22,4,9对应的时间是UTC时，对应北京时间早上六点，中午十二点，下午五点
详细对应关系请查看：http://timebie.com/cn/universalbeijing.php

只有健康打卡的小伙伴可以只留着22就可以了，这样其余两个时间就不会打卡
"""
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  schedule:
    - cron: 0 22,4,9 * * *
```





#### 一、功能介绍

1. 完美校园模拟登录获取 token
2. 自动获取上次提交的打卡数据
3. 微信推送打卡消息(推送做得很拉跨)



#### 二、打卡数据

细心的你应该会发现，自从第一次打卡之后，每次进去信息基本自动填写好了，我抓取的就是这个接口，

这样子也相当于大家不用抓包了，如果你进入完美校园健康打卡界面，它没有自动填写信息，可能

本项目也就不起作用了，可以试试打一次卡然后再进入看有无自动填充信息。

```res1 = requests.post(url="https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': token}).json()
#这里请求的是其中的打卡地址
res = requests.post(url="https://reportedh5.17wanxiao.com/sass/api/epmpics", json=jsons, timeout=10).json()#其中jsons的数据也修改了
#这里请求的是部分数据，没有的自行不全，其中"updatainfo"的数据响应的数据量太大，所以直接填上去算了
```


以下是原项目得食用方法

#### 三、使用方法

1. 请先确保进入健康打卡界面，信息能够正确的自动填写（没有自动填写的项，可以自行修改代码）

2. 点击右上角的 `fork`，`fork` 本项目到自己仓库中
    
   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/click_fork.png)

   

3. 开启 `Actions`

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/start_action.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_actions.png)

   

4. 设置三个 `secrets`  字段：`USERNAME`、`PASSWORD`、`SCKEY`（对应就是账号，密码以及 Server 酱）

   1. 如果是多人打卡的话：
      - USERNAME字段：手机号1,手机号2,......（与下面密码对应），例如：`1737782***,13602***`
      - PASSWORD字段：密码1,密码2,......  （与上面账号对应），例如：`123456,456789`
      - SCKEY字段：填写一个即可，例如：`SCU90543*******`

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/new_secrets.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/secrets_details.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_secrets.png)

   

5. 修改 `README.md` 测试一次

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/modify_readme.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_modify.png)

   

6. 查看 `Actions` 运行情况，以及微信推送情况，至此每日六点多将会自行打卡

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/check_status.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_check.png)



