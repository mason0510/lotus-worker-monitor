import psutil
import pexpect
import re
import json
import time

from config import workerConf
class worker:
    _pc2_space = 500         #PC2需要的空间，单位GiB
    _pc1_space = 500         #PC1需要的空间，单位GiB
    _c2_space = 32          #C2需要的空间，单位GiB

    #检查空间并关闭对应任务
    def checkDisk(self):
        if not isinstance(workerConf['disk'],list):
            print("路径设置错误，必须为List型")
            return
        enoughForP1 = False
        enoughForP2 = False
        enoughForC2 = False
        for d in workerConf['disk']:
            space = psutil.disk_usage(d)
            gb = round(space.free / 1024 /1024 /1024)
            if gb > self._pc2_space:
                enoughForP2 = True
            if gb > self._pc1_space:
                enoughForP1 = True
            if gb > self._c2_space:
                enoughForC2 = True

        #检查p2任务
        if enoughForP2 == False:
             if self.checkTasking('PC2') and 'PC2' in workerConf['tasks']:
                 print('没有足够空间执行PC2，关闭PC2!')
                 self.run("lotus-worker tasks disable PC2")
        else:
             if (not self.checkTasking('PC2')) and 'PC2' in workerConf['tasks']:
                 print('有足够空间重启任务PC2!')
                 self.run("lotus-worker tasks enable PC2")
        # 检查p1任务
        if enoughForP1 == False:
            if 'PC1' in workerConf['tasks'] and self.checkTasking('PC1'):
                print('没有足够空间执行PC1，关闭PC1!')
                self.run("lotus-worker tasks disable PC1")
        else:
            if 'PC1' in workerConf['tasks'] and (not self.checkTasking('PC1')):
                 print('有足够空间重启任务PC1!')
                 self.run("lotus-worker tasks enable PC1")
        # 检查C2任务
        if enoughForC2 == False:
            if self.checkTasking('C2') and 'C2' in workerConf['tasks']:
                print('没有足够空间执行C2，关闭C2!')
                self.run("lotus-worker tasks disable C2")
        else:
            if (not self.checkTasking('C2')) and 'C2' in workerConf['tasks']:
                 print('有足够空间重启任务C2!')
                 self.run("lotus-worker tasks enable C2")
        if enoughForP1 == True and enoughForP1 ==True and enoughForC2 ==True:
            print('磁盘空间充足，继续监控')

    #检查运行中有没有某个任务
    def checkTasking(self,task):
        output = self.exec('lotus-worker info')
        if len(output) == 0: return False
        s = re.search('\s+' + task, output)
        if not s == None:
            return True
        return False

    #执行命令取得返回值
    def exec(self,cmd):
        output = ''
        try:
            if workerConf['isDocker']:
                p = pexpect.spawn(workerConf['dockerPath'] + 'docker exec -it ' + workerConf[
                    'container'] + ' /bin/bash -c "'+ cmd +'"',timeout=60)
                #print(workerConf['dockerPath'] + 'docker exec -it ' + workerConf[
                 #   'container'] + ' /bin/bash -c "'+ cmd +'"')
                output = p.read()
            else:
                p = pexpect.spawn('/bin/bash -c "' + workerConf['workerBinPath'] + cmd +'"',timeout=60)
                output = p.read()

        except pexpect.exceptions.ExceptionPexpect as err:
            print(err)

        return output.decode('utf-8')

    #执行命令
    def run(self,cmd):
        try:
            if workerConf['isDocker']:
                p = pexpect.spawn(workerConf['dockerPath'] + 'docker exec -it '+ workerConf['container'] +' /bin/bash -c "'+ cmd +'"' )
                p.expect(pexpect.EOF,timeout=None)
            else:
                p = pexpect.spawn(workerConf['workerBinPath']+cmd)
                p.expect(pexpect.EOF,timeout=None)
        except pexpect.exceptions.ExceptionPexpect as err:
            print(err)

    #关闭任务
    def closeTask(self,task):
        if task == 'PC2':
            self.run("lotus-worker tasks disable PC2")
            print('已关闭PC2。')
        elif task == 'PC1':
            self.run("lotus-worker tasks disable PC1")
            print('已关闭PC1。')
        elif task == 'C2':
            self.run("lotus-worker tasks disable C2")
            print('已关闭C2。')

    #获取某个进程数量
    def getProcessNum(self,task):
        if task == 'AP': task = 'AP '
        output = self.exec('lotus-miner sealing jobs | grep \''+ task +'   running\' |wc -l')
        if len(output) == 0 : return 0
        s =  int(output)
        return s
    #获取某个任务扇区的数量
    def getSectorNum(self,sector):
        output = self.exec('lotus-miner sectors list --states PreCommit1 |grep '+ sector +' | wc -l')
        if len(output) == 0 : return 0
        s =  int(output)
        return s

    #质押封装
    def pledge(self):
        print('开始随机质押封装...')
        self.run('lotus-miner sectors pledge')

    #检查消息池
    def checkMessagePool(self):
        message = self.exec('lotus mpool pending --local')
        if not len(message) == 0:
            message = message.replace('\r\n','')
            data = []
            new_data_list = re.split('}{', message[1:-1])
            for i in new_data_list:
                ii = '{' + i + '}'
                a = json.loads(ii)
                data.append(a)
            return data
        else:
           return None

    #处理消息
    def processMessage(self,data):
        if data == None: return False
        for d in data:
            GasPremium = int(d['Message']['GasPremium'])
            GasPremium = (round(int(GasPremium) * 1.25) +1)
            s = self.exec('lotus mpool replace --gas-feecap 10000000000 --gas-premium '+ str(GasPremium) +' --gas-limit '+ str(d['Message']['GasLimit']) +' '+d['Message']['From']+' '+str(d['Message']['Nonce'])+'')
            print(s)
    #检查磁盘守护进程
    def checkDiskDamon(self):
        while 1:
            self.checkDisk()
            time.sleep(10)

    #miner任务守护进程
    def minerDamon(self):
        while 1:
            i = 0
            p1 = self.getProcessNum('PC1')
            ap = self.getProcessNum('AP')
            sectors = self.getSectorNum('PreCommit1')
            if p1 +ap < workerConf['PC1_num'] and sectors < workerConf['PreCommit1']:
                self.pledge()
                i = i+1
                print('已经质押了' + str(i) + '个封装任务')
            else:
                print('当前有PreCommit1状态扇区'+ str(sectors)+'个。')
                print('当前有'+str(p1)+'个PC1任务，'+str(ap)+'个AP任务。无需新增任务。')
            if i >= workerConf['totalSector']:
                print('完成全部质押任务')
                return

            print('等待'+ str(workerConf['miner_check_time']) +'秒,进行下次检查')
            print('正在检查消息是否堵塞。')
            data = self.checkMessagePool()
            self.processMessage(data)
            time.sleep(workerConf['miner_check_time'])


