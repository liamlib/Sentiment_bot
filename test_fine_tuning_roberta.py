import pandas as pd
from datasets import Dataset

data = pd.read_csv("prepared_reviews.csv")
dataset = Dataset.from_pandas(data)


dataset = dataset.train_test_split(test_size=0.2)
train_dataset = dataset['train']
test_dataset = dataset['test']

# # Load the CSV into a DataFrame
# df = pd.read_csv('prepared_reviews.csv')

# # Print the DataFrame
# print(df)
