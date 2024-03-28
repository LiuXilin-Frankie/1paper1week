# load libraries 
import math
import decimal 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

from scipy.linalg import block_diag
from scipy.linalg import eig



def processing_data(df_data, n_imb, n_spread, dt, is_filter_symm=True):
    """
    processing data for micro price construction 
    """
    
    ## 1. calculate relevant indicators 
    # find tick size 
    # minimum of absolute spread is the tick size 
    spread = df_data["ask_price"] - df_data["bid_price"]
    ticksize = np.round(min(spread.loc[spread > 0]) * 1e6) / 1e6
    print('tick_size is', ticksize)

    # spread in terms of tick 
    df_data['spread'] = np.round((df_data['ask_price'] - df_data['bid_price']) / ticksize) * ticksize

    # mid price
    df_data['mid'] = (df_data['ask_price'] + df_data['bid_price'])/2

    # weighed mid price 
    df_data['wmid'] = (
        (df_data['ask_price'] * df_data['bid_size'] + df_data['bid_price']*df_data['ask_size'])
        / (df_data['ask_size'] + df_data['bid_size'])
    )

    # orderbook imbalance 
    df_data["imb"] = df_data["bid_size"] / (df_data["bid_size"] + df_data["ask_size"])

    # discretize imbalance into percentiles
    df_data['imb_bucket'] = pd.qcut(df_data['imb'], n_imb, labels=False)

    # next
    df_data['next_mid'] = df_data['mid'].shift(-dt)
    df_data['next_wmid'] = df_data['wmid'].shift(-dt)
    df_data['next_spread'] = df_data['spread'].shift(-dt)
    df_data['next_imb_bucket'] = df_data['imb_bucket'].shift(-dt)

    # mid price difference -- half tick 
    df_data["dM"] = np.round((df_data['next_mid'] - df_data['mid']) / ticksize * 2) * ticksize / 2
    # weighted mid price difference -- half tick 
    df_data["dwM"] = np.round((df_data['next_wmid'] - df_data['wmid']) / ticksize * 2) * ticksize / 2
    
    if is_filter_symm:
        # filter out spreads >= n_spread
        df_data = df_data.loc[(df_data["spread"] <= n_spread * ticksize)]
        # filter out dM > 1.1 * ticksize
        df_data = df_data.loc[(df_data["dM"] <= ticksize*1.1) & (df_data["dM"] >= -ticksize*1.1)]

        ## 2. symmetrize data
        #    - (It,St,It+1,St+1,dM) ==> (1-It,St,1-It+1,St+1,-dM)

        df_data_symm = df_data.copy(deep=True)
        df_data_symm['imb_bucket'] = n_imb - 1 - df_data_symm['imb_bucket']
        df_data_symm['next_imb_bucket'] = n_imb - 1 - df_data_symm['next_imb_bucket']
        df_data_symm['dM'] = -df_data_symm['dM']

        df_data = pd.concat([df_data, df_data_symm])
    
    return df_data 

def estimate_transi_prob(df_data, K, n_imb, n_spread):
    """
    Function to estimate transition probabiliies [Q, T, R]
    """
  
    # Q ==> transient states, 瞬时状态  [nm * nm] 
    # Xt := (It,St)
    # probability that mid_price dont change, known Xt, Xt+1

    # locate all that don't move 
    no_move = df_data[df_data['dM'] == 0]

    # count 
    # no need to use next_spread, coz mid_price not move, next_spread should stay the same 
    no_move_counts = no_move.pivot_table(index=['next_imb_bucket'], 
                                         columns=['spread', 'imb_bucket'], 
                                         values='time_seconds',
                                         fill_value=0, 
                                         aggfunc='count').unstack()

    # resize to [n * n] ==> first matrix when m=1 
    Q_counts = np.resize(np.array(no_move_counts[0:(n_imb*n_imb)]), (n_imb,n_imb))

    # loop over all spreads and add block matrices
    for i in range(1,n_spread):
        Qi = np.resize(np.array(no_move_counts[(i*n_imb*n_imb):(i+1)*(n_imb*n_imb)]),(n_imb,n_imb))
        Q_counts = block_diag(Q_counts, Qi)

    # R2 ==> transient matrix, 瞬时状态 [nm * nm] ==> represents T in the paper 
    # Xt := (It,St)
    # probability that mid_price do change, known Xt, Xt+1

    # locate all that move 
    do_move = df_data[df_data['dM'] != 0]

    # count all moves 
    # 必须要对齐，index, columns 位置要正确
    move_counts = do_move.pivot_table(index=['spread', 'imb_bucket'], 
                                      columns=['next_spread', 'next_imb_bucket'], 
                                      values='time_seconds',
                                      fill_value=0, 
                                      aggfunc='count')
    # R2 = T 
    # resize to [nm * nm] 
    R2_counts = np.resize(np.array(move_counts), (n_imb*n_spread, n_imb*n_spread))

    # R ==> absorbing states, [nm * 4]
    move_counts2 = do_move.pivot_table(index=['dM'], 
                                       columns=['spread', 'imb_bucket'], 
                                       values='time_seconds',
                                       fill_value=0, 
                                       aggfunc='count').unstack()

    R_counts = np.resize(np.array(move_counts2), (n_imb*n_spread,4))
    
    # T1 = [Q_counts, R_counts]
    # combine them and calculate probability from count 
    T1 = np.concatenate((Q_counts, R_counts), axis=1).astype(float)

    # probability known Xt, Xt+1 = (count_i) / (count_dont_move + count_move)
    for i in range(0, n_imb*n_spread):
        T1[i, :] = T1[i, :] / T1[i, :].sum()

    # return Q, R1 in probability 
    Q = T1[:,0:(n_imb*n_spread)]
    R1 = T1[:,(n_imb*n_spread):]

    # T2 = [Q_counts, R2_counts]
    # combine them and calculate probability from count 
    T2 = np.concatenate((Q_counts, R2_counts), axis=1).astype(float)

    # probability known Xt, Xt+1 = (count_i) / (count_dont_move + count_move)
    for i in range(0, n_imb*n_spread):
        T2[i, :] = T2[i, :] / T2[i, :].sum()

    # return Q2, R2 in probability 
    Q2 = T2[:, 0:(n_imb*n_spread)]
    R2 = T2[:, (n_imb*n_spread):]
    
    # Calculate G1 [nm * 1]
    # G1 = (1-Q)**-1 * R * K 
    G1 = np.dot(np.dot(np.linalg.inv(np.eye(n_imb*n_spread) - Q), R1), K)
    
    # Calculate G* ==> micro price adjustment 
    # B = (1-Q)**-1 * R2 [nm*nm]
    B = np.dot(np.linalg.inv( np.eye(n_imb*n_spread) - Q), R2)
    
    return G1,B,Q,Q2,R1,R2

def f_cal_G6(G1, B):
    """
    calculate micro price 
    """
    G2=np.dot(B,G1)+G1
    G3=G2+np.dot(np.dot(B,B),G1)
    G4=G3+np.dot(np.dot(np.dot(B,B),B),G1)
    G5=G4+np.dot(np.dot(np.dot(np.dot(B,B),B),B),G1)
    G6=G5+np.dot(np.dot(np.dot(np.dot(np.dot(B,B),B),B),B),G1)
    return G6

def get_default_K(df_data):
    """
    获取默认 K 的函数，默认 K 为
    [-1个tick, -0.5个tick,  0.5个tick, 1个tick]
    """
    spread = df_data["ask_price"] - df_data["bid_price"]
    ticksize = np.round(min(spread.loc[spread > 0]) * 1e6) / 1e6

    return np.array([-1*ticksize, -0.5*ticksize, 0.5*ticksize, 1*ticksize])


# Function to estimate transition probabiliies 
# from https://github.com/shaileshkakkar/MicroPriceIndicator/blob/master/Micro-Price%20Reproduction.ipynb

def estimate_old(T):
    no_move=T[T['dM']==0]
    no_move_counts=no_move.pivot_table(index=[ 'next_imb_bucket'], 
                     columns=['spread', 'imb_bucket'], 
                     values='time',
                     fill_value=0, 
                     aggfunc='count').unstack()

    #print no_move_counts
    Q_counts=np.resize(np.array(no_move_counts[0:(n_imb*n_imb)]),(n_imb,n_imb))
    # loop over all spreads and add block matrices
    for i in range(1,n_spread):
        Qi=np.resize(np.array(no_move_counts[(i*n_imb*n_imb):(i+1)*(n_imb*n_imb)]),(n_imb,n_imb))
        Q_counts=block_diag(Q_counts,Qi)
    #print Q_counts
    move_counts=T[(T['dM']!=0)].pivot_table(index=['dM'], 
                         columns=['spread', 'imb_bucket'], 
                         values='time',
                         fill_value=0, 
                         aggfunc='count').unstack()

    R_counts=np.resize(np.array(move_counts),(n_imb*n_spread,4))
    T1=np.concatenate((Q_counts,R_counts),axis=1).astype(float)
    for i in range(0,n_imb*n_spread):
        T1[i]=T1[i]/T1[i].sum()
    Q=T1[:,0:(n_imb*n_spread)]
    R1=T1[:,(n_imb*n_spread):]

    move_counts=T[(T['dM']!=0)].pivot_table(index=['spread','imb_bucket'], 
                     columns=['next_spread', 'next_imb_bucket'], 
                     values='time',
                     fill_value=0, 
                     aggfunc='count') #.unstack()

    R2_counts=np.resize(np.array(move_counts),(n_imb*n_spread,n_imb*n_spread))
    T2=np.concatenate((Q_counts,R2_counts),axis=1).astype(float)

    for i in range(0,n_imb*n_spread):
        T2[i]=T2[i]/T2[i].sum()
    R2=T2[:,(n_imb*n_spread):]
    Q2=T2[:,0:(n_imb*n_spread)]
    G1=np.dot(np.dot(np.linalg.inv(np.eye(n_imb*n_spread)-Q),R1),K)
    B=np.dot(np.linalg.inv(np.eye(n_imb*n_spread)-Q),R2)
    
    return G1,B,Q,Q2,R1,R2,K