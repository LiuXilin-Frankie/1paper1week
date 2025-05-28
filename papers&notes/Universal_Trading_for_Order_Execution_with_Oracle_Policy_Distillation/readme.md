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

## 强化学习的MDP过程

在已知状态$s_t$下，策略遵守交易规则$\pi$生成下一步的动作，即$a_t = \pi(s_t)$，为下一时刻的成交量，即$q_{t+1} = a_t * Q $。最后时刻全部订单必须被完全交易，所以最后时刻的$a_{T-1}=\max\{1-\sum_{i=0}^{T-2}a_{i},\pi(s_{T-1})\}$。奖励函数为：
$$\hat{R}_{t}^{+}(s_{t},a_{t})=\frac{q_{t+1}}{Q}\cdot\overbrace{\left(\frac{p_{t+1}-\tilde{p}}{\tilde{p}}\right)}^{\text{price mormalization}}=a_{t}\left(\frac{p_{t+1}}{\tilde{p}}-1\right)$$
其中$\tilde{p}=\frac{1}{T}\sum_{i=0}^{T-1}p_{i+1}$是整个时间段的平均价格，作者这里承认使用了未来信息，但是它认为只在训练教师的时候作为反向传播使用，不存在信息泄露。

同时作者还增加了流动性惩罚，市场冲击成本，即$$\hat{R}_t^-=-\alpha(a_t)^2$$

所以最终的奖励函数是：
$$\begin{aligned}
R_{t}(s_{t},a_{t}) & =\hat{R}_{t}^{+}(\boldsymbol{s}_{t},a_{t})+\hat{R}_{t}^{-}(\boldsymbol{s}_{t},a_{t}) \\
 & =\left(\frac{p_{t+1}}{\tilde{p}}-1\right)a_{t}-\alpha\left(a_{t}\right)^{2}.
\end{aligned}$$

所以强化学习的最终目标就是解决下述的优化问题：$$\arg\max_\pi\mathbb{E}_\pi\left[\sum_{t=0}^{T-1}\gamma^tR_t(s_t,a_t)\right].$$


## Policy Distillation
教师学习全局信息，做出交易决策；学生学习教师的决策并且进行模仿，使用的信息是不完全的部分的历史信息。为了建立学生和教师之间的联系，我们使用这样的损失函数评估（其中$\tilde{a}_t$表示教师在t时刻的决策：
$$L_d=-\mathbb{E}_t\left[\log\Pr(a_t=\tilde{a}_t|\pi_{\boldsymbol{\theta}},\boldsymbol{s}_t;\pi_{\boldsymbol{\phi}},\tilde{\boldsymbol{s}}_t)\right],$$

这里缺乏理解，后面需要结合补充材料和代码去看，最终的损失函数如下，教师和学生都使用PPO进行训练，对于教师来说不适用最后一项的策略蒸馏损失：$$L(\theta)=\overbrace{L_{p}+\lambda L_{v}}^{\text{poticy optimization}}+\overbrace{\mu L_{d}}^{\text{poticy distitlation}},$$

## 实验对比

作者使用：
1. TWAP
2. VWAP
3. AC
4. DDQN
5. PPO

进行对比，其中前三个作者认为是基于模型的，后两个作者认为是基于学习的。结论是学生策略优于所有其它策略（劣于教师策略），所以Oracle的策略蒸馏是有效的，同时OPD优于其它的强化学习策略，作者认为说明奖励函数是有效的

## 疑点
1. 作者使用全部的A股数据训练，使用样本时间外，沪深300作为验证集和训练集。更换数据集会怎么样？
2. DDQN、PPO原论文不是在全部股票上训练，而是一只股票一个模型，那如果是只用一个股票数据训练，OPD效果怎么样？
3. 作者认为自己设计的奖励函数有效，但是没有控制变量进行试验。




