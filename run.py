import psutil
import sys
from worker import worker


def main(argv):
    if argv == None:
        print('请输入参数，1、miner：启动miner质押和监控守护进程；2、worker：启动worker监控守护进程')
        return
    w = worker()
    #启动worker守护进程
    if argv[1] == 'worker':
        print('启动lotus-worker监控进程！')
        w.checkDiskDamon()
    #启动miner守护进程
    if argv[1] == 'miner':
        print('启动miner监控进程！')
        w.minerDamon()


if __name__ == "__main__":
    main(sys.argv)