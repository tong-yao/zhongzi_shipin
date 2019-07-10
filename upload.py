# -*- coding: utf-8 -*-

import upyun
import hashlib

# 需要填写自己的服务名，操作员名，密码
service = "qukanba-test"
username = "zhaoyining"
password = "QrNy0WvD9BTfPW3lWIes14vOg4Sg7N12"

# 需要填写上传文件的本地路径和云存储路径，视频
local_file = "9a187c024f998516ab7fac15a53b90c8.mp4"
remote_file = "testsss_video/0c8.mp4"

# 填写要上传的图片
img_file = "1000.jpeg"
re_file = "img/Bran Stark1"

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


# def form_upload():
#     """
#     form文件上传
#     """
#     # kwargs 可选，见form上传参数
#     kwargs = None
#     with open(local_file, 'rb') as f:
#         res = up.put(remote_file, f, checksum=True, form=True)
#         print(res)
