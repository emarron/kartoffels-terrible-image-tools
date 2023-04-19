import csv
import numpy as np

# Open CSV file for reading
from matplotlib import pyplot as plt

with open('output_normalized.csv', 'r') as f:
    reader = csv.reader(f)

    # Read header row to get column names
    header = next(reader)
    # Create dictionary from remaining rows
    my_dict = {}
    for row in reader:
        name = row[0]
        values = np.asarray([float(x) for x in row[1:]])
        my_dict[name] = values

# Print dictionary
print(my_dict)
count = 0
for key, values in my_dict.items():
    if np.any(abs(values) > 1):
        count += 1
print(count)

fig = plt.figure(figsize=(16, 16))
ax = fig.add_subplot(projection='3d')
for coords in my_dict.values():
    ax.scatter(abs(coords[0]), abs(coords[1]), abs(coords[2]))
ax.set_xlabel('Average(R - G) / Brightness')
ax.set_ylabel('Average(R - B) / Brightness')
ax.set_zlabel('Average(G - B) / Brightness')
ax.grid(True, which='major')
# given that this is sort of unintelligible
plt.title("NORMALIZED |Average(Channel_G - Channel_B)| over |Average(Channel_R - Channel_B)| over |Average(Channel_R - Channel_G)|")
plt.show()
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
for coords in my_dict.values():
    #if np.all(abs(coords) > 0):
    ax1.scatter(abs(coords[0]), abs(coords[1]))
    ax2.scatter(abs(coords[0]), abs(coords[2]))
ax1.set_xlabel('Average(R - G)/ Brightness')
ax1.set_ylabel('Average(R - B) / Brightness')
ax2.set_xlabel('Average(R - G) / Brightness')
ax2.set_ylabel('Average(G - B) / Brightness')
ax1.grid(True, which='major')
ax2.grid(True, which='major')
ax1.set_title("NORMALIZED |Average(Channel_R - Channel_B)| over |Average(Channel_R - Channel_G)|")
ax2.set_title("NORMALIZED |Average(Channel_G - Channel_B)| over |Average(Channel_R - Channel_G)|")
plt.show()

# R,G,B = Red, Blue, Green
# channel cases:
# S: All R,G,B intensity values are the same (inside their own channel)
# S_R: All R intensity values are the same, but R and G are not
# S_G: All G intensity values are the same, but R and B are not
# S_B: All B intensity values are the same, but R and G are not
# S_RG: All R and G intensity values are the same, but B is not
# S_RB: All R and B intensity values are the same, but G is not
# S_GB: All G and B intensity values are the same, but R is not
# NS: Not any of the above cases.
#
# X,Y,Z = diff_R-G, diff_R-B, diff_G-B
# # cases:
# RGB: all values above 1
# GRAY: all values below or equal to 1

# example classification
# image_1: (S, GRAY)
# image_2: (S, RGB)
# image_3: (NS, GRAY)
# image_4: (S_GB, RGB)
# image_5: (S_B, RGB)
# S_R, S_G, S_B, S_RG, S_RB, S_GB are always RGB
# S or NS can be RGB or GRAY
