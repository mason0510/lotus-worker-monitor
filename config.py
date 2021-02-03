
workerConf = {
    'disk':['/'],                #需要监控的路径，可配置多个路径
    'tasks':['PC1','PC2'],  #需要监控的worker进程
    'container':'lotus-worker',  #运行的docker image的名字，仅在isDocker为True的时候有用
    'isDocker':True,            #是否使用docker执行
    'workerBinPath':'/usr/bin/',   #worker的执行目录，不含lotus-worker.必须以/结尾
    'dockerPath':'/usr/bin/',
    'PC1_num':5,              #控制pc1数量，低于数量开始新增质押
    'PreCommit1':5,          #PreCommit1状态块的数量
    'miner_check_time':60,      #多少秒检查一次miner
    'totalSector':1000          #总的封装扇区数量
}