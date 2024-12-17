from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis", model="roberta-base")

review_content = "The best game ever!"

result = sentiment_analyzer(review_content)
print(result)