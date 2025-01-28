import json

with open('aggregated_reviews.json', 'r') as f1:
    data1 = json.load(f1)

with open('aggregated_reviews_2.json', 'r') as f2:
    data2 = json.load(f2)

merged_data = data1 + data2

with open('reviews.json', 'w') as mf:
    json.dump(merged_data, mf, indent=4)

print("Files have been concatenated successfully.")