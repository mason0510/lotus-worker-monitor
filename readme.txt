lotus-miner&&worker 守护脚本
脚本作用：
1、自动质押，根据当前进行的任务数量来决定是否质押
2、监控消息池，有卡住的消息自动发送
3、监控worker机器的磁盘，磁盘空间不足自动停止PC1、PC2 或者C2。磁盘空闲后再自动打开任务。

支持docker环境和原生环境，使用方法
需要安装python3，pip3
改下国内源
pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip3 install psutil
pip3 install pexpect
安装screen
apt install screen

1、编辑config.py，配置miner路径，使用docker的配置docker路径。其余按说明配置
2、新建screen 窗口
如果是miner机器上，使用
python3 run.py miner

如果是worker机器上，使用
python3 run.py worker




