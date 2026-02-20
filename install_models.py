from transformers import pipeline

# Example text to trigger full model download
example_text = "This is a simple test sentence for downloading models."

# # -----------------------
# # BART for summarization
# # -----------------------
# print("Downloading BART model...")
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
# # Run a dummy summarization to download full weights
# summarizer(example_text, max_length=20, min_length=5)

# # -----------------------
# # T5 for summarization
# # -----------------------
# print("Downloading T5 model...")
# t5_summarizer = pipeline("summarization", model="t5-base")
# t5_summarizer(example_text, max_length=20, min_length=5)

# # -----------------------
# # Pegasus CNN/DailyMail for summarization
# # -----------------------
# print("Downloading Pegasus model...")
# pegasus_summarizer = pipeline("summarization", model="google/pegasus-cnn_dailymail")
# pegasus_summarizer(example_text, max_length=20, min_length=5)

# # -----------------------
# # GPT-2 for text generation
# # -----------------------
# print("Downloading GPT-2 model...")
# generator = pipeline("text-generation", model="gpt2")
# generator("Once upon a time", max_length=20)

# # -----------------------
# # BERT for feature extraction
# # -----------------------
# print("Downloading BERT model...")
# extractor = pipeline("feature-extraction", model="bert-base-uncased")
# extractor("This is a test sentence.")

print("All models downloaded and cached successfully!")



"""
stored at:
~/.cache/huggingface/

rm -rf ~/.cache/huggingface
rm -rf ~/.cache/huggingface/hub/facebook_bart-large-cnn

du -sh ~/.cache/huggingface/hub

"""