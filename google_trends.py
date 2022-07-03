from pytrends.request import TrendReq


def getRealtimeTrends():
    pytrend = TrendReq(hl='vi_VI')
    df = pytrend.trending_searches(pn='vietnam')
    # print(df)
    print(df.head(5).values.tolist())
    list_trend = []
    for i in df.head(5).values.tolist():
        # print(i)
        # print(i[0])
        list_trend.append(i[0])
    # print(list_trend)
    return list_trend

if __name__ == '__main__':
    getRealtimeTrends()
