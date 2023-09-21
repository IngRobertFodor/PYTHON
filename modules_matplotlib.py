import matplotlib
from matplotlib import pyplot as plt


x = [1, 8, 3, 4, 5]
x_2 = [1.5, 8.5, 3.5, 4.5, 5.5]
y = ["a","b","c","d","e"]

# PLOT
plt.figure(figsize=(10,5))
plt.plot(x, y, "o", color="green", label = "Test_1", lw=2.7, ms=5)
plt.plot(x_2,y, "o--", color="blue", label = "Test_2", lw=1.5, ms=5)
plt.xlabel("Values")
plt.ylabel("Characters")
plt.title("My Table")
plt.legend(loc="upper left", fontsize="10")
plt.show()

xx = [1, 2, 3, 4, 5]
xx_2 = [1.5, 2.5, 5.5, 4.5, 5.5]
yy = ["a","b","c","d","e"]
fig, axes = plt.subplots(3, 2, figsize=(12,120))
ax_one = axes[0][0]
ax_one.plot(xx, yy, "o--", color="blue", lw=1.5, ms=5)
ax_one.set_xlabel("xx_2")
ax_one.set_ylabel("yy")
ax_six = axes[2][1]
ax_six.plot(xx_2, yy, "o--")
plt.show()