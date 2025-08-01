from sentence_transformers import SentenceTransformer

print("Downloading and caching model: all-MiniLM-L6-v2")
# This line triggers the download and saves the model to a cache folder.
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model download complete and cached.")