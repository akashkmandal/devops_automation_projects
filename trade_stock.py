#!/usr/bin/python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout

# Load the data from CSV
df = pd.read_csv('RELIANCE.csv')
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

# Plot the results
plt.figure(figsize=(16, 8))
plt.plot(df['Date'][training_size + look_back + 1:], df['Close'][training_size + look_back + 1:], label='Actual')
plt.plot(df['Date'][training_size + look_back + 1:], y_pred, label='Predicted')
plt.title('Reliance Industries Limited Stock Price Prediction')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

