# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 16:32:34 2022

@author: karta
"""

import talib
import pandas as pd
import yF_Kbar

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
    df["Buy"]=pd.NA
    df["Sell"]=pd.NA
    
    df["RSI_5"]=talib.RSI(df["收盤價"], 5) #計算RSI
    df["RSI_5_T1"]=df["RSI_5"].shift(1) #前一日RSI
    df["RSI_5_T2"]=df["RSI_5"].shift(2) #前兩日RSI
    
    df["DI"]=talib.PLUS_DI(df["最高價"], df["最低價"], df["收盤價"]) #計算DI
    df["DI_T1"]=df["DI"].shift(1) #前一日DI
    df["DI_T2"]=df["DI"].shift(2) #前兩日DI

    df["SMA_5"]=talib.SMA(df["收盤價"],5) #計算SMA5
    df["SMA_5_T1"]=df["SMA_5"].shift(1) #前1日的SMA5
    df["SMA_5_T2"]=df["SMA_5"].shift(2) #前2日的SMA5
    
    df["SMA_20"]=talib.SMA(df["收盤價"],20) #計算SMA20
    df["SMA_20_T1"]=df["SMA_20"].shift(1) #前1日的SMA20

    #設定MACD的參數
    fastperiod=12
    slowperiod=26
    signalperiod=9
    
    # DIF = EMA_12 - EMA_26 (快線)
    # MACD = DIF值取EMA_9 (慢線)
    # hist = 快線 - 慢線 (柱狀圖)
    df["DIF"], df["MACD"], df["hist"]=talib.MACD(df["收盤價"],
                                                 fastperiod=fastperiod,
                                                 slowperiod=slowperiod,
                                                 signalperiod=signalperiod)
    
    return df

def trade(df):
    df["Buy"] = None
    df["Sell"] = None
  
    last_index = df.index[-1]
    hold = 0 # 是否持有
    #foreach每個row
    for index, row in df.copy().iterrows():
        # 最後一天不交易，並將部位平倉
        if index == last_index: 
            if hold == 1: # 若持有部位，平倉
                  df.at[index, "Sell"] = row["收盤價"] # 紀錄賣價
                  hold = 0
            break # 跳出迴圈
        #買進條件
        #買進條件1 前一日+DI<=前兩日+DI 且 前一日+DI<今日+DI
        #買進條件2 今日SMA20>前一日SMA20
        #買進條件3 今日+DI<33
        buy_condition_1=(row["DI_T1"]<=row["DI_T2"]) and (row["DI_T1"]<row["DI"])
        buy_condition_2=row["SMA_20"]>row["SMA_20_T1"]
        buy_condition_3=row["DI"]<33
        
        #賣出條件
        #賣出條件1 前一日SMA5>=前二日SMA5 and 前一日SMA5>今日SMA5
        #賣出條件2 今日DIF<0
        sell_condition_1=(row["SMA_5_T1"]>=row["SMA_5_T2"]) and (row["SMA_5_T1"]>row["RSI_5"])
        sell_condition_2=row["DIF"]<0
        
        #符合兩個買進條件，沒有持股就買入
        if(buy_condition_1 and buy_condition_2 and buy_condition_3) and hold==0:
            df.at[index, "Buy"]=row["收盤價"]  #記錄買價
            hold=1 #持股
        #符合兩個賣出條件，有持股就賣出
        elif(sell_condition_1 and sell_condition_2) and hold==1:
            df.at[index, "Sell"]=row["收盤價"]  #記錄賣價
            hold=0 #持股
    return df


def main(stock_id=3711, period="12mo"):
    df=get_MA(stock_id, period) #取得資料
    df=trade(df)    #交易
    KPI_df=get_KPI(df)
    
    return df, KPI_df
    print(df)

if __name__ == "__main__":
    main()