import numpy as np
import json
import os

class GraphProjector:
    """
    Stage 1: Graph Projection & Weighting (The 'View' Builder).
    
    This component creates a weighted mathematical projection of the Knowledge Graph.
    It fuses TOPOLOGY (physical causal links) with SEMANTICS (embedding similarity).
    """

    def __init__(self, alpha=1.0, beta=0.5, similarity_threshold=0.85):
        self.alpha = alpha  # Weight factor for structural edges
        self.beta = beta    # Weight factor for semantic similarity
        self.threshold = similarity_threshold
        print(f"Projector initialized (Alpha: {alpha}, Beta: {beta}, Threshold: {similarity_threshold})")

    def cosine_similarity(self, vec_a, vec_b):
        """Calculates cosine similarity between two vectors."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)

    def build_projection(self, nodes, edges, embeddings):
        """
        Fuses structural and semantic signals into a weighted edge-list.
        """
        projected_edges = []
        node_ids = list(nodes.keys())
        
        # 1. Process Structural Edges (Causal Links)
        print(f"Processing {len(edges)} structural edges...")
        for edge in edges:
            src, tgt = edge['source'], edge['target']
            weight = self.alpha
            projected_edges.append((src, tgt, weight, "structural"))

        # 2. Process Semantic Adjacency (Embeddings)
        print("Computing semantic adjacency...")
        num_nodes = len(node_ids)
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                id_i, id_j = node_ids[i], node_ids[j]
                sim = self.cosine_similarity(embeddings[i], embeddings[j])
                
                if sim >= self.threshold:
                    weight = sim * self.beta
                    projected_edges.append((id_i, id_j, weight, "semantic"))

        return projected_edges

    def save_projection(self, projected_edges, output_path):
        """Saves the weighted edge-list to a CSV for the Leiden Engine."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("source,target,weight,type\n")
            for src, tgt, w, t in projected_edges:
                f.write(f"{src},{tgt},{w:.4f},{t}\n")
        print(f"Weighted projection saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Mock Data for Verification
    mock_nodes = {
        "101": "BGP_DOWN",
        "102": "HOLD_TIMER_EXPIRED",
        "103": "MTU_MISMATCH"
    }
    
    # Structural Edge: 102 (Timer) CAUSES 101 (BGP Down)
    mock_edges = [
        {"source": "102", "target": "101"}
    ]
    
    # Mock Embeddings (101 and 102 are semantically close; 103 is different)
    mock_embeddings = np.array([
        [1.0, 0.2, 0.0],  # BGP DOWN
        [0.9, 0.3, 0.1],  # HOLD_TIMER (Close to 101)
        [0.1, 0.8, 0.9]   # MTU_MISMATCH (Different)
    ])

    projector = GraphProjector()
    projection = projector.build_projection(mock_nodes, mock_edges, mock_embeddings)
    
    # Verify
    print("\n--- Weighted Projection Results ---")
    for src, tgt, w, t in projection:
        print(f"Link: {src} -> {tgt} | Weight: {w:.4f} | Type: {t}")
    
    projector.save_projection(projection, "data/processed/weighted_projection.csv")
