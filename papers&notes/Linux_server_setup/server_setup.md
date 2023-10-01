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

