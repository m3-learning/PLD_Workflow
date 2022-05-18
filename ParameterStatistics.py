import ast
import re
import pandas as pd
import hvplot.pandas

def PlotParameter(df_api, ls_resp, parameter):
    '''
    This function is designed to plot the parameter change with time.

    :param ls_resp: collectionItemsList
    :type ls_resp: collectionItemsList

    :param parameter: PLD experiment parameter to track and plot 
    :type parameter: str
    '''
    
    time_stamp_list, metric_list = [], []

    for i in range(len(ls_resp[0].item)):

        id = ls_resp[0].item[i].id
        labels = ast.literal_eval(df_api.dataView(id)[0].data[0].metadata)
        
        if 'target_1' not in labels.keys(): continue
            
        if parameter in labels['target_1'].keys():
            metric = labels['target_1'][parameter]
        else:
            metric = 0

        if metric != 0:
            metric = float(re.split('/', metric)[-1])
            date = labels['header']['Date']    
            time_stamp = date[-4:]+'-'+date[:2]+'-'+date[3:5]

            if 'time' in labels['header'].keys():
                time = labels['header']['time']
                time_stamp = date + ' ' + time

            time_stamp_list.append(time_stamp)
            metric_list.append(metric)
            
    df = pd.DataFrame({
                   'Date': time_stamp_list,
                    parameter: metric_list
                  })

    df = df.set_index(pd.DatetimeIndex(df.iloc[:,0]))
    df.drop('Date', 1, inplace=True)
    display(df.hvplot.scatter())
    return df