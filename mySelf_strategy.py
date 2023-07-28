# -*- coding: utf-8 -*-
"""
Created on Mon May 16 15:39:35 2022

@author: karta
"""

import talib
import yF_Kbar

import pandas as pd
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)

from KPI import get_KPI

def get_MA(stock_id, period="12mo"):
    df = yF_Kbar.get_data(stock_id, period)
    
    #把英文欄位名稱改為中文
    df.rename(columns={"Open":"開盤價",
                       "High":"最高價",
                       "Low":"最低價",
                       "Close":"收盤價",
                       "Volume":"交易量"}
                       , inplace =True)
    
    #新增欄位
    
    df["SMA_5"]=0 #計算SMA5
    df["SMA_10"]=0 #計算SMA10
    df["SMA_20"]=0 #計算SMA20
    df["SMA_60"]=0 #計算SMA60
    
    df["SMA_5"]=talib.SMA(df["收盤價"],5) #計算SMA5
    df["SMA_10"]=talib.SMA(df["收盤價"],10) #計算SMA10
    df["SMA_20"]=talib.SMA(df["收盤價"],20) #計算SMA20
    df["SMA_60"]=talib.SMA(df["收盤價"],60) #計算SMA60

    
    return df

def trade(df):
    df["Buy"] = pd.NA
    df["Sell"] = pd.NA
  
    last_index = df.index[-1]
    hold = 0 # 是否持有
    #foreach每個row
    for index, row in df.copy().iterrows():
        # 最後一天不交易，並將部位平倉
        if index == last_index: 
            if hold >= 1: # 若持有部位，平倉
                  df.at[index, "Sell"] = row["收盤價"] # 紀錄賣價
                  hold = 0
            break # 跳出迴圈
        #買進條件
        #買進條件1 目前股價>=月線 且 目前股價<季線，月到季是搶反彈的時候
        #買進條件2 目前股價>=5,10,20,60 -> 四海遊龍
        #買進條件3 5MA>=10MA
        buy_condition_1=(row["收盤價"]>=row["SMA_20"]) and (row["收盤價"]<row["SMA_60"])
        buy_condition_2=(row["收盤價"]>=row["SMA_60"]) and (row["收盤價"]>=row["SMA_20"])and (row["收盤價"]>=row["SMA_10"])and (row["收盤價"]>=row["SMA_5"])
        buy_condition_3=(row["SMA_5"]>=row["SMA_10"])
        
        #賣出條件
        #賣出條件1 目前股價<月線 且 目前股價<季線，把搶反彈的部位賣掉
        #賣出條件2 目前股價<5日賣掉
        #賣出條件4 目前股價<=5,10,20,60 -> 四面楚歌。還沒寫
        #賣出條件3 5MA<=10MA
        sell_condition_1=(row["收盤價"]<row["SMA_20"]) and (row["收盤價"]<row["SMA_60"])
        sell_condition_2=(row["收盤價"]<row["SMA_5"])
        sell_condition_3=(row["SMA_5"]<=row["SMA_10"])
        
        #符合買進條件1，沒有持股就買入
        # if(buy_condition_1) and hold==0:
        #     df.at[index, "Buy"]=row["收盤價"]  #記錄買價
        #     hold=1 #持股
        #加碼
        if(buy_condition_1 or buy_condition_2 or buy_condition_3) and hold==0:
            df.at[index, "Buy"]=row["收盤價"]  #記錄買價
            hold=1 #持股
        #符合賣出條件1，有持股把搶反彈的部位賣掉
        # elif(sell_condition_1) and hold==1:
        #     df.at[index, "Sell"]=row["收盤價"]  #記錄賣價
        #     hold=0 
        #減碼
        elif(sell_condition_1 and sell_condition_2 and sell_condition_3) and hold==1:
            df.at[index, "Sell"]=row["收盤價"]  #記錄賣價
            hold=0
    return df

    # 將買賣價格配對
    record_df = pd.DataFrame()
    record_df["Buy"] = df["Buy"].dropna().to_list()
    record_df["Sell"] = df["Sell"].dropna().to_list()
    record_df["Buy_fee"] = record_df["Buy"] * 0.001425
    record_df["Sell_fee"] = record_df["Sell"] * 0.001425
    record_df["Sell_tax"] = record_df["Sell"] * 0.003
    
    # 交易次數
    trade_time = record_df.shape[0] 

    # 總報酬
    record_df["profit"] = (record_df["Sell"] - record_df["Buy"] - record_df["Buy_fee"] - record_df["Sell_fee"] - record_df["Sell_tax"]) * 1000
    total_profit = record_df["profit"].sum()
    
    # 成敗次數
    win_times = (record_df["profit"] >= 0).sum()
    loss_times = (record_df["profit"] < 0).sum()

    # 勝率
    if trade_time > 0:
        win_rate = win_times / trade_time
    else:
        win_rate = 0
    
    # 獲利/虧損金額
    win_profit = record_df[ record_df["profit"] >= 0 ]["profit"].sum()
    loss_profit = record_df[ record_df["profit"] < 0 ]["profit"].sum()
    
    # 獲利因子
    profit_factor =abs(win_profit / loss_profit)
    
    # 平均獲利金額
    if win_times > 0:
        avg_win_profit = win_profit / win_times
    else:
        avg_win_profit = 0.0000000001

    # 平均虧損金額
    if loss_times > 0:
        avg_loss_profit = loss_profit / loss_times
    else:
        avg_loss_profit = 0.0000000001
    # avg_loss_profit分母不能是1
    # 沒有交易紀錄就不要算不然會出錯
    # 賺賠比
    if trade_time>0:
        profit_rate = abs(avg_win_profit / avg_loss_profit)
    else:
        profit_rate = 0
    # 最大單筆獲利
    max_profit = record_df["profit"].max()
    
    # 最大單筆虧損
    max_loss = record_df["profit"].min()
    
    # 最大回落MDD
    record_df["acu_profit"] = record_df["profit"].cumsum() # 累積報酬
    MDD = 0
    peak = 0
    for i in record_df["acu_profit"]:
        if i > peak:
            peak = i
        diff = peak - i
        if diff > MDD:
            MDD = diff
    
    #KPI DF
    KPI_df = pd.DataFrame()
    KPI_df.at["交易次數", "數值"] = trade_time
    KPI_df.at["總報酬", "數值"] = total_profit
    KPI_df.at["成功次數", "數值"] = win_times
    KPI_df.at["虧損次數", "數值"] = loss_times
    KPI_df.at["勝率", "數值"] = win_rate
    KPI_df.at["獲利總金額", "數值"] = win_profit
    KPI_df.at["虧損總金額", "數值"] = loss_profit
    KPI_df.at["獲利因子", "數值"] = profit_factor
    KPI_df.at["平均獲利金額", "數值"] = avg_win_profit
    KPI_df.at["平均虧損金額", "數值"] = avg_loss_profit
    KPI_df.at["賺賠比", "數值"] = profit_rate
    KPI_df.at["最大單筆獲利", "數值"] = max_profit
    KPI_df.at["最大單筆虧損", "數值"] = max_loss
    KPI_df.at["MDD", "數值"] = MDD
    return KPI_df

def main(stock_id=3711, period="12mo"):
    df=get_MA(stock_id, period) #取得資料
    df=trade(df)    #交易
    result_text=get_KPI(df)
    
    return df, result_text
    print(df)
            
if __name__ == "__main__":
    main()