'''
Created on Sep 26, 2014

@author: ayan

This is the script that actually got used for data analysis.
'''
import calendar
from datetime import date
import pandas as pd
import numpy as np
from plotly.graph_objs import *
# from matplotlib.pylab import plt, gcf


def get_month_range(series, year_col, month_col):
    month_reverse = {v: k for k,v in enumerate(calendar.month_abbr)}
    year_val = int(series[year_col])
    year_month_str = str(series[month_col])
    month_val = month_reverse[year_month_str]
    month_range = calendar.monthrange(year_val, month_val)
    last_date = month_range[1]
    month_end_date = date(year_val, month_val, last_date)
    return month_end_date


def di_pct_sum(series, d_0, d_1, d_2, d_3, d_4):
    d_0_val = series[d_0]
    d_1_val = series[d_1]
    d_2_val = series[d_2]
    d_3_val = series[d_3]
    d_4_val = series[d_4]
    pct_sum = d_0_val + d_1_val + d_2_val + d_3_val + d_4_val
    return pct_sum
    

def state_di_avg(series, d_0, d_1, d_2, d_3, d_4):

    d_0_val = series[d_0] / 100
    d_1_val = series[d_1] / 100
    d_2_val = series[d_2] / 100
    d_3_val = series[d_3] / 100
    d_4_val = series[d_4] / 100
    state_avg = (0*d_0_val + 1*d_1_val + 2*d_2_val + 3*d_3_val + 4*d_4_val)
    return state_avg


def report_month(series, date_col):
    date_val = series[date_col]
    month_val = date_val.strftime('%m')
    return int(month_val)

  
def year_str(series, year_col):
    year_val = int(series[year_col])
    return '{0}'.format(year_val)


def prep_data():
    # Traditional Drought Index
    TDI_DATA = 'data\\drought\\traditional_drought_index.csv'
    df_tdi = pd.read_csv(TDI_DATA, sep=',', skiprows=1, header=0, parse_dates=['Week'], comment='#', index_col='Week')
    df_severe = df_tdi[['D2-D4']]
    di_str = 'Percent of CA in Severe Drought'
    df_tdi_2007_2014 = df_severe[(df_severe.index >= '2007-01-01') & (df_severe.index < '2014-09-01')] # get data from 2007 to present
    df_tdi_2007_2014_rs = df_tdi_2007_2014.resample('M')
    df_tdi_2007_2014_rs['date'] = df_tdi_2007_2014_rs.index
    df_tdi_2007_2014_rs.columns = [di_str, 'date']
    
    # produce prices
    produce_items = ['navel_oranges', 'lemons', 'lettuce', 'grapes', 'tomatoes']
    dfs = {}
    dfs_ri = {}
    for produce_item in produce_items:
        csv_path = 'data/produce/{0}.csv'.format(produce_item)
        df = pd.read_csv(csv_path, sep=',', quotechar='"', skiprows=8, header=0, index_col=0)
        df_produce = df.loc[2007:]
        dfs[produce_item] = df_produce
        df_stack = df_produce.stack()
        df_stack_ri = df_stack.reset_index()
        column_name = '{0} Avg Price'.format(produce_item.title())
        df_stack_ri.columns = ('year', 'month', column_name)
        df_stack_ri['date'] = df_stack_ri.apply(get_month_range, axis=1, year_col='year', month_col='month')
        df_stack_ri['date'] = df_stack_ri[['date']].astype(np.datetime64)
        df_stack_filtered = df_stack_ri[['date', column_name]]
        dfs_ri[produce_item] = df_stack_filtered
    df_lemon = dfs_ri['lemons']
    df_orange = dfs_ri['navel_oranges']
    df_lettuce = dfs_ri['lettuce']
    df_grapes = dfs_ri['grapes']
    df_tomato = dfs_ri['tomatoes']
    df_lemon_orange = pd.merge(df_lemon, df_orange, how='inner', on='date')
    df_lo_grapes = pd.merge(df_lemon_orange, df_grapes, how='inner', on='date')
    df_log_tom = pd.merge(df_lo_grapes, df_tomato, how='inner', on='date')
    df_produce = pd.merge(df_log_tom, df_lettuce, how='inner', on='date')
    df_di = df_tdi_2007_2014_rs[['date', di_str]]
    df_di_produce = pd.merge(df_produce, df_di, how='inner', on='date')
    df_di_produce['mon_int'] = df_di_produce.apply(report_month, axis=1, date_col='date')
    df_di_produce.index = df_di_produce['date']
    # average over identical timeframes each year
    start_month = 6
    end_month = 8
    df_di_produce_timeframe = df_di_produce[(df_di_produce['mon_int'] >= start_month) & (df_di_produce['mon_int'] <= end_month)] # filter to subset months
    grouper_year = pd.TimeGrouper('A')
    df_avg = df_di_produce_timeframe.groupby(grouper_year).mean()
    df_avg['year'] = df_avg.index.year
    # tf_string = 'month_{0}_through_{1} (year)'.format(start_month, end_month)
    tf_string = 'year_str'
    df_avg[tf_string] = df_avg.apply(year_str, axis=1, year_col='year')
    pertinent_columns = ['Lemons Avg Price', 'Navel_Oranges Avg Price', 'Lettuce Avg Price', 'Grapes Avg Price', 'Tomatoes Avg Price', di_str, tf_string]
    df_tf_avg = df_avg[pertinent_columns]
    # df_tf_avg.plot(kind='scatter', y=['Lemons Avg Price', 'Navel_Oranges Avg Price', 'Lettuce Avg Price'], 
    #                   x=[di_str]*3, color=['blue', 'red', 'green'], label=['lemon', 'orange', 'lettuce'])
    # title = 'Produce Price vs Percent Severe Drought'
    # plt.xlabel('Percent of CA experiencing severe drought')
    # plt.ylabel('Price (USD/lb)')
    # plt.legend(loc='best')
    # plt.title(title)
    # fig = gcf()
    # fig.set_size_inches(18.5, 14.5)
    # plot_name = 'price_vs_drought_index'
    # figure_name = 'plots/{0}.png'.format(plot_name)
    # fig.savefig(figure_name)
    df_tf_avg.to_csv('data/ca_price_vs_pct_severe_di.csv', index=False)
    print('Done!') 
    
    return df_tf_avg


def calc_anomoly(series, column_name, avg_value):
    produce_value = series[column_name]
    anomoly = produce_value - avg_value
    return anomoly


def convert_str_to_float(series, column_name):
    str_value = series[column_name]
    float_value = float(str_value)
    return float_value


def df_to_plotly(df, y_axis, x_axis='Percent of CA in Severe Drought'):
    
    x_values = df[x_axis].values
    y_values = df[y_axis].values
    data_dict = {
                 'x': x_values.tolist(),
                 'y': y_values.tolist(),
                 'name': y_axis
                 }
    return data_dict


if __name__ == '__main__':
    """
    # Drought Index
    DI_DATA = 'data\\drought\\drought_index_data_ca.csv'
    df = pd.read_csv(DI_DATA, sep=',', skiprows=2, header=0, parse_dates=['Week'], comment='#', index_col='Week')
    di_str = 'State Avg Drought Index'
    df_1 = df[['0', '1', '2', '3', '4']]
    df_1[di_str] = df_1.apply(state_di_avg, axis=1, d_0='0', d_1='1', d_2='2', d_3='3', d_4='4')
    df_1['Pct Sum'] = df_1.apply(di_pct_sum, axis=1, d_0='0', d_1='1', d_2='2', d_3='3', d_4='4')
    df_ds = df_1.resample('M') # downsample to Months
    df_2007 = df_ds[(df_ds.index > '2007-01-01') & (df_ds.index < '2014-09-01')]
    df_2007['date'] = df_2007.index
    """
    df = prep_data()
    print(df)