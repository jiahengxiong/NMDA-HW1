import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load data from the 'rtt_distance.csv' file into a Pandas DataFrame
data = pd.read_csv('rtt_distance.csv', header=0)

# Clean the 'distance' column by removing ' km' and converting to float
data['distance'] = data['distance'].str.replace(' km', '').astype(float)

# Sort the data based on the 'distance' column
data.sort_values('distance', inplace=True)

# Fit a linear regression model to the data
coefficients = np.polyfit(data['distance'], data['avg_rtt'], 1)
polynomial = np.poly1d(coefficients)

# Predict the y values using the fitted line
y_pred = polynomial(data['distance'])

# Plotting
fig = plt.figure()

# Plot the actual data points
plt.plot(data['distance'], data['avg_rtt'], '--r', label='Average RTT plot')
plt.scatter(data['distance'], data['avg_rtt'], color='red', s=5)

# Plot the fitted line
plt.plot(data['distance'], y_pred, '-b', label='Fitted Line')

# Adding labels and title
plt.title('Average RTT vs Distance')
plt.xlabel('Distance (km)')
plt.ylabel('RTT (ms)')

# Adding legend with customization
plt.legend(
    loc='best',
    handlelength=2.5,
    handletextpad=0.1,
    labelspacing=0.1,
    borderaxespad=0.1,
    fontsize='medium',
    framealpha=0
)

# Display grid for better readability
plt.grid(visible=True, color='gray', linewidth=0.5)

# Save the plot as an image file
plt.savefig('rtt_distance.png', dpi=2000)

# Display the plot
plt.show()

# Print the coefficient of the linear regression model
print(f"The RTT per distance is: {coefficients[0]}")

# Comments: The plot represents the relationship between the average RTT and distance. What I used here have 323 IP
# addresses with the corresponding RTT since some of the IP addresses don't response. RTT and distance are sorted
# according to the geographic distances between the virtual ip address and target ip address from near to far.
# Intuitively, the RTT should grow with the increments of the distance. This can be seen from the plot.

# As for the linear approximation. Since it's a function of the RTT and distance -- RTT = 2(L/C + d/v) + n And L/C
# represents the packets transmission time which can be ignored compare with the real transmitting time in the
# network. So simplified formula is RTT = 2(1/v)+n/d, after calculating the RTT per km is around 18.63 ms/km. Compare
# with the real situation While the linear fit is not an exact representation of the relationship between distance
# and RTT, it provides a useful estimate of how these two variables are related. In this case, the linear fit shows
# that there is a positive relationship between distance and RTT, which is consistent with our intuition. As the
# distance between the virtual IP address and the target IP address increases, the RTT also tends to increase. But we
# know that maybe there are some delays in the real case. The physical distance between the sender and receiver is
# the main reason that affects the RTT. Others are the transmission medium network traffic .
