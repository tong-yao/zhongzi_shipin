from zhongzi_settings import user_agent, proxies

import random, base64, requests, json, pymysql, os, hashlib, logging


def headers():
    # 配置请求头
    header = {
        "User-Agent": "{}".format(user_agent()),
    }
    return header


def proxy():
    # 配置代理
    proxies_list = proxies()
    ip_port = random.choice(proxies_list)
    agent = {
        "http": ip_port
    }
    print("目前使用代理为:{}".format(agent))
    return agent


logging.basicConfig(filename="/home/gogs/spider/log/zhongzi_log.txt", filemode="a", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)


def down():
    # 现在连接数据库，方便后期循环写入，否则写入一次连接一次开销好大
    conn = pymysql.connect(host="39.97.241.144",  # ID地址
                           port=3306,  # 端口号
                           user='lianzhuoxinxi',  # 用户名
                           passwd='LIANzhuoxinxi888?',  # 密码
                           db='spider',  # 库名
                           charset='utf8')

    logging.debug("连接数据库")

    # 去请求种子的url
    res = requests.get(
        'https://txservice.imilive.cn/api/feed/tab/show?cc=TG48611&sid=&tubeid=456%2C789&cv=GA3.0.15_Android&imei=&osversion=android_26&count=5&tab_code=small_video',
        headers=headers(),
        timeout=10)
    logging.debug("请求种子url成功")
    # 请求到的数据json化一下
    res_json = json.loads(res.content.decode('UTF-8'))
    # 先把json数据做初步处理
    urls = res_json['data']['videos']

    # 循环URL，对自己需要的再进一步处理
    for i in urls:
        # 获取视频的名称
        title_url = i['video']["title"]
        logging.debug("获取视频名称成功")
        # 获取视频格式
        type = i['video']['play_info']['play_list'][0]['vtype']
        logging.debug("获取视频格式成功")
        # 种子网的url是用base64加密的，解密一下，下载数据
        url = i['video']['play_info']['play_list'][0]['play_url']['main_url']['url']
        logging.debug("获取视频资源成功")
        url = base64.b64decode(url)
        logging.debug("base64解密")
        res = requests.get(url).content
        # 获取上传用户姓名
        Uploader = i['user']['nick']
        logging.debug("获取上传用户姓名成功")
        # 获取上传时间
        birthday = i['user']['birthday']
        logging.debug("获取上传时间成功")
        # 获取海报
        poster = requests.get(i['video']['cover']["middle_cover"]["url"]).content
        logging.debug("获取海报成功")

        # md5加密为后期去重
        md5 = hashlib.md5()
        md5.update(res)
        name = md5.hexdigest()
        print("md5")

        # 这是视频
        with open('/home/video/{name}.{type}'.format(name=name, type=type), 'wb') as f:
        # with open('{name}.{type}'.format(name=name, type=type), 'wb') as f:
            # print(112131231414231423453521412346524353243)
            f.write(res)
            f.close()

        # 这是海报
            with open('/home/video/{}.jpg'.format(name), 'wb') as f:
            # with open('{}.jpg'.format(name), 'wb') as f:
                # print("sgdshrthjdhjiofduydghsfdf,khgjfkhjyg")
                f.write(poster)
                f.close()

        # 写入到mysql写入名字，和路径
            with conn.cursor() as cursor:
                video_path = os.path.abspath("/home/video_zhongzi/{}.{}".format(name,type))
                poster_path = os.path.abspath("/home/video_zhongzi/{}.jpg".format(name))
                # video_path = os.path.abspath("{}.{}".format(name, type))
                # poster_path = os.path.abspath("{}.jpg".format(name))

                print("存入mysql")
                sql = "insert into zhongzi_video(video_name,video_path,Uploader,birthday,json,poster_path) values ('%s','%s','%s','%s','%s','%s')" % (
                    title_url, video_path, Uploader, birthday, pymysql.escape_string(str(i)), poster_path)
                # sql = "insert into video(video_name,video_path,Uploader,birthday,json,poster_path) values ('%s','%s','%s','%s','%s','%s')" % (
                #     title_url, video_path, Uploader, birthday, pymysql.escape_string(str(i)), poster_path)

                cursor.execute(sql)
                logging.debug("存入mysql")
            conn.commit()
        conn.close()
