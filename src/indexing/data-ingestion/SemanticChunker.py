from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class SemanticChunker:
    def __init__(self, model_name='all-MiniLM-L6-v2', threshold=0.8):
        """
        Initializes the Semantic Chunker with a BERT-based model.
        
        Args:
            model_name (str): The name of the sentence-transformer model.
            threshold (float): Similarity threshold (0 to 1). If similarity drops below this, a new chunk starts.
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

    def split_sentences(self, text):
        """
        Split text into sentences. Simple regex-based splitter for demonstration.
        In production, use Spacy or NLTK for high accuracy.
        """
        # Split by . followed by space, but handle common abbreviations
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, text):
        """
        Processes cleaned text and returns a list of semantic chunks.
        """
        sentences = self.split_sentences(text)
        if not sentences:
            return []

        print(f"Analyzing {len(sentences)} sentences for thematic shifts...")
        
        # 1. Generate embeddings for all sentences
        embeddings = self.model.encode(sentences)
        
        chunks = []
        current_chunk = [sentences[0]]
        
        # 2. Compare adjacent sentences
        for i in range(1, len(sentences)):
            # Calculate cosine similarity between sentence i and i-1
            # Reshape for sklearn requirement
            sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
            
            if sim < self.threshold:
                # Topic shift detected! Store current chunk and start a new one.
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
            else:
                current_chunk.append(sentences[i])
        
        # Add the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

# --- Production Simulation ---
if __name__ == "__main__":
    # Sample cleaned data from our C++ DataCleaner (simulate RFC 4271 content)
    cleaned_rfc_text = (
        "The Border Gateway Protocol Finite State Machine consists of six states. "
        "The first state is Idle. In the Idle state, the Border Gateway Protocol ignores all incoming messages. "
        "Upon receiving a Start event, the system transitions to the Connect state. "
        "BGP uses TCP port 179 for all control plane traffic. "
        "TCP establishs a three-way handshake before the Border Gateway Protocol Open message is exchanged. "
        "If the TCP connection fails, the Finite State Machine transitions back to Idle. "
        "The Open Message contains the hold timer and the local Border Gateway Protocol Identifier. "
        "Wait-for-Open and Established are subsequent states in the machine."
    )

    # Initialize Chunker with a strict threshold for finding boundaries
    chunker = SemanticChunker(threshold=0.6) # Lowered for smaller text samples
    
    smart_chunks = chunker.chunk_text(cleaned_rfc_text)
    
    print(f"\n--- Produced {len(smart_chunks)} Smart Chunks ---")
    for idx, chunk in enumerate(smart_chunks):
        print(f"\n[Chunk {idx+1}]:")
        print(chunk)
        print("-" * 50)
