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
    file_path = Path(f"/home/neko/Projects/deepseek_harness_ws/stock-direction-app/backend/tests/bao_data/{code}_k_daily-{start_date}_{end_date}.csv")
    print(f"code: {code}, start_date: {start_date}, end_date: {end_date}")
    df = pd.read_csv(file_path)
    print(df.tail(5))

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

        recent_low_10d = df.tail(10)['low']
        print(recent_low_10d)
        print(f'recent low (10d):,mean: {recent_low_10d.mean()}')
        recent_low_5d = df[-5:]['low']
        print(f'recent low (5d):, mean: {recent_low_5d.mean()}')
        recent_low_3d = df[-4:-1]['low']
        print(f'recent low (3d)p: mean: {recent_low_3d.mean()}')
        recent_low_3d = df[-3:]['low']
        print(f'recent low (3d): mean: {recent_low_3d.mean()}')

        recent_high_10d = df.tail(10)['high']
        print(recent_high_10d)
        print(f'recent high (10d):mean: {recent_high_10d.mean()}')
        recent_high_5d = df.tail(5)['high']
        print(f'recent high (5d):mean: {recent_high_5d.mean()}')
        recent_high_3d = df.tail(3)['high']
        print(f'recent high (3d): mean: {recent_high_3d.mean()}')


if __name__ == "__main__":
    #   main('sh.603353')  # 和顺石油
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