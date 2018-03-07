import requests
import pandas as pd

while True:
    try:
        columns_number = int(input("Enter number of columns: "))*-1
        break
    except:
        print("Please enter an integer\n")

#global timeframe,steps,shift,token,headers,url,symbols,count
timeframe = "H1"
steps = [100,50]
shift =0
count = 1000

token="your token here"
headers = {"Authorization": "Bearer %s"%token}
url = 'https://api-fxtrade.oanda.com/v1/candles'

symbols = ["JP225_USD", "US30_USD", "HK33_HKD", "CN50_USD", "DE30_EUR"]

def get_candles(instrument):
    params = {"instrument": instrument, "granularity":timeframe,"count":count}
    try: response = requests.get(url, headers=headers, params=params)
    except: print("Comunication error")
    candles = response.json()['candles']
    df = pd.DataFrame(candles)
    df = df[['lowBid','highBid']]//1-shift
    df = df.astype(int)
    df['highBid'] = df['highBid'].apply(lambda x:x//step*step)
    df['lowBid'] = df['lowBid'].apply(lambda x:(x//step+1)*step)
    return(df)

def pf_chart(dataframe):
    chart = pd.DataFrame(index=reversed(list(range(dataframe.values.min(),dataframe.values.max()+step,step))))
    last = [0,'',0]
    lastLow = dataframe.loc[0,'lowBid']
    lastHigh = dataframe.loc[0,'highBid']

    for i in range(1,len(dataframe)):
        low = dataframe.loc[i,'lowBid']
        high = dataframe.loc[i,'highBid']
        if last[0] == 0:
            if high > lastHigh and low < lastLow:
                lastHigh = high
                lastLow = low
                continue
            elif high > lastHigh:
                #chart[1] = ''
                last[1] = 'X' 
                for p in range(lastLow,high+step,step):
                    chart.loc[p,1] = 'X'
                    last[2]+=1
                lastHigh = high
                last[0]+=1
            elif low < lastLow:
                #chart[1]=''
                last[1] = 'O'
                for p in range(low,lastHigh+step,step):
                    chart.loc[p,1] = 'O'
                    last[2]+= 1
                lastLow = low
                last[0]+= 1
        else:
            if last[1] == 'X':
                if high > lastHigh:
                    for p in range(lastHigh+step,high+step,step):
                        chart.loc[p,last[0]] = 'X'
                        last[2]+= 1
                    lastHigh = high
                elif low < lastHigh-2*step:
                    last[0]+= 1
                    #chart[last[0]]=''
                    last[1] = 'O'
                    last[2] = 0
                    for p in range(low,lastHigh,step):
                        chart.loc[p,last[0]] = 'O'
                        last[2]+= 1
                    lastLow = low
            else:
                if low < lastLow:
                    for p in range(low,lastLow,step):
                        chart.loc[p,last[0]] = 'O'
                        last[2]+= 1
                    lastLow = low
                elif high > lastLow+2*step:
                    last[0]+= 1
                    #chart[last[0]]=''
                    last[1] = 'X'
                    last[2] = 0
                    for p in range(lastLow+step,high+step,step):
                        chart.loc[p,last[0]] = 'X'
                        last[2]+= 1
                    lastHigh = high
               
    chart = chart[chart.columns[columns_number:]].dropna(axis="index",how='all')
    chart.fillna("",inplace=True)
    chart[last[0]+1] = chart.index
    chart.loc[chart.index[0]+step]='.'
    chart.sort_index(inplace=True,ascending=False)
    return(chart)

if __name__ == "__main__":  
    for symbol in symbols:
        if symbol!=symbols[0]:
            input("press enter for next symbol...\n")
        print(symbol)
        for step in steps:
            my_dataframe = get_candles(symbol)
            my_chart = pf_chart(my_dataframe)
            
            print(my_chart.to_string(index=False,header=False))

