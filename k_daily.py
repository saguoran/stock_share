from datetime import datetime, timedelta
from pdb import main
import sys

import baostock as bs
import pandas as pd
from pathlib import Path



def main(code = "sz.000059"):

    #### 结果集输出到csv文件 ####   
    end_date = datetime.now()
    start_date = end_date - pd.Timedelta(days=365*10)  # 过去一年的数据
    end_date = end_date.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")

    print(f"code: {code}, start_date: {start_date}, end_date: {end_date}")
    file_path = Path(f"/home/neko/Projects/deepseek_harness_ws/stock-direction-app/backend/tests/bao_data/{code}_k_daily-{start_date}_{end_date}.csv")
    file_path.parent.mkdir(parents=True, exist_ok=True)    
    df = None
    if (skip_query := file_path.exists()):
        df = pd.read_csv(file_path)
        if not df.empty:
            if "date" in df.columns:
                # check if the last date in the dataframe is equal to the end_date
                if df['date'].iloc[-1] == end_date:
                    print(f"Data for {code} is already up to date until {end_date}. Skipping query.")
                    skip_query = True
                    print(df.tail(5))
          
                

    if not skip_query:
        #### 登陆系统 ####
        lg = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:'+lg.error_code)
        print('login respond  error_msg:'+lg.error_msg)

        #### 获取沪深A股历史K线数据 ####
        # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        rs = bs.query_history_k_data_plus(code,
            "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST",
            start_date=start_date, end_date=end_date,
            frequency="d", adjustflag="3")
        print('query_history_k_data_plus respond error_code:'+rs.error_code)
        print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        df = pd.DataFrame(data_list, columns=rs.fields)

        #### 结果集输出到csv文件 ####   
        df.to_csv(file_path, index=False)
        print(df)

        #### 登出系统 ####
        bs.logout()

    # calculate mean price and volume
    if type(df) == pd.DataFrame and not df.empty:
        # 最大连续跌天数
        # df['consecutive_down_days'] = (df['close'].astype(float) < df['preclose'].astype(float)).astype(int).groupby((df['close'].astype(float) >= df['preclose'].astype(float)).cumsum()).cumsum()
        # # 最大连续涨天数
        # df['consecutive_up_days'] = (df['close'].astype(float) > df['preclose'].astype(float)).astype(int).groupby((df['close'].astype(float) <= df['preclose'].astype(float)).cumsum()).cumsum()
        # print(df.tail(5)[['date', 'close', 'preclose', 'consecutive_down_days', 'consecutive_up_days']])
        # df = df.sort_values('date').reset_index(drop=True)
        is_down = (df['close'].astype(float) < df['preclose'].astype(float)).fillna(False)
        streaks = is_down.groupby((~is_down).cumsum()).cumsum()
        max_down = int(streaks.max()) if not streaks.empty else 0
        print("max consecutive down days:", max_down)
        # 均价 中点
        df['mean_price'] = (df.high.astype(float) + df.low.astype(float)) / 2

        # 均价 
        df['mean_price1'] = df.amount.astype(float) / df.volume.astype(float)
        
        # 均量
        df['mean_volume5'] = df['volume'].astype(float).rolling(window=5).mean()  # 5-day rolling mean
        # 压力位
        df['resistance5'] = df['mean_price'] + 2 * df['mean_price'].rolling(window=5).std()
        # 支撑位
        df['support5'] = df['mean_price'] - 2 * df['mean_price'].rolling(window=5).std()
        print(df.tail(5))
        file_path = Path(f"/home/neko/Projects/deepseek_harness_ws/stock-direction-app/backend/tests/bao_data/{code}_k_daily-{start_date}_{end_date}_analysis.csv")
        file_path.parent.mkdir(parents=True, exist_ok=True)    
        df.to_csv(file_path, index=False)
        print(df.tail(5)[['date', 'open', 'close', 'low','high', 'pctChg', 'amount', 'volume']])
        print(df.tail(5)[['date',  'mean_price', 'mean_price1', 'mean_volume5', 'resistance5', 'support5']])
    
if __name__ == "__main__":
    # main('sh.603353')  # Example stock code for testing
    # main('sz.000938')  # 紫光股份
    # main('sz.002716')  # 湖南白银
    main('SZ.002378')  # 章源钨业
    # print("Starting k_daily.py script...", sys.argv)
    # if len(sys.argv) != 2:
    #     print("Usage: python3 k_daily.py <stock_code>")
    # else:
    #     code = sys.argv[1]
    #     # Call the main logic with the provided stock code
    #     main(code)