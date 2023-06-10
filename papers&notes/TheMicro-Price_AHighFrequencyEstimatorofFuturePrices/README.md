![1paper1week](../../docs/1paper1week-git.jpg)

# stoikov_micro-price

该篇的目的是研究如何得到更好的 fair price，是我看到这篇[知乎文章](https://zhuanlan.zhihu.com/p/622226738)后决定一读原文。以我学生时随机过程弱鸡的成绩，该文章是注定一知半解的，但还是那句话“better late than never”。斗胆帮大家做一下翻译器。

## Abstract
1. 作者定义了micro-price，用于更好的替代mid-price（作为资产的fair-price）。
2. 作者认为真正的fair-price应该是一个martingale。
3. 使用的信息就是LOB数据，考虑到了spread以及orderbook imbalance数据。
4. 作者之后实证指出了为什么自己的micro-price更好。

## Introduction
HFT是一个很宽松的定义，在各种不相关的情况下被滥用。作者认为的HFT有以下几个共同特点:1.需要compute technology(硬件或者软件)；2.允许Agents以人类无法反应过来的速度进行交易。插一句，最近写高频交易公司的笔试题，该公司把 minute level rebalance 叫做 mid/long term，让我甚是震撼。

### mid-price
对于高频中甚是常用的orderbook数据来说，最经典的是 mid-price，定义如下：
$$
M = \frac{1}{2}(P^a + P^b)
$$
但是mid-price有以下几个缺点：
1. changes are highly auto-correlated，其中一个原因可能是 bid-ask bounce（不太理解，原文给了相关引用）。
2. 相比于LOB数据来说，他的更新频率可能较低。比如说bid1/ask1的价格不变，但是数量发生了变化，mid-price不会做出任何的改变。
3. 没有使用LOB中的volume信息。

### weighted mid-price
作者认为LOB数据中的bid1/ask1的数量隐藏着强有力的信息，不应该被忽略。同时进一步介绍了另外一个概念，weighted mid-price：
$$
W = IP^a + (1-I)P^b
$$
where:
$$
I = \frac{Q^b}{Q^b + Q^a}
$$
但同样有着以下缺点：
1. quite noisy。
2. No theoretical justification， since it is not a martingale
3. counter-intuitive。比如说现在的LOB是ask1=11 q=1；bid1=10 qty=9.非常容易计算这个时候的W=10.1。这时候如果低于ask1的订单插入，比如说 ask订单 prc=10.5 qty=9，很显然fair-price应该下降，但是计算出来的W却上升了。

### micro-price
所以作者给了新的定义叫做micro-price：
$$
P^{micro} = M + g(I,S)
$$
$I$ 同上文，$S$代表的是Spread，$S=P^a-P^b$

这篇文章的目的主要是研究如何estimate fair-price的方法论。

作者认为自己的micro-price有以下优点：
1. martingale
2. 可以被视为资产的fair-price
3. 可以根据过去的LOB数据计算，并且运算非常的快。

## General Framework
