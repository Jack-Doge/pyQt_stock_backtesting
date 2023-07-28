# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 23:22:40 2022

@author: karta
"""

import talib
import pandas as pd
import yF_Kbar

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
    
    #RSI
    df["RSI_5"]=talib.RSI(df["收盤價"], 5) #計算RSI
    df["RSI_5_T1"]=df["RSI_5"].shift(1) #前一日RSI
    df["RSI_5_T2"]=df["RSI_5"].shift(2) #前兩日RSI
    #+DI(14 日上升方向線)
    df["+DI"]=talib.PLUS_DI(df["最高價"], df["最低價"], df["收盤價"],14) #計算+DI
    df["+DI_T1"]=df["+DI"].shift(1) #前一日+DI
    df["+DI_T2"]=df["+DI"].shift(2) #前兩日+DI
    #-DI(14 日下跌方向線)
    df["-DI"]=talib.MINUS_DI(df["最高價"], df["最低價"], df["收盤價"],14) #計算-DI
    df["-DI_T1"]=df["-DI"].shift(1) #前一日-DI
    df["-DI_T2"]=df["-DI"].shift(2) #前兩日-DI
    #ADX(14 日趨向平均線)
    df["ADX"]=talib.ADX(df["最高價"], df["最低價"], df["收盤價"],14) #計算ADX
    df["ADX_T1"]=df["ADX"].shift(1) #前一日ADX
    df["ADX_T2"]=df["ADX"].shift(2) #前兩日ADX
    #ADXR(14 日趨向平均線之評估數值)
    df["ADXR"]=talib.MINUS_DI(df["最高價"], df["最低價"], df["收盤價"],14) #計算ADXR
    df["ADXR_T1"]=df["ADXR"].shift(1) #前一日ADXR
    df["ADXR_T2"]=df["ADXR"].shift(2) #前兩日ADXR
    
    #SMA(均線)
    df["SMA_3"]=talib.SMA(df["收盤價"],3) #計算SMA3
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
    df["DIF_T1"]=df["DIF"].shift(1) #前一日DIF
    df["DIF_T2"]=df["DIF"].shift(2) #前一日DIF
    
    df["OSC"]=df["DIF"]-df["MACD"]
    df["OSC_T1"]=df["OSC"].shift(1) #前一日OSC
    df["OSC_T2"]=df["OSC"].shift(2) #前兩日OSC
    #KD(隨機)
    df["K"],df["D"]=talib.STOCH(df["最高價"], df["最低價"], df["收盤價"])
    df["K_T1"]=df["K"].shift(1) #前一日K
    df["K_T2"]=df["K"].shift(2) #前兩日K
    df["D_T1"]=df["D"].shift(1) #前一日D
    df["D_T2"]=df["D"].shift(2) #前兩日D
    #J
    df["J"]=list(map(lambda x,y:3*x-2*y,df["K"],df["D"]))
    df["J_T1"]=df["J"].shift(1) #前一日J
    df["J_T2"]=df["J"].shift(2) #前兩日J
    
    #Bollinger Bands(布林)
    df["upperband"], df["middleband"], df["lowerband"] = talib.BBANDS(df["收盤價"])
    #%b
    df["%b"]=((df["收盤價"]-df["lowerband"])/(df["upperband"]-df["lowerband"]))*100
    df["%b_T1"]=df["%b"].shift(1) #前一日%b
    df["%b_T2"]=df["%b"].shift(2) #前兩日%b
    
    #var(變異數)
    df["VAR_5"]=talib.VAR(df["收盤價"],5)
    df["VAR_5_T1"]=df["VAR_5"].shift(1) #前一日VAR_5
    df["VAR_5_T2"]=df["VAR_5"].shift(2) #前兩日VAR_5
    df["VAR_10"]=talib.VAR(df["收盤價"],10)
    df["VAR_10_T1"]=df["VAR_10"].shift(1) #前一日VAR_10
    df["VAR_10_T2"]=df["VAR_10"].shift(2) #前兩日VAR_10
    
    #std(標準差)
    df["STD_3"]=talib.STDDEV(df["收盤價"], timeperiod=3, nbdev=1)
    df["STD_5"]=talib.STDDEV(df["收盤價"], timeperiod=5, nbdev=1)
    
    #SAR
    df["SAR"]=talib.SAR(df["最高價"],df["最低價"])
    
    #MFI
    df["MFI"]=talib.MFI(df["最高價"],df["最低價"],df["收盤價"],df["交易量"], timeperiod=14)
    df["MFI_T1"]=df["MFI"].shift(1)
    df["MFI_T2"]=df["MFI"].shift(2)
    
    return df