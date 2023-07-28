# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 14:11:18 2022

@author: karta
"""

import pandas as pd

def get_KPI(df):
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
    
    #總成本
    total_cost=(record_df["Buy"]+record_df["Buy_fee"]+record_df["Sell_fee"]+record_df["Sell_tax"]).sum()*1000
    
    #報酬率
    percent_profit=total_profit/total_cost*100
    
    # 成敗次數
    win_times = (record_df["profit"] >= 0).sum()
    loss_times = (record_df["profit"] < 0).sum()

    # 勝率
    if trade_time > 0:
        win_rate = win_times / trade_time*100
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
    KPI_df.at["投入成本", "數值"]= total_cost
    # KPI_df.at["報酬率", "數值"]= str(percent_profit)+"%"
    KPI_df.at["成功次數", "數值"] = win_times
    KPI_df.at["虧損次數", "數值"] = loss_times
    KPI_df.at["勝率", "數值"] = str(round(win_rate,3))+"%"
    KPI_df.at["獲利總金額", "數值"] = win_profit
    KPI_df.at["虧損總金額", "數值"] = loss_profit
    KPI_df.at["獲利因子", "數值"] = profit_factor
    KPI_df.at["平均獲利金額", "數值"] = round(avg_win_profit,3)
    KPI_df.at["平均虧損金額", "數值"] = round(avg_loss_profit,3)
    KPI_df.at["賺賠比", "數值"] = round(profit_rate,3)
    KPI_df.at["最大單筆獲利", "數值"] = max_profit
    KPI_df.at["最大單筆虧損", "數值"] = max_loss
    KPI_df.at["MDD", "數值"] = MDD
    
    return KPI_df