#encoding=utf-8

import urllib,urllib2
from monitor import Monitor
from resultHandler import xmlHandler
if __name__ == '__main__':
    # 演示结果处理器可以配置
    class Handler:
        pass
    rh = Handler()
    rh.hl = xmlHandler()
    setattr(rh,'handle',lambda x:rh.hl.handle(x))
    #raise Exception,"just test"
    Monitor(result_handler=rh).run()

