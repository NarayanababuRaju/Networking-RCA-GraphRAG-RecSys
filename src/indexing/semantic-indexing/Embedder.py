import torch
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

class TechnicalEmbedder:
    """
    Implementation: Technical Semantic Embedder.
    
    This component converts technical text segments into high-dimensional vectors.
    These vectors allow the system to find 'Related Knowledge' even when the 
    exact keywords don't match.

    TRADE-OFF ANALYSIS:
    ------------------
    1. MODEL CHOICE: all-MiniLM-L6-v2
       - PRO: Optimized for speed and semantic search (~5x faster than BERT-base).
       - CON: Smaller context window (256 tokens) than some larger models.
       - DECISION: Ideal for our 'Chunked' architecture where segments are concise.

    2. BATCHING:
       - PRO: Drastically reduces overhead of CPU/GPU moves.
       - CON: Increases memory footprint.
    """

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"Initializing TechnicalEmbedder with model: {model_name}...")
        # Check for Apple Silicon / GPU acceleration
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        print(f"Model loaded on device: {self.device}")

    def generate_embeddings(self, text_chunks):
        """
        Generates embeddings for a list of text chunks.
        
        Args:
            text_chunks (list): List of strings.
        Returns:
            np.ndarray: Matrix of embeddings (NumChunks x Dimension).
        """
        if not text_chunks:
            return np.array([])
        
        print(f"Generating embeddings for {len(text_chunks)} chunks...")
        embeddings = self.model.encode(text_chunks, show_progress_bar=True, batch_size=32)
        return embeddings

    def save_embeddings(self, embeddings, metadata, output_path):
        """
        Persists embeddings and their corresponding metadata.
        """
        # Save embeddings as a binary numpy file for Faiss consumption
        np.save(f"{output_path}.npy", embeddings)
        
        # Save metadata (the actual text and IDs) as JSON
        with open(f"{output_path}.json", 'w') as f:
            json.dump(metadata, f, indent=4)
        
        print(f"Successfully persisted embeddings and metadata to {output_path}")

if __name__ == "__main__":
    embedder = TechnicalEmbedder()
    
    # 🔬 Sample Technical Knowledge Chunks
    sample_data = [
        {"id": 1, "text": "BGP sessions use TCP port 179 for transport."},
        {"id": 2, "text": "The hold timer defines how long to wait for a keepalive message."},
        {"id": 3, "text": "Maximum Transmission Unit (MTU) mismatches can cause OSPF adjacency hangs."},
        {"id": 4, "text": "BGP-4 is the standard protocol for routing between autonomous systems."}
    ]
    
    chunks = [item["text"] for item in sample_data]
    
    # 1. Generate
    embeddings = embedder.generate_embeddings(chunks)
    
    # 2. Verify
    print(f"\nGenerated Matrix Shape: {embeddings.shape}")
    print(f"First Vector snippet (5 dims): {embeddings[0][:5]}")
    
    # 3. Save (Mock)
    os.makedirs("data/processed", exist_ok=True)
    embedder.save_embeddings(embeddings, sample_data, "data/processed/knowledge_vectors")
