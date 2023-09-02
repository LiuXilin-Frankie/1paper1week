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

### 胡说八道
关于流动性需求弹性的想法：
1. 已知流动性需求弹性存在，weighted midponit 和 midpoint 都是有偏估计
2. midpoint 为什么有偏，因为完全低估（无视）了价格需求弹性
3. weighted midpoint 为什么有偏，因为高估了价格需求弹性

所以是不是假如真的存在 $P^{fair}$ weighted midponit 和 midpoint 虽然都是有偏，但是偏在了完全不同的方向。

假如我现在引入一个新的概念：
$$
new-price = (P^{weighted \ midponit} + P^{midponit})/2
$$
效果会如何呢

如果我拿出xx，阁下又该如何应对呢。





### Lee and Ready algorithm
实证市场微观结构研究通常需要了解交易是由买方还是卖方发起的。 例子包括但不限于有效价差的准确计算（Lightfoot等人，1999年），使用基于交易指标变量的方法识别买卖价差的组成部分（Huang和Stoll，1997年）以及 某些结构微观结构模型的估计（例如，Easley 等人，1996b）。


通常可用的数据集不提供有关交易发起者的信息。 因此，研究人员使用算法将交易分类为买方发起的交易或卖方发起的交易。 最简单的算法是“tick test”。 如果交易价格较高（低于之前的交易价格），则将交易分类为买方发起（卖方发起）。因为只需要交易数据 , 应用 tick test 的数据要求较低 - 但算法的准确性也可能较低。Lee 和 Ready (1991) 提出了一种算法，可以在报价和交易数据都可用时应用。该算法分三个阶段进行

1.
以高于（低于）报价中点的价格发生的交易被归类为买方发起的（卖方发起的）。

2.
以等于报价中点但高于（低于）前一交易价格的价格发生的交易被归类为买方发起（卖方发起）。

3.
以等于报价中点和前一交易价格但高于（低于）最后一个不同交易价格的价格发生的交易被归类为买方发起（卖方发起）。