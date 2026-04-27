from datasets import load_dataset

# 1. Load the specific dataset
dataset = load_dataset("LibrAI/do-not-answer", split="train")

# 2. Filter for Information Hazards
# We check if the 'risk_area' column matches
filtered_data = dataset.filter(lambda row: row['risk_area'] == 'Information Hazards')

# 3. Save only the 'query' column to CSV
filtered_data.to_csv("information_hazards_questions.csv", columns=["question"])

print(f"Saved {len(filtered_data)} questions to information_hazards_questions.csv")
