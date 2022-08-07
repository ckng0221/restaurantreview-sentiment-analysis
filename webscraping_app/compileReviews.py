# %%
from pathlib import Path

import pandas as pd


def main():
    "Compile all data."
    # path = Path("data/review")
    path = Path("/Users/ckng/Desktop/Coding/Selenium/data/review")

    data = []
    for file in path.glob('*.csv'):
        location = str(file).split("_")[2].split('.')[0]
        df = pd.read_csv(file)
        df["Location"] = location
        data.append(df)
    df = pd.concat(data)
    df.drop_duplicates(inplace=True)

    return df


if __name__ == "__main__":
    df = main()

# %%
df.Location.hist()
# %%
df.Rating.hist()
# %%
totalRestaurant = df[['Restaurant', 'Location']].drop_duplicates().index.size
totalReviews = df.index.size
print(f"Total Restaurant: {totalRestaurant}")
print(f"Total Restaurant: {totalReviews}")
# %%
