![1paper1week](../../docs/1paper1week-git.jpg)

# Bias in the effective of bid-ask spread

这次的文章在实证方面进一步研究了bid-ask spread。拿经典的 midpoint、weighted midpoint 以及之前文章提到过的 stikov micro-price 进行实证研究。之前的 stikov micro-price 也在文末用自己的方式证明了自己的研究成果更好，但是证明方式略显潦草，对bias形成的本质也没有这一篇如此详细。这一篇发布在 Journal of Financial Economics 上，洋洋洒洒有60页，所以这篇文章会分成多篇来写，但是每一篇中文帖子的内容含量绝对不会少。


## Abstract
这篇主要挑战了midpoint的 benchmark 地位，作者认为midpoint在 discrete prices and elastic liquidity demand 情况下错估了 fair-price。

## Introduction
作者先介绍 effective bid-ask spread 的应用场景。主要有如下：
1. 评估market架构变动的效果
2. 交易成本测量
3. 资产定价
4. 公司金融
5. 宏观

作者进一步介绍了measure传统 effective bid-ask spread 的midpoint，认为midpoint过度估计了流动性，并且说明了什么是effective bid-ask spread，在本文中：
$$
effective \ spread := (P^{ask}/P^{bid}- P^{fair})*2
$$
概念略显抽象，总之就是一个衡量最优买卖价格偏离真实价值的值，越小代表最优买卖价偏离的越小。文中给了一个简单的例子，在“The midpoint effective spread bias can be illustrated”那一段。这个定义的语言描述或许可以叫做：立刻执行价格成本与真实价格的差值的两倍。


所以在我们测算 effective spread 的时候，我们就需要计算一个价格来代替公式中的$ P^{fair}$，传统金融使用midpoint作为benchmark，这显然是不合理的。绝大多数情况下LOB都是asymmetry的，这个时候在两边立刻执行的执行成本不可能相同，这就涉及到作者介绍的一个新概念，liquidity demand is elastic。

### elastic demand
价格需求的弹性的。所以对于立刻执行的成本来说，两边是完全不一样的。

```
If traders respond to the cost asymmetry by trading more on the side of the market where the effective spread is tighter, as modeled by Goettler et al. (2005), the liquidity demand is elastic.
```

### Approach
作者证明了midpoint是无偏估计的条件，只有当交易的方向完全与资产的基本价值无关的时候，midpoint是无偏估计，即investor完全不在意或者说流动需求弹性不存在。

作者又引出了其它两个概念作为midpoint的对照，分别是 weighted midpoint 以及我们之前提到过的 stikov micro-price。这里不过多介绍这里啊分别是什么。

### Data Sample
1. 作者先是使用了S&P500成分股，2015年12月 7-11 的 trade & quote 数据。
2. 作者又实用了一些纳斯达克交易所披露的HFT交易数据
3. 最后作者将比较重新放在20年的时间里进行比较，使用NYSE这段时间所有的股票。

### Result
作者认为使用midpoint会造成3.22bps的偏差，weighted midpint的偏差大概是2.84bps。这数字看起来小，但是weighted midponit相比midpoint改进了18%。micro-price相比midpoint改进了23%。

bias in effective bid-ask spread 主要造成以下影响：
1. The bias influences liquidity-sorted portfolios because it varies with price discreteness.
2. Trading venue rankings are influenced because the bias varies across exchanges.
3. Finally, the bias feeds through to trading performance evaluations when investors differ in their monitoring of the fundamental value.

同时作者使用策略评估，对fair price更好的评估能否改进策略的表现？作者分别使用 midpoint 以及 weighted midpoint，模拟了 liquidity timing strategy 的表现。作者发现更好的评估指标不光能获得更好的策略表现，并且 excution shortfall 更低，which is a transaction price-based measure that does not rely on the accuracy of the fundamental value estimator.








## 嘻嘻
之前忙于搬家拖更了，这周三更补上。人总有忙的时候嘛（我是不会承认我小说瘾犯了，连续看了一周的小说的）嘻嘻。