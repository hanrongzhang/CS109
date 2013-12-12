import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('all_data.csv')
grouped = df.groupby('source')
labels = [i for i in grouped.count()['source'].index]
values = [i for i in grouped.count()['source']]
index = np.arange(len(labels))
plt.bar(index, values)
plt.xticks(index+0.5, labels,rotation='vertical', fontsize=8)
plt.subplots_adjust(bottom=0.20)

plt.show()