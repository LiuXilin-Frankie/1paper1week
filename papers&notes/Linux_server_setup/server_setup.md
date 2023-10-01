# R730XD 年轻人的第一台服务器

起初是手里闲置了一张 ‘Msi ventus 3070 2x’，希望搞一台服务器放在家里，顺便学习学习linux系统，炼炼丹，所以搞出这样一台机器。不过在配置这台机器的过程中发生了太多意外，无所谓了，生命在于折腾。如果你也想要一台linux服务器做炼丹服务器的话，或许你可以follow这篇文章。配置如下：

![list](/docs/r730_list.png)

最后部分商品没有跟着上面的配置单来，但配置单总体没有大问题，我也懒得修改了。

## 系统安装

我有2张480G的sas ssd，装在背板上面的2.5寸盘位组raid1安装系统。另外一张18T的希捷HDD放在前置的3.5寸盘位用来寸数据。一开始安装系统之后发现了蛮多问题，比如1.两张盘放在raid卡下boot设置读不到盘。2.装了系统后我的系统识别不到18T的数据盘等等。在反复地重装系统之后，我选择follow这篇文章[知乎](https://zhuanlan.zhihu.com/p/604893199?utm_id=0)

如果需要添加新的硬盘的话参考[blog](https://blog.csdn.net/weixin_67287151/article/details/128006939)

## 配置frp

### frp 原理
介绍frp细节可以参考这篇[博客](https://cloud.tencent.com/developer/article/1631703)。

简单地来说，为了保证用户无论在香港还是北极都能访问，我购买了一个云服务器做转发（就是下图中间的服务器）。用户的ssh请求会先通过`云服务器 -p 6000`再发送到您将要使用的`深度学习服务器`。也就是说，只有您的访问请求是访问 `-p 6000 ipv4address` 是访问`深度学习服务器`的，不带端口号的访问请求一律视为只访问腾讯云服务器。

![frp](/docs/frp.png)

### frp配置

frp 下载地址
https://github.com/fatedier/frp/releases

首先下载对应的frp文件，并修改文件中对应的ip，将frpc开头的文件放在本地服务器中，frps开头的文件放在用于转发的云服务器中。

配置命令如下：
#### frps：
```shell
1.后台运行frp：
nohup ./frps -c frps.ini &

2.开机自启动：
sudo mkdir -p /etc/frp
sudo cp frps.ini /etc/frp
sudo cp frps /usr/bin
sudo cp systemd/frps.service /usr/lib/systemd/system/
sudo systemctl enable frps
sudo systemctl start frps
```

#### frpc：
```shell
1.后台运行frp：
nohup ./frpc -c frpc.ini &

2.开机自启动：
sudo mkdir -p /etc/frp
sudo cp frpc.ini /etc/frp
sudo cp frpc /usr/bin
sudo cp systemd/frpc.service /usr/lib/systemd/system/
sudo systemctl enable frpc
sudo systemctl start frpc
```

这样就可以通过 ssh usrname@ip -p xx.xx.xx.xx 访问


## pytorch 环境配置

### 配置anaconda

参考[配置anaconda](https://yangyq.net/2023/03/anaconda-install-and-use.html)

每个用户的环境自己的home目录.conda/envs下。默认更换了清华大学的镜像源。该设置的结果可以保护每个用户创建的env不能被其它用户访问且修改。root用户创建的env所有用户都可运行但不可修改。


### 配置git
centos7 支持的库仅仅更新到git 1.8，无法安装最新的git2.

常见的 `make && make install` 的方法频繁报错，所以采用第三方插件库的方式安装。[安装博客](https://blog.csdn.net/qq_32811865/article/details/123397297)


### 安装显卡驱动
这里参考朋友chenken的文件

准备工作：
```shell
yum update
yum -y install wget
yum -y install gcc kernel-devel kernel-headers
```

禁止开源驱动，阻止 nouveau 模块的加载.
```
vi /usr/lib/modprobe.d/dist-blacklist.conf

添加blacklist nouveau 
注释blacklist nvidiafb
```

重新建立initramfs image文件(生成新的内核，这个内核在开机的时候不会加载 nouveau驱动程序)
```shell
mv /boot/initramfs-$(uname -r).img /boot/initramfs-$(uname -r).img.bak
dracut /boot/initramfs-$(uname -r).img $(uname -r)
reboot
```

驱动下载以及安装

从 https://www.nvidia.cn/Download/index.aspx?lang=cn 选择合适的显卡型号，下载对应的文件.
此处使用的是4060TI
```shell
init 3
# 进入文件所在文件夹
chmod +x NVIDIA-Linux-x86_64-340.65.run 
./NVIDIA-Linux-x86_64-460.91.03.run
```
安装完成后运行 nvidia-smi 查看是否安装成功。


### CUDA Toolkit
在[这里](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=CentOS&target_version=7&target_type=runfile_local)选择合适配置进行安装。Architecture选择x86_64，Installer Type选择runfile。根据提示输入网
⻚上生成的代码下载

`注意`：上面链接只给了最新版本的cuda下载，具体下载cuda版本请参考pytorch 官网，我选择的是12.1。可以在链接中 https://developer.nvidia.com/cuda-12-1-0-download-archive 修改相关的部分寻找。

```shell
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run
```

修改环境变量(这里的内容请参考安装完成后输出的提示，或者更改您的版本号)
```shell
export PATH=$PATH:/usr/local/cuda-12.1/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.1/lib64:/usr/lib/x86_64-linux-gnu
```

使改动生效
```
source ~/.bashrc
```

查看版本号，有输出意味着安装成功
```nvcc -V```

### cuDNN
在[英伟达官网](https://developer.nvidia.com/rdp/cudnn-download)注册成为开发者会员并下载对应版本cudnn安装包，并scp到服务器。下载的是 Tar 文件。

参考[官方安装指南](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html#installlinux-tar)


### 安装pytorch
这里选择在root用户啊下创建环境
```shell
conda create -n pytorch_GPU python=3.11
conda activate pytorch_GPU
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
conda install numpy pandas matplotlib jupyter
```
![pytorch-env](/docs/pytorch-env.png)