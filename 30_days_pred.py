#!/usr/bin/python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout

# Load the data from CSV
df = pd.read_csv('RELIANCE.csv')

# Drop rows with missing data
df = df.dropna()

# Scale the data
scaler = MinMaxScaler()
data = scaler.fit_transform(df['Close'].values.reshape(-1, 1))

# Split the data into training and testing sets
training_size = int(len(data) * 0.8)
train_data = data[:training_size]
test_data = data[training_size:]

# Define the input and output data for the model
def create_dataset(data, look_back=1):
    x, y = [], []
    for i in range(len(data) - look_back - 1):
        x.append(data[i:(i + look_back), 0])
        y.append(data[i + look_back, 0])
    #return np.array(x), np.array(y).reshape(-1, 1)
    return np.array(x), np.array(y)

look_back = 5
x_train, y_train = create_dataset(train_data, look_back)
x_test, y_test = create_dataset(test_data, look_back)

# Define the model
model = Sequential()
model.add(LSTM(64, input_shape=(look_back, 1), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(32, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(1, activation='linear'))
model.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=50, batch_size=32)

# Evaluate the model
train_score = model.evaluate(x_train, y_train, verbose=0)
test_score = model.evaluate(x_test, y_test, verbose=0)
print(f'Training loss: {train_score:.5f}')
print(f'Testing loss: {test_score:.5f}')

# Make predictions on test data
y_pred = scaler.inverse_transform(model.predict(x_test))

# Predict the price for the next week
# Predict the price for the next week
last_predicted = data[-look_back:].reshape(1, look_back, 1)
predictions = []
for i in range(7):
    next_day_price = model.predict(last_predicted)
    last_predicted = np.append(last_predicted[:,1:,:], next_day_price.reshape(1, 1, 1), axis=1)
    predictions.append(next_day_price[0, 0])
    date = pd.to_datetime(df['Date'].iloc[-1]) + pd.DateOffset(days=1)
    new_row = {'Date': date.date(), 'Close': scaler.inverse_transform([[next_day_price]])[0][0]}
    df = df.append(new_row, ignore_index=True)

# Add predicted price to DataFrame
dates = pd.date_range(start=df['Date'].iloc[-1], periods=7, freq='D')[1:]
new_rows = pd.DataFrame({'Date': dates, 'Close': scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()})
df = pd.concat([df, new_rows], ignore_index=True)

# Convert Date column to string
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

# Plot the results
plt.figure(figsize=(16, 8))
predicted = np.empty_like(data)
predicted[:] = np.nan
predicted[-(len(y_pred)+7):-(7)] = y_pred.flatten()
plt.plot(df['Date'], scaler.inverse_transform(data), label='Actual')
plt.plot(df['Date'], predicted, label='Predicted')
for i in range(7):
    plt.plot(df['Date'][-7+i:], [None]*(7-i) + [df['Close'].iloc[-1-i]], label=f"Day {i+1}")
plt.title('Reliance Industries Limited Stock Price Prediction')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

