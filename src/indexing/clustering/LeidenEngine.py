import igraph as ig
import leidenalg as la
import pandas as pd
import json
import os

class LeidenEngine:
    """
    Stage 2: Hierarchical Clustering (The Leiden Engine).
    
    Uses modularity optimization to find dense clusters within the 
    weighted graph projection. Supports multi-level resolutions.
    """

    def __init__(self, resolution_macro=0.1, resolution_micro=1.0):
        self.res_macro = resolution_macro
        self.res_micro = resolution_micro
        print(f"Leiden Engine initialized (Macro Resolution: {resolution_macro}, Micro: {resolution_micro})")

    def cluster(self, projection_path):
        """
        Loads the weighted projection and performs hierarchical clustering.
        """
        print(f"Loading weighted projection from {projection_path}...")
        df = pd.read_csv(projection_path)
        
        # 1. Build Graph
        tuples = [tuple(x) for x in df[['source', 'target', 'weight']].values]
        g = ig.Graph.TupleList(tuples, directed=True, edge_attrs=['weight'])
        
        # 2. Run Leiden Partitioning (Macro)
        print("Running Macro-Level Partitioning...")
        partition_macro = la.find_partition(
            g, 
            la.RBConfigurationVertexPartition, 
            weights='weight', 
            resolution_parameter=self.res_macro
        )
        
        # 3. Run Leiden Partitioning (Micro)
        print("Running Micro-Level Partitioning...")
        partition_micro = la.find_partition(
            g, 
            la.RBConfigurationVertexPartition, 
            weights='weight', 
            resolution_parameter=self.res_micro
        )

        # 4. Compile Results
        community_map = {}
        for idx, node_name in enumerate(g.vs['name']):
            community_map[str(int(node_name))] = {
                "macro_community": partition_macro.membership[idx],
                "micro_community": partition_micro.membership[idx]
            }

        return community_map

    def save_community_map(self, community_map, output_path):
        """Persists the node->community mapping to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(community_map, f, indent=4)
        print(f"Community map successfully persisted to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    engine = LeidenEngine()
    
    # Check if projection file exists
    proj_file = "data/processed/weighted_projection.csv"
    if os.path.exists(proj_file):
        cmap = engine.cluster(proj_file)
        
        print("\n--- Clustering Results ---")
        for node, meta in cmap.items():
            print(f"Node {node} | Macro: {meta['macro_community']} | Micro: {meta['micro_community']}")
            
        engine.save_community_map(cmap, "data/processed/community_map.json")
    else:
        print(f"Error: Projection file {proj_file} not found. Run Projector.py first.")
