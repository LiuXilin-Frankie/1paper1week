![1paper1week](../../docs/1paper1week-git.jpg)

# Exploring Market Making Strategy for High Frequency Trading_ An Agent-Based Approach

该篇的目的是迅速帮助我了解做市商的原理，全文笔记或者说全文翻译如下：

## 高频交易做市商建模
仿照现实世界的股票市场，该篇论文提出了一个由Agents组成的股票市场，在这个市场中Agents通过订单薄进行交易。根据他们目的以及行为的不同，主要被分为两类：
- 一类是低频交易者（`LFTer`），他们关心资产的真实价值并试图使用基本面和图表分析的综合策略获利；
- 另一类是高频交易者（`HFTer`），他们不在意资产的真实价值，主要通过做市策略在spread上积累利润。

论文针对这样的市场模拟日内交易场景并进行建模，全文假设LFTers和HFTers都在同一个资产上进行交易。


## 模型框架
模型总共由T个时间段，每个时间段LFTers和HFTers都进行交易，并各自遵守自己的交易准则：
1. LFTers根据自己的模型以及数据计算资产的预期价值，计算决定是否在此时入场。并决定bid或ask的价格以及订单大小。
2. HFTers知道LFTers提交的orders（或者说可以看到部分），决定是否进场。如果决定进入，他们通常会向市场提交规定好价格以及数量的限价单。吸收LFTers的订单并从中赚取差价获利。
3. LFTers和HFTers的订单到达交易所，交易所根据到达顺序、价格对订单进行撮合，未被执行的订单将会保留在订单薄中并出现在之后的时间段里（如果没有取消的话）。
4. 每个时间段结束时，LFTers和HFTers根据各种因素调整自己的交易参数（是否要下更大的订单，是否需要着手卖出控制仓位等等），并更新已有订单（撤销并下新的订单/不对订单进行更改）

## LFTers的交易行为
对于每一个交易时间段内，每一个活跃的LFTer_i的行为如下(这里低频交易者行为简单带过)：
1. 根据动态更新的概率值$ {LF}^i\_ap $，决定是否要进入活跃状态（持续观察市场准备进行操作）。
2. 如果决定处于活跃状态，${LFT}^i$ 根据该资产的预期价格 ${LF}^i\_EP$ 计算自己的预期收益$ {LF}^i\_ER $，同时计算买入价格以及卖出价格。根据其它论文中的观点，LFTers通过加权基本面+量价+噪声，共同预测未来收益。
3. 向交易所递交相应的买入卖出订单（同时可能要决定订单的数量）。订单的有效时间为$\gamma^L$，超时未被执行则订单会被取消。
4. $τ$时间段结束后，${LFT}^i$ 决定是否要更新自己的交易参数，并循环开启下一次交易。

## HFTers交易行为
对于每一个交易时间段内，每一个活跃的${HFT}^j$的行为如下：
1. ${HFT}^j$ 根据价格在时间t的波动 $P_t^{flu}(bps)$ 以及自身预先设置的是否行动的threshold ${HF}^j\_at$，决定是否活跃，如果 $P_t^{flu}$ > $HF^j\_at$ 则 ${HFT}^j$ 处于活跃状态.
$$
P_t^{flu}=\mid\frac{p_{t-1}-p_{t-2}}{p_{t-1}}\mid\times10,000\ \ \ and\ \ {HF}^j\_at\sim U(\alpha_{min}^H,\alpha_{max}^H)
$$
2. 如果决定处于活跃状态， ${HFT}^j$ 会同时提交数量为 ${HF}^j\_AS$ 价格为 ${HF}^j\_AP$ 的卖单，以及数量为 ${HF}^j\_BS$ 价格为 ${HF}^j\_BP$ 的买单，订单的到达时间随机，且有效时长为$\gamma^H$，超时未被执行则订单会被取消。
    
    在默认情况下，$HF^j\_AP=p_t+κ_j^H$,$HF^j\_BP=p_t-κ_j^H$,$κ^H$是价格的波动参数。$HF^j\_AS=HF^j\_BS=0.5×(q_b+q_s)×η_j^H$ ,$q_b (q_s) $可以理解为在该时间段t下，订单薄买入（卖出）订单的总数，$η_j^H$可以理解为关于订单吸收速度的参数。
3. 同低频交易者一样，在$τ$时间段结束后，${HFT}^j$ 基于策略表现决定是否要更新参数。

我们的模型假设高频交易通常利用做市并试图赚取差价积累利润，事实上他们并不是一直如此。当他们检测到LFT的交易趋势并推测到订单将会持续失衡时，他们会采取激进的做市策略（aggressive market making），这个时候他们不是流动性的提供者，摇身一变变为take流动性的taker。在这种情况下，他们会快速交易以从价格变动中获利，或者平仓。 在我们的模型中，我们进行每日结算，收盘后的收益就是HFTers的交易收益，但是HFTers收盘后的库存所带来的隔夜风险确是他们主要的风险来源

## 被动做市以及主动做市
HFTers在被动（maker）做市和激进（taker）做市之间切换。 在通常情况下，HFT 使用被动做市为整个市场交易提供流动性，他们根据最新交易价格或最佳询价（best ask）/买价（best bid）进行报价以赚取价差。 但是当LOB中出现显著的不平衡时，即当$∣q_b - q_s∣/(q_b + q_s)$超过一个预先设定的阈值时，他们将采取激进的做市。在这种情况下，HFT要么跟随临时趋势报价获取趋势端的收益，要么下相反的单来清理目前的库存。

当高频交易采用被动做市时，报价围绕最后交易价格提供最佳询价/买价。当高频交易者采用主动做市时，比如说$∣q_b - q_s∣/(q_b + q_s) >0.5$。如果现在市场上卖单多余买单，在0.5的阈值下代表卖单是买单的三倍，趋势跟踪高频交易者选择在$P_t$价位提交卖单，在 $P_t-k_2$ 的价位提交卖单，$k_2$是在主动做市情况下的参数值。如果高频交易者选择反向以清理库存，则在$P_t+k_2$的价位提交卖单，$P_t$价位提交买单。

## 做市商策略的下单数量
为了获得更多的利润和更少的风险，高频交易者会考虑两个方面,增加订单履行的机会（increasing the chance of order fulfillment）并控制仓位平稳尽可能地平仓（keeping flat position accordingly）。

- For increasing the chance of order fulfillment，
高频交易者通过提交订单，尽可能地吸收低频交易者提交的订单来赚取spread价差，这是高频交易者采取被动做市时的利润来源。当高频交易者采取主动做市时，他们希望通过吸收过剩的流动性来获利（LOB中某一方存在过剩的订单，HFTers这是成为taker不再提供流动性）。所有高频交易商都会通过计算过去几个交易日的平均订单执行率来自适应调整他们的订单数量。 假设$r_m$和$r_h$指的是过往$τ$交易时段的市价单（market order）成交率和自单（self order）成交率，则下单量Q由下式决定：
$$
Passive:Q=min(q_b,q_s)×0.5×(r_m+r_h)
$$
$$
Aggressive:Q=∣q_b-q_s∣×0.5×(r_m+r_h)
$$

- For keeping flat position accordingly，我们根据其他论文引入概念：$NT$作为我们设置的阈值，$np$作为HFTers的净头寸。 假设 $V_i$ 代表第i时段的交易量，$NT$与第一期的平均交易量成正比，那么在$τ$期后，$NT$的计算方式如下:
$$
NT=\frac{1}{τ} ∑_{i=1}^τ V_i 
$$

notes:
- 当$|np|<NT*0.5$, 高频交易者像往常一样交易
- $ 0.5*NT$ $⩽∣np∣$ < $ NT $, 有意将价格向某一方向调整一个tick以提高成交率
- $NT⩽∣np∣$ 时我们停止某一个方向的交易，只进行平仓
- HFTers被允许的同时存在最大订单数量和$NT$相等