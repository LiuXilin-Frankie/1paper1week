![1paper1week](../../docs/1paper1week-git.jpg)

# Lead-Lag relationship

该篇的目的是研究UHF视角下的资产回报之间的关联性。我选择的论文是arxiv上的最初版本，该版本相比于直接发表在期刊上的版本，少了很多对于theory的阐述，整体写作逻辑更精炼。

## Abstract
论文发现如下：
1. 更高流动性的asset更有可能lead流动性低的asset（这里给了高流动性的定义: short intertrade duration, narrow bid/ask spread, small volatility, high turnover）
2. 但是关联性最高的 asset pair 往往是具有相似流动性的。
3. lead lag relationship 在日内并不是一个定值，可能受到一些宏观的影响出现周期性
4. 当我们专注于一些 events 的时候， relationship十分显著。

通过使用 lead-lag relationship 辅助 predict mid quote 的变化，可以达到60%的准确率。高于直接基于 lag assets 的历史数据进行预测。但是这个策略却很难直接应用于一些策略，主要原因是市场的交易成本以及 bid-ask spread。

## 1.Data description
数据预处理：
1. 对于高频数据来说（A股市场同理），tick数据一般分为 quote，trade，order 三类，这里只使用trade以及quote数据。
2. 对于trade数据来说，如果一次交易分别成交在了两个价位上，记录会分成两条记录，对于这样的一次交易分两条记录的情况，我们把数据aggregate，记录的价格是vwap价格，成交量是这两条的加和。也就是说对于每一个独立的成交事件（在数据表单中是timstamps），有且仅有一条记录在表格当中。
3. 只考虑equities以及对应的futures，原论文给出了汇总表格。

作者同时使用了一些指标来衡量asset的流动性，如下：
+ the average duration between two consecutive trades $<\Delta t>$，连续两次交易的平均时间间隔
+ the average tick size δ in percentage of the midquote $<\delta/m>$，tick size和平均midquote的比
+ the average bid/ask spread expressed in tick size $ <s>/\delta$ 平均 bidask spread 和tick的比值
+ the frequency of unit bid/ask spread $1_{\{s=δ\}}$ bidask spread 恰好为一个标准tick的出现频率
+ the frequency of trades hitting more than the best limit price available $1_{\{trade \ through\}}$ 交易突破最优价格的频率
+ a proxy for the daily volatility expressed in tick size : $<|\Delta m|>/\delta$, where $\Delta m$ is the midquote variation between two consecutive trades 连续两次交易的变化与tick的比值
+ the average turnover per trade $<P_{trade}V_{trade}>$

## 2. Methodology
