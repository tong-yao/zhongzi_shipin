import time, zhongzi_video
from multiprocessing.dummy import Pool


class myThread(object):

    def run(self):
        zhongzi_video.down()
        time.sleep(1)


pool = Pool(2)
t = myThread()
for i in range(2):
    pool.apply_async(t.run)
pool.close()
pool.join()