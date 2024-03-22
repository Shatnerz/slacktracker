"""Plot out histogram of deleted users"""

import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


if __name__ == "__main__":
    pass

deleted_path = Path(__file__).parent / "data" / "humans_deleted.csv"
df = pd.read_csv(deleted_path)

df["updated"] = pd.to_datetime(df["updated_epoch"], unit="s")
df.set_index("updated", inplace=True)

# Resample by week and count entries. This example assumes each row is an entry you're counting.
weekly_data = df.resample('W').size()
# Cut first bin since it is likely time of last mass update
weekly_data = weekly_data[1:]

# Plot
plt.figure(figsize=(10,6))
weekly_data.plot(kind='bar')
plt.title('Entries per Week')
plt.xlabel('Week')
plt.ylabel('Count')

ax = plt.gca()  # Get current axis
# Hack around DateFormatter issue (https://stackoverflow.com/questions/69101233/using-dateformatter-resets-starting-date-to-1970)
x_labels = [date.strftime("%Y-%m-%d") for date in weekly_data.index]
ax.set_xticklabels(x_labels)
# Only show every fifth tick label
for i, label in enumerate(ax.xaxis.get_ticklabels()):
    if i % 5 != 0:
        label.set_visible(False)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
