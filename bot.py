#!/usr/bin/env python3

 some informations:
#       minutes: m1, m5, m15 and m30,
#       hours: H1, H2, H3, H4, H6 and H8,
#       one day: D1,
#       one week: W1,
#       one month: M1.
#       
#       add number= to set number of period '!=10'
#       add columns=[''] to display only a column starting with the input

#data = con.get_candles('EUR/USD', period='D1')

from pylab import plt
plt.style.use('seaborn')

# Get historic from EUR USD JPY market

dataEURUSD = con.get_candles('EUR/USD', period='m15', number=100)
#dataEURUSD.plot(figsize=(10, 6), lw=0.8);
dataUSDJPY = con.get_candles('USD/JPY', period='m15', number=100)
dataEURJPY = con.get_candles('EUR/JPY', period='m15', number=100)

print(dataEURUSD)

# Subscribe to them

if con.is_connected() == True:
    if con.is_subscribed('EUR/USD') == False:
        con.subscribe_market_data('EUR/USD')
        print('Subscribed to EUR/USD')
    if con.is_subscribed('USD/JPY') == False:
        con.subscribe_market_data('USD/JPY')
        print('Subscribed to USD/JPY')
    if con.is_subscribed('EUR/JPY') == False:
        con.subscribe_market_data('EUR/JPY')
        print('Subscribed to EUR/JPY')
else:
    print('is_connected() return false')

print('Subscibed symbols: ')
print(con.get_subscribed_symbols())

con.close()