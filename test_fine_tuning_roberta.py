import pandas as pd
from datasets import Dataset
from transformers import RobertaForSequenceClassification, RobertaTokenizer, Trainer, TrainingArguments

# Load your data
data = pd.read_csv("prepared_reviews.csv")

data['label'] = data['label'].apply(lambda x: 1 if x >= 7 else (0 if x <= 4 else None))
data = data.dropna(subset=['label'])

data = data[['review', 'label']].dropna() 
data['review'] = data['review'].astype(str)
data['label'] = data['label'].astype(int)

dataset = Dataset.from_pandas(data)

dataset = dataset.train_test_split(test_size=0.2)
train_dataset = dataset['train']
test_dataset = dataset['test']

tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

def preprocess_data(examples):
    """Tokenizes the text data for the model."""
    return tokenizer(
        examples['review'],              # Text to tokenize
        padding="max_length",            # Pad to max length
        truncation=True,                 # Truncate if too long
        max_length=512                   # Maximum input length
    )

# Apply preprocessing (tokenization) to the datasets
train_dataset = train_dataset.map(preprocess_data, batched=True)
test_dataset = test_dataset.map(preprocess_data, batched=True)

# Load RoBERTa model for sequence classification
model = RobertaForSequenceClassification.from_pretrained("roberta-base", num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",          # Output directory
    evaluation_strategy="epoch",     # Evaluate each epoch
    learning_rate=2e-5,              # Learning rate
    per_device_train_batch_size=8,   # Batch size for training
    per_device_eval_batch_size=8,    # Batch size for evaluation
    num_train_epochs=3,              # Number of epochs
    weight_decay=0.01,               # Weight decay for regularization
    logging_dir="./logs",            # Logging directory
    logging_steps=10,                # Log every 10 steps
    save_strategy="epoch"            # Save checkpoints at the end of each epoch
)

trainer = Trainer(
    model=model,                           # The model to train
    args=training_args,                    # Training arguments
    train_dataset=train_dataset,           # Training dataset
    eval_dataset=test_dataset              # Evaluation dataset
)

trainer.train()

results = trainer.evaluate()
print("Evaluation Results:", results)

model.save_pretrained("./fine_tuned_roberta")
tokenizer.save_pretrained("./fine_tuned_roberta")
