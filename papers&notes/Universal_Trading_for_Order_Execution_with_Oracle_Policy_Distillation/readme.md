![1paper1week](../../docs/1paper1week-git.jpg)

# Universal Trading for Order Execution with Oracle Policy Distillation

该论文研究最优执行，使用 oracle policy distillation 进行强化学习训练。论文中实验回测使用的指标比较贴近真实交易的效果评估，对比TWAP、VWAP、AC模型以及一些经典强化学习模型。交易回测忽略手续费，在之前我可能觉得忽略手续费的论文都是一坨屎，但是现在我觉得是正确的hhh。此外选择该论文的理由还有：
+ 1. [论文内置在qlib的高频交易中](https://github.com/microsoft/qlib/tree/high-freq-execution/examples/trade)，初期猜测的代码运行成本极低，方便复现自己实验。
+ 2. 最近在思考因子库的数据库设计逻辑，如果该论文能够帮我对qlib的数据库设计逻辑一探究竟的话那就太好了。qlib也提到对于LOB这种异步数据，他们使用MangoDB来进行存储。
+ 3. 论文会议是AAAI，21发布至今引用数61，十分可观（我不了解强化学习论文正常引用量是什么样子的）

后续会进行实验：
1. 作者认为想对于DDQN等强化学习模型，自己设计的奖励惩罚函数起了效果，事实是否如此？
2. DDQN原论文是在单一标的上训练，作者的OPD是在全市场上进行训练。如果换成单一标的训练会有什么效果？
3. 后续实验的疑点


## 订单执行问题
`一切以卖出平仓为例`
作者先介绍了订单执行问题本身，对于$\{0,1,2....T-1\}$一共$T$个时间点来说，$p$表示价格，$q$表示执行的数量，$Q$表示时间内需要执行的全部订单数量。问题变成：
$$\arg\max_{q_1,q_2,\ldots,q_T}\sum_{t=0}^{T-1}(q_{t+1}\cdotp_{t+1}),s.t.\sum_{t=0}^{T-1}q_{t+1}=Q.$$
交易员需要最大化成交价格：
$$\bar{P}=\frac{\sum_{t=0}^{T-1}(q_{t+1}\cdotp_{t+1})}{\sum_{t=0}^{T-1}q_{t+1}}=\sum_{t=0}^{T-1}\frac{q_{t+1}}{Q}\cdotp_{t+1}$$

这种情况下回测忽略手续费是合理的，因为你总是要卖出某些单位数量的股票，这个问题的本质是如何把原本的任务执行的更优，而不是一个 `single asset trading signal`问题

## 




