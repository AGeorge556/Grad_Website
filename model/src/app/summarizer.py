from transformers import pipeline
import torch

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1)

def chunk_text(text, max_length=1000):
    """Split text into chunks of approximately max_length characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def summarize_text(text, max_length=150):
    """Summarize text by first chunking it if necessary."""
    # Split text into chunks if it's too long
    chunks = chunk_text(text)
    
    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=max_length, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    # If we only have one chunk, return its summary
    if len(summaries) == 1:
        return summaries[0]
    
    # If we have multiple chunks, combine their summaries and summarize again
    combined_summary = ' '.join(summaries)
    final_summary = summarizer(combined_summary, max_length=max_length, min_length=30, do_sample=False)
    return final_summary[0]['summary_text']
