![1paper1week](../../docs/1paper1week-git.jpg)

# stoikov_micro-price

该篇的目的是研究如何得到更好的 fair price，是我看到这篇[知乎文章](https://zhuanlan.zhihu.com/p/622226738)后决定一读原文。以我学生时随机过程弱鸡的成绩，该文章是注定一知半解的，但还是那句话“better late than never”。斗胆帮大家做一下翻译器。

## Abstract
1. 作者定义了micro-price，用于更好的替代mid-price（作为资产的fair-price）。
2. 作者认为真正的fair-price应该是一个martingale。
3. 使用的信息就是LOB数据，考虑到了spread以及orderbook imbalance数据。
4. 作者之后实证指出了为什么自己的micro-price更好。

## Introduction
HFT是一个很宽松的定义，在各种不相关的情况下被滥用。作者认为的HFT有以下几个共同特点:1.需要compute technology(硬件或者软件)；2.允许Agents以人类无法反应过来的速度进行交易。插一句，最近写高频交易公司的笔试题，该公司把 minute level rebalance 叫做 mid/long term，让我甚是震撼。作者这里之后给出了高频的几个方向：Optimal order splitting, pairs trading, statistical arbitrage, market making, liquidity provision, latency arbitrage and sentiment
analysis of news。

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
对于价格的预测应该服从以下的形式，这样的构造保证了他是一个martingale：
$$
P^i_t = E[M_{\tau_i}|F_t]
$$
$F_t$代表information in LOB，stopping time $\tau_1,......,\tau_n$代表mid-price发生改变的时间，比如：
$$
\tau_1 = inf\{u>t| M_u - M_{u^-} \neq 0\}
$$
$$
\tau_{i+1} = inf\{u>\tau_{i}| M_u - M_{u^-} \neq 0\}
$$
所以micro-price的定义是：
$$
P^{micro}_t = \lim \limits_{i \rightarrow \infty} P^i_t
$$
选用$\lim$的好处是：1. 每个截面上都是独立的； 2. 过滤掉了一些噪音

同时论文做出了一些假设：
### Assumption 1：
LOB中的信息$F_t$是一个马尔可夫过程且只跟三个维度的信息有关（或者说过滤后信息只跟这三个维度有关），分别是：1.mid-price $M_t$; 2. bid-ask spread $S_t = \frac{1}{2}(P^a_t - P^b_t)$; 3. imbalance $I_t$.
### Assumption 2:
mid-price 的变化跟mid-price的大小无关，或者说价格的变动在每一个tick上是一样的。
$$
E[M_{\tau_{i}} - M_{\tau_{i-1}}|M_t,I_t,S_t] = E[M_{\tau_{i}} - M_{\tau_{i-1}}|I_t,S_t]
$$

### Theorem
given 2 assumption:
$$
P^i_t = M_t + \sum_{k=1}^i g^k(I_t,S_t)
$$
where
$$
g^1(I,S) = E[M_{\tau_{1}} - M_{\tau_{t}}|I_t,S_t]
$$
$$
g^{i+1}(I,S) = E[g^{i}(I_{\tau_1},S_{\tau_1})|I_t,S_t],\  compute \ recursively
$$

## Finite state space example

现在在我们已知 $(M_t, I_t, S_t)$, 要估计fair price。为了对离散过程进行建模同时减少计算量，我们进行以下处理：

1. 我们把 $I_t$ 分为 n 段，每一段的表示为如下公式。比如说[1，2，3，4，5]分别表示imbalance程度为[0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0]：
$$
I_t=\sum_{j=1}^nj\mathbb{1}_{\left(\frac{j-1}{n}<\frac{Q_t^b}{Q_t^b+Q_t^a}\leq\frac{j}{n}\right)}
$$

2. 同时 spread 的值为离散值，服从 1<= s <= m

所以状态 $(I_t, S_t)$ 为离散值，且取值有 nm 个。

3. 我们使用$K=\begin{bmatrix}-0.01,-0.005,0.005,0.01\end{bmatrix}^T$来表示 mid-price 的变动，（或者取值为 -1个tick，-0.5个tick， 0.5个tick， 1个tick）

则对于下一个时刻的 mid-price 的变动来说，服从以下的公式：

$$\begin{aligned}
G^{1}(x)& =\mathbb{E}\left[M_{\tau_{1}}-M_{t}|X_{t}=x\right]  \\
&= \sum_{k\in K}k\cdot\mathbb{P}(M_{\tau_{1}}-M_{t}=k|X_{t}=x)  \\
&=\sum_{k\in K}\sum_{u}k\cdot\mathbb{P}(M_{\tau_{1}}-M_{t}=k\wedge\tau_{1}-t=u|X_{t}=x)
\end{aligned}$$

我们估计两种状态：
1. R := absorbing states, 可以理解为在给定 $(I_t, S_t)$ 下，mid-price发生改变k的概率，其中k是上文中定义的K的取值。所以矩阵的维度是 4 x nm
$$R_{xk}:=\mathbb{P}(M_{t+1}-M_t=k|X_t=x)$$


2. Q :=  transient states, 可以理解为在给定 $x = (I_t, S_t)$ 下，mid-price 不发生改变且下一个状态是新的$y = (I_t, S_t)$ 的概率。所以矩阵的维度是 nm x nm
$$Q_{xy}:=\mathbb{P}(M_{t+1}-M_t=0\wedge X_{t+1}=y|X_t=x)$$

所以下一个时刻，mid-price 发生改变的期望是：
$$G^1(x)=\bigl(\sum_sQ^{s-1}R\bigr)K=\bigl(1-Q\bigr)^{-1}RK$$

通过递归我们就可以算出来$G^{i+1}(x)$


### 最终公式

为了方便计算，我们重新定义 absorbing states T, 新的矩阵维度是 nm x nm:
$$T_{xy}:=\mathbb{P}(M_{t+1}-M_t\neq0\wedge X_{t+1}=y|X_t=x)$$

定义$B:=\left(1-Q\right)^{-1}T$， B 显然是一个 nm x nm 的矩阵。则最终的价格为：
$$P_t^i=M_t+\sum_{k=0}^iB^kG^1$$

THEOREM $3.1\quad If\:B^*=\lim_{k\to\infty}B^k\:and\:B^*G^1=0,\:then\:the\:limit$
$\lim_{i\to\infty}P_{t}^{i}=P_{t}^{micro}$
$converges.$

The matrix $B$ is a regular stochastic matrix so it can be decomposed

$$
B=B^*+\sum_{j=2}^{nm}\lambda_jB_j
$$

所以最终的公式为：

$$P_t^{micro}=\lim\limits_{i\to\infty}P_t^i=M_t+G^1+\sum\limits_{j=2}^{nm}\frac{\lambda_j}{1-\lambda_j}B_jG^1$$

