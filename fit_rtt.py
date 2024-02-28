import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv('../rtt_distance.csv', header=0)

data['distance'] = data['distance'].str.replace(' km', '').astype(float)

data.sort_values('distance', inplace=True)

coefficients = np.polyfit(data['distance'], data['avg_rtt'], 1)
polynomial = np.poly1d(coefficients)

y_pred = polynomial(data['distance'])

fig = plt.figure()

plt.plot(data['distance'], data['avg_rtt'], '--r', label='Average RTT')
plt.scatter(data['distance'], data['avg_rtt'], color='red', label='Average RTT', s=5)

plt.plot(data['distance'], y_pred, '-b', label='Fitted Line')

plt.title('Average RTT vs Distance Scatter Plot')
plt.xlabel('Distance (km)')
plt.ylabel('RTT (ms)')

plt.legend()
plt.grid(visible=True)

# 显示图表
plt.show()
