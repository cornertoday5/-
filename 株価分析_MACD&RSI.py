from pandas_datareader.stooq import StooqDailyReader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 証券コード、開始、終了区間、RSI領域
company_code = '7867.JP'
start = '2020-04-01'
end = '2024-04-01'
rsi_upper = 65
rsi_lower = 35

# データフレーム作成
stooq = StooqDailyReader(company_code, start, end)
df = stooq.read()

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    
    # Calculate RSI
    rsi = calculate_rsi(data)
    
    # Create Buy and Sell signals
    data['Buy_Signal'] = np.where((macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1)) & (rsi < rsi_lower), 1, 0)
    data['Sell_Signal'] = np.where((macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1)) & (rsi > rsi_upper), -1, 0)
        
    return macd_line, signal_line, macd_histogram, data, rsi

# Function to calculate RSI
def calculate_rsi(data, window=25):
    data['Price Change'] = data['Close'].diff()
    data['Gain'] = np.where(data['Price Change'] > 0, data['Price Change'], 0)
    data['Loss'] = np.where(data['Price Change'] < 0, abs(data['Price Change']), 0)
    
    avg_gain = data['Gain'].rolling(window=window, min_periods=1).mean()
    avg_loss = data['Loss'].rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    data['MA'] = data['Close'].rolling(window=window, min_periods=1).mean()
    data['Upper'] = data['MA'] + num_std_dev * data['Close'].rolling(window=window, min_periods=1).std()
    data['Lower'] = data['MA'] - num_std_dev * data['Close'].rolling(window=window, min_periods=1).std()
    
    return data

# Function to calculate Stochastics
def calculate_stochastics(data, k_window=14, d_window=3):
    lowest_low = data['Low'].rolling(window=k_window, min_periods=1).min()
    highest_high = data['High'].rolling(window=k_window, min_periods=1).max()
    
    data['%K'] = ((data['Close'] - lowest_low) / (highest_high - lowest_low)) * 100
    data['%D'] = data['%K'].rolling(window=d_window, min_periods=1).mean()
    
    return data

# Calculate MACD indicators
macd_line, signal_line, macd_histogram, df, rsi = calculate_macd(df)

# Calculate Bollinger Bands
df = calculate_bollinger_bands(df)

# Calculate Stochastics
df = calculate_stochastics(df)

# Plotting the MACD, RSI, Bollinger Bands, and Stochastics charts
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(12, 16), sharex=True)

# Plotting price chart on the first subplot
ax1.plot(df.index, df['Close'], label='Close Price', color='blue')
ax1.scatter(df.index[df['Buy_Signal'] == 1], df['Close'][df['Buy_Signal'] == 1], marker='^', color='g', label='Buy Signal')
ax1.scatter(df.index[df['Sell_Signal'] == -1], df['Close'][df['Sell_Signal'] == -1], marker='v', color='r', label='Sell Signal')
ax1.set_ylabel('Price')
ax1.legend(loc='upper left')

# Plotting MACD indicators on the second subplot
ax2.plot(df.index, macd_line, label='MACD Line', color='orange')
ax2.plot(df.index, signal_line, label='Signal Line', color='green')
ax2.fill_between(df.index, macd_histogram, label='MACD Histogram', color='grey', alpha=0.5)
ax2.hlines(0, df.index[0], df.index[-1], 'grey', linestyles='dashed')
ax2.set_ylabel('MACD')
ax2.legend(loc='upper left')

# Plotting RSI on the third subplot
ax3.plot(df.index, rsi, label='RSI (25 days)')
ax3.axhline(y=50, color='grey', linestyle='-', label='50')
ax3.axhline(y=rsi_upper, color='r', linestyle='--', label='Overbought(' + str(rsi_upper) + ')')
ax3.axhline(y=rsi_lower, color='g', linestyle='--', label='Oversold(' + str(rsi_lower) + ')')
ax3.set_ylabel('RSI')
ax3.legend(loc='upper left')

# Plotting Bollinger Bands on the fourth subplot
ax4.plot(df.index, df['Close'], label='Close Price', color='blue')
ax4.plot(df.index, df['MA'], label='Moving Average', color='black', linestyle='--')
ax4.fill_between(df.index, df['Upper'], df['Lower'], color='grey', alpha=0.3)
ax4.set_ylabel('Bollinger Bands')
ax4.legend(loc='upper left')

# Plotting Stochastics on the fifth subplot
ax5.plot(df.index, df['%K'], label='%K', color='purple')
ax5.plot(df.index, df['%D'], label='%D', color='pink')
ax5.hlines(80, df.index[0], df.index[-1], 'r', linestyles='dashed', label='Overbought (80)')
ax5.hlines(20, df.index[0], df.index[-1], 'g', linestyles='dashed', label='Oversold (20)')
ax5.set_xlabel('Date')
ax5.set_ylabel('Stochastics')
ax5.legend(loc='upper left')

# Show the plot
plt.show()
