from random import sample

import tensorflow as tf
import pandas as pd
import numpy as np
from keras import Sequential
from keras.src.layers import Dense

#location: 1- city; 2- country
Data = {
    'bedrooms': [3,4,2,5],
    'bathrooms': [2,3,1,4],
    'sq_meters': [60,80,32,110],
    'location': [1,2,1,2],
    'price': [600000, 550000, 450000, 700000]
}

df = pd.DataFrame(Data)

X = df[['bedrooms', 'bathrooms', 'sq_meters', 'location']]
y = df[['price']]

model = Sequential()

model.add(Dense(units=64, activation='relu', input_shape=(4,)))
model.add(Dense(units=32, activation='relu'))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

model.fit(X, y, epochs=100, batch_size=1)

sample_in = np.array([[ 3, 2, 60, 1]])

prediction = model.predict(sample_in)

print()
print(f"Predicted price: {prediction[0][0]*100} zl")