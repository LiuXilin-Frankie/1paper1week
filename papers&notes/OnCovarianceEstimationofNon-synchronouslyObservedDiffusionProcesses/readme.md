![1paper1week](../../docs/1paper1week-git.jpg)

# On covariance estimation of non-synchronously observed diffusion processes

论文考虑当仅在离散时间以非同步方式观察两个扩散过程时估计两个扩散过程的协方差的问题。论文中提出的新的估计方法，它不需要对原始数据进行任何“同步”处理，因此没有偏差或由此引起的其他问题。这也就意味着这种方法更加roubust。


## Introduction

对于价格序列 $(P^1_{t_i},P^2_{t_i})_{i=0,1,...,m}$ ,我们希望计算这两个序列的协方差，如下方法计算的叫做 realized covariance：

$$V_{\pi(m)}:=\sum_{i=1}^m(P_{t_i}^1-P_{t_{i-1}}^1)({P_{t_i}}^2-P_{t_{i-1}}^2),\quad(1.1)$$

但是我们实际应用的时候面对以下问题，为了解决一下问题插值处理获得的估计是有偏估计：
1. 数据异步，并不是每个时间点我们都能同时得到两个资产的价格数据
2. 时间间隔随机。
