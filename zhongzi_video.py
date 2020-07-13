from zhongzi_settings import user_agent, proxies
import bloom_filter
import upyun
import hashlib
# aaaaaaaaaaaaaaa
import random, base64, requests, json, pymysql, os, hashlib, logging, ffmpeg


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
    logging.debug("目前使用代理为:{}".format(agent))
    return agent


logging.basicConfig(filename="/home/gogs/spider/log/zhongzi_log.txt", filemode="a",
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)

# 需要填写自己的服务名，操作员名，密码
service = "qukanba-test"
username = "zhaoyining"
password = "QrNy0WvD9BTfPW3lWIes14vOg4Sg7N12"

# logging.basicConfig(filename="zhongzi_log.txt", filemode="a",
#                     format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S",
#                     level=logging.DEBUG)


def down():
    print("连接数据库")
    # 现在连接数据库，方便后期循环写入，否则写入一次连接一次开销好大
    conn = pymysql.connect(host="39.97.241.144",  # ID地址
                           port=3306,  # 端口号
                           user='lianzhuoxinxi',  # 用户名
                           passwd='LIANzhuoxinxi888?',  # 密码
                           db='spider',  # 库名
                           charset='utf8')

    logging.debug("连接数据库")

    # 去请求种子的url
    print("请求种子")
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
        url = i['video']['play_info']['play_list'][0]['play_url']['main_url']['url']
        logging.debug("获取视频资源成功")
        # 种子网的url是用base64加密的，解密一下，下载数据
        url = base64.b64decode(url)
        logging.debug("base64解密")
        print("去布隆函数")
        url = str(url, encoding="utf-8")
        if bloom_filter.func1(url=url):
            # 获取视频
            res = requests.get(url).content
            # 获取视频的名称
            title_url = i['video']["title"]
            logging.debug("获取视频名称成功")
            # 获取视频格式
            typ = i['video']['play_info']['play_list'][0]['vtype']
            logging.debug("获取视频格式成功")
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
            with open('{name}.{typ}'.format(name=name, typ=typ), 'wb') as f:
                print("写入视频")
                f.write(res)
            # 需要填写上传文件的本地路径和云存储路径，视频
            local_file = "{name}.{typ}".format(name=name, typ=typ)
            remote_file = "testsss_video/{name}.{typ}".format(name=name, typ=typ)

            # 这是海报
            with open('{}.jpg'.format(name), 'wb') as f:
                print("写入海报")
                f.write(poster)
            # 填写要上传的图片
            img_file = "{}.jpg".format(name)
            re_file = "img/{}.jpg".format(name)

            up = upyun.UpYun(service, username=username, password=password)

            def rest_upload():
                """
                rest文件上传
                """
                with open(img_file, "rb") as f:
                    # headers 可选，见rest上传参数
                    headers = None
                    up.put(re_file, f, headers=headers)

            rest_upload()
            print("图片上传成功")

            def rest_resume_upload():
                """
                文件断点续传
                """
                with open(local_file, "rb") as f:
                    # headers 可选，见rest上传参数
                    headers = None
                    res = up.put(remote_file, f, checksum=True,
                                 need_resume=True, headers=headers)
                    print(res)

            rest_resume_upload()
            print("视频上传成功")

            # 写入到mysql写入名字，和路径
            with conn.cursor() as cursor:
                video_path = "/testsss_video/{name}.{typ}".format(name=name, typ=typ)
                poster_path = "/img/{}.jpg".format(name)

                print("存入mysql")
                dura = ffmpeg.probe('{name}.{typ}'.format(name=name, typ=typ))
                # print(dura)
                print(type(dura))
                dura_str = dura.get("format").get("duration")
                video_size = dura.get("format").get("size")
                print(type(dura_str))
                print(dura_str)
                dura_int = float(dura_str)
                print(type(dura_int))
                if dura_int > 60:
                    print("大于60")
                    sql = "insert into zhongzi_video(video_name,video_path,Uploader,birthday,json,poster_path,duration,video_size) values ('%s','%s','%s','%s','%s','%s','%s')" % (
                        title_url, video_path, Uploader, birthday, pymysql.escape_string(str(i)), poster_path, 0,video_size)
                else:
                    print("小于60")    
                    sql = "insert into zhongzi_video(video_name,video_path,Uploader,birthday,json,poster_path,duration,video_size) values ('%s','%s','%s','%s','%s','%s','%s')" % (
                        title_url, video_path, Uploader, birthday, pymysql.escape_string(str(i)), poster_path, 1,video_size)
                cursor.execute(sql)
                logging.debug("存入mysql")
                print("存入sql成功")
                conn.commit()
            os.remove('{name}.{typ}'.format(name=name, typ=typ))
            os.remove("{}.jpg".format(name))
        else:
            print("url已存在")
            logging.debug("url已存在")
            continue

    conn.close()
