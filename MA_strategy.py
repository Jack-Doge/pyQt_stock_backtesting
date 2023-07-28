# -*- coding: utf-8 -*-
"""
Created on Mon May  2 14:24:53 2022

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
    df["MA5"]=talib.SMA(df["收盤價"],5)
    df["MA20"]=talib.SMA(df["收盤價"],20)
    
    #MA5和MA20的交叉
    df["diff"]=df["MA5"]-df["MA20"]
    # MA5>MA20
    df["upper_lower"]=df["diff"]>0
    
    df["last_upper_lower"]=df["upper_lower"].shift(-1) #　前一天的狀態
    df["sign"]=df["last_upper_lower"]!=df["upper_lower"] # 判斷是否與前一天狀態一樣
    
    # print(df)
    return df

def trade(df):
    df["Buy"] = None
    df["Sell"] = None
  
    last_index = df.index[-1]
    hold = 0 # 是否持有
    for index, row in df.copy().iterrows():
        # 最後一天不交易，並將部位平倉
        if index == last_index: 
            if hold == 1: # 若持有部位，平倉
                  df.at[index, "Sell"] = row["收盤價"] # 紀錄賣價
                  hold = 0
            break # 跳出迴圈
      
        # 與前一天的狀態不一樣，今天的MA5比MA10高，沒有持有股票，符合以上條件買入
        if not(row["sign"]) and row["upper_lower"] and hold == 0:
            df.at[index, "Buy"] = row["收盤價"] # 記錄買價
            hold = 1
            # 與前一天的狀態不一樣，今天的MA5比MA10低，有持有股票，符合以上條件賣出
        elif not(row["sign"]) and not(row["upper_lower"]) and hold == 1:
            df.at[index, "Sell"] = row["收盤價"] # 紀錄賣價
            hold = 0
  
    return df

def main(stock_id, period):
    df=get_MA(stock_id, period) #取得資料
    df=trade(df)    #交易
    KPI_df=get_KPI(df)
    
    return df, KPI_df