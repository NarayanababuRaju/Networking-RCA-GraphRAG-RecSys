import json
import os
import sys
import numpy as np

# Path adjustment to import the TechnicalEmbedder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../semantic-indexing")))
from Embedder import TechnicalEmbedder

class SummaryIndexer:
    """
    Stage 4: Summary Indexing.
    
    Converts structured Knowledge Briefs into searchable vectors.
    Creates a 'Thematic Index' that represents entire communities.
    """

    def __init__(self):
        self.embedder = TechnicalEmbedder()
        print("Summary Indexer initialized.")

    def index_briefs(self, briefs_path):
        """
        Flatten, vectorize, and prepare the community index.
        """
        print(f"Reading briefs from {briefs_path}...")
        with open(briefs_path, 'r') as f:
            briefs = json.load(f)

        thematic_texts = []
        metadata = []

        for comm_id, brief in briefs.items():
            # 1. Flatten for indexing
            # We combine title, summary, symptoms, and causes for maximum recall
            flat_text = f"TITLE: {brief['title']}\n"
            flat_text += f"SUMMARY: {brief['summary']}\n"
            flat_text += f"SYMPTOMS: {', '.join(brief['symptoms'])}\n"
            flat_text += f"CAUSES: {', '.join(brief['potential_causes'])}"
            
            thematic_texts.append(flat_text)
            metadata.append({
                "community_id": comm_id,
                "title": brief['title'],
                "original_summary": brief['summary']
            })

        # 2. Vectorize
        print(f"Vectorizing {len(thematic_texts)} community themes...")
        embeddings = self.embedder.generate_embeddings(thematic_texts)

        return embeddings, metadata

    def save_index(self, embeddings, metadata, output_base):
        """Saves vectors and metadata to disk."""
        os.makedirs(os.path.dirname(output_base), exist_ok=True)
        
        # Save vectors
        np.save(f"{output_base}.npy", embeddings)
        
        # Save metadata
        with open(f"{output_base}.json", 'w') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Successfully created community index at {output_base}")

if __name__ == "__main__":
    # 🔬 Verification Script
    indexer = SummaryIndexer()
    
    # Path relative to summarization folder
    briefs_file = "data/processed/community_briefs.json"
    
    if os.path.exists(briefs_file):
        embeddings, metadata = index_briefs = indexer.index_briefs(briefs_file)
        
        print(f"\nCreated Vector Matrix: {embeddings.shape}")
        
        # Save to disk
        indexer.save_index(embeddings, metadata, "data/processed/community_index")
    else:
        print(f"Error: Briefs file {briefs_file} not found. Run KnowledgeSynthesizer.py first.")
