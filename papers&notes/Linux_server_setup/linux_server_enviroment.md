# R730XD 配置多用户Anaconda以及配置pytorch环境
没想到我上一篇R730XD的文章竟然获得了7000+的阅读量，属于是不适合做量化了。因为我经常搞硬盘添加弄坏我的系统环境，导致我多次重装系统，另外我之前找到的一些博客帖子对于环境配置确实有很多可取之处。所以我希望重新整理一篇帖子系统安装指令，也方便我以后瞎搞的时候[重装系统](https://blog.csdn.net/yykzyj123456/article/details/123681883)。

以下所有操作默认使用root用户操作，先更新一下系统
```shell
sudo apt-get update
sudo apt-get upgrade
```
另外ubuntu默认不启用root + ssh不能使用root用户登录，为了方便我设置环境所以打开
```shell
sudo passwd root
sudo vim /etc/ssh/sshd_config
```
找到并用#注释掉这行：（如果没有就不用注释）

PermitRootLogin prohibit-password

查看是否有PermitRootLogin yes,如果没有，新建一行 添加：PermitRootLogin yes

重启ssh
```shell
/etc/init.d/ssh restart
systemctl restart ssh
```

## 为多用户安装Anaconda环境以及使用方法
参考[帖子](https://yangyq.net/2023/03/anaconda-install-and-use.html)，本无意抄袭，但是看到这篇文章挂在作者的个人网站下，所以复制到这边以防域名失效。

### 下载安装
访问[官网](https://www.anaconda.com/download#downloads)查看下载链接，或者[历史版本]( https://repo.anaconda.com/archive/)
```shell
wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
```
输入以下指令安装，注意，安装路径不要直接回车，输入：/opt/anaconda3
```shell
bash Anaconda3-2023.09-0-Linux-x86_64.sh
```

### 为多用户进行配置
为了让所有用户都能找到相关命令，需要更改全局环境变量：
```shell
vim /etc/profile
```
在最下面加入：
```shell
export PATH=/opt/anaconda3/bin:$PATH
```
保存退出后执行
```shell
source /etc/profile
```

操作多用户权限：
```shell
groupadd conda_usr
```
将需要的用户加入该组，注意，如果是新增一个用户，则执行（记得替换username为你想要的名字）：
```shell
# centos
useradd username -g conda_usr
```
如果是已有用户，则执行（记得替换username为你想要的名字）：
```shell
sudo adduser username
usermod -a -G conda_usr username
```


将安装目录转给该组
```shell
chgrp -R conda_usr /opt/anaconda3
```
设置 root 用户与 conda_usr 组的读写权限。root是目录所有者，conda_usr是组所有者。
```shell
chmod 770 -R /opt/anaconda3
```
设置组继承，使以后新建的文件夹仍属于 conda_usr 组
```shell
find /opt/anaconda3 -type d -exec chmod g+s {} +
```
设置共享环境只能由 root 修改，其他用户的环境，放在每个用户自己的home目录下。
```shell
chmod g-w /opt/anaconda3/envs
```
配置conda：
```shell
vim /opt/anaconda3/.condarc
```
在文件中输入：
```shell
envs_dirs:
  - /opt/anaconda3/envs
  - ~/.conda/envs
```
这样，root创建的虚拟环境，就在/opt/anaconda3/envs中，而其他用户因为没有该文件夹的读写权限，就放在自己的home目录.conda/envs下。


### 新用户使用conda的方式

其他用户登陆并且使用下面的指令初始化conda后，应该可以直接使用conda命令了。
```shell
conda init bash
```

## 安装git2（ubuntu以及centos7）

### ubuntu
使用`apt-get`命令安装Git。对于Ubuntu 18.04及其后续版本，可以使用以下命令：

```shell
sudo apt install git
```
验证Git安装：安装完成后，可以通过在终端输入`git --version`命令来检查Git是否已经成功安装。如果输出了Git的版本信息，表明安装成功。


### centos7
centos7默认的git版本是1.8.x，太老土了，需要第三方的库安装git2

使用[第三方仓库](https://ius.io/setup)安装
```shell
yum install \
https://repo.ius.io/ius-release-el7.rpm \
https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
```
若是出现“不更新已安装的软件包”，需要卸载之前的源再进行安装
```shell
yum remove epel-release.noarch
yum remove ius-release.noarch
```

搜索git，这一步是为了搜索该第三方库能够支持的git版本
```shell
yum search git
```

选择上一步展示的最高版本进行安装并验证
```shell
yum -y install git224
git version
```

## 安装显卡驱动以及配置pytorch环境


### 安装英伟达显卡驱动

#### 禁止开源驱动，阻止 nouveau 模块的加载
```shell
vi /etc/modprobe.d/blacklist.conf
添加:
blacklist nouveau
options nouveau modeset=0
```
通过如下命令更新系统，使刚刚修改的文件生效：
```shell
sudo update-initramfs -u
reboot
```
验证nouveau是否已禁用：
```shell
lsmod | grep nouveau
```
命令行输出为空,说明nouveau显卡驱动已被禁用，此时可以安装nvidia显卡驱动。

#### 安装nvidia显卡驱动

从英伟达[官网](https://www.nvidia.com/download/index.aspx)下载对应的显卡驱动
```shell
wget https://us.download.nvidia.com/XFree86/Linux-x86_64/535.154.05/NVIDIA-Linux-x86_64-535.154.05.run

sudo apt-get install gcc make
chmod +x NVIDIA-Linux-x86_64-535.154.05.run
sudo ./NVIDIA-Linux-x86_64-535.154.05.run
```

使用 nvidia-smi 查看是否安装成功


### 安装cuda
这里选在安装12.1版本
```shell
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run
```

安装需要比较久的时间，安装结束后请把提醒的路径加入到环境中
```shell
export PATH=$PATH:/usr/local/cuda-12.1/bin

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.1/lib64

source ~/.bashrc
```

检查是否安装成功
```shell
nvcc -V
```


### 安装 cuDNN
访问英伟达[官网](https://developer.nvidia.com/cudnn)
```shell
wget https://developer.download.nvidia.com/compute/cudnn/9.0.0/local_installers/cudnn-local-repo-ubuntu2204-9.0.0_1.0-1_amd64.deb
sudo dpkg -i cudnn-local-repo-ubuntu2204-9.0.0_1.0-1_amd64.deb
sudo cp /var/cudnn-local-repo-ubuntu2204-9.0.0/cudnn-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cudnn
```







