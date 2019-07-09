import zhongzi_video
from multiprocessing.dummy import Pool


class myThread(object):

    def run(self):
        print("开始函数")
        zhongzi_video.down()


pool = Pool(1)
t = myThread()
for i in range(1):
    pool.apply_async(t.run)
pool.close()
pool.join()
