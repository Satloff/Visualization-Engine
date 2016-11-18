import numpy as np
import matplotlib.pyplot as plt

plt.hist(matrix1, bins = 1000, normed = 0)
ax = plt.subplot(111)
ax.set_xlabel('X')
ax.set_xlim(3,7)
