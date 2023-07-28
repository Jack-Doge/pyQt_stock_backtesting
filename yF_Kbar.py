# -*- coding: utf-8 -*-
"""
Created on Mon May  2 14:29:43 2022

@author: karta
"""

import yfinance as yf
import mplfinance as fplt


def get_data( stock_id="2330", period="12mo" ):
    stock_id = str( stock_id ) + ".TW" # Yahoo Finance 的 代號為台灣的代號 + .TW
    data = yf.Ticker( stock_id ) # 抓取資料
    # 1mo = 1個月，max 可以把所有期間的資料都下載
    ohlc = data.history( period = period )

    ohlc = ohlc.loc[ :, ["Open", "High", "Low", "Close", "Volume"] ] # 選擇製圖需要欄位(開高低收量)
    
    # print(ohlc)

    return ohlc

def draw_candle_chart(stock_id,df):
    # 配合mplfinance更改欄位名稱
    df.rename(columns = {"開盤價" : "Open", 
               "最高價" : "High",
               "最低價" : "Low",
               "收盤價" : "Close",
               "交易量" : "Volume"}
              , inplace = True)
    
    # 調整圖表標示顏色
    mc = fplt.make_marketcolors(
                                up = 'tab:red',down = 'tab:green', # 上漲為紅，下跌為綠
                                wick = {'up':'red','down':'green'}, # 影線上漲為紅，下跌為綠
                                volume = 'tab:green', # 交易量顏色
                               )
    s = fplt.make_mpf_style( marketcolors = mc ) # 定義圖表風格
    
    fplt.plot(
                df, # 開高低收量的資料
                type = 'candle', # 類型為蠟燭圖，也就是 K 線圖
                style = s, # 套用圖表風格
                title = str(stock_id), # 設定圖表標題
                ylabel = 'Price ($)', # 設定 Y 軸標題
                volume = True,
                savefig='./stockImg/stock_{}_Kbar.png'.format(stock_id), # 儲存檔案
            )
    
if __name__ == "__main__":
    df = get_data()
    # 配合程式更改欄位名稱
    df.rename(columns = {"Open" : "開盤價", 
               "High" : "最高價",
               "Low" : "最低價",
               "Close" : "收盤價",
               "Volume" : "交易量"}
              , inplace = True)
    
    print(df)

    draw_candle_chart( 1101, df )