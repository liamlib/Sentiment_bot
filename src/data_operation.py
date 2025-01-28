import pandas as pd
import json

with open('reviews.json', 'r') as file:
     data = json.load(file)

df = pd.DataFrame(data)

def catergorise_rating(rating):
    rating = float(rating)
    if rating >= 7:
        return "positive"
    elif 4 <= rating <7:
        return "neutral"
    else:
        return "negative"

print(catergorise_rating(2))


df['label'] = df['Rating'].apply(catergorise_rating)


df_prepared = df[['Content' , 'label']]


df_prepared.rename(columns={"Content": "review"}, inplace=True)

df_prepared.to_csv("prepared_reviews.csv", index=False)
