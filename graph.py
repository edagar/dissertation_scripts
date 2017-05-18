import matplotlib.pyplot as plt
import pandas as pd

print("hehe")

data = pd.read_csv('data.csv', sep=',',header=0, index_col = 1)

data.plot(kind='bar')
plt.ylabel('Frequency')
plt.xlabel('numpackets')
plt.title('Title')

plt.show()
