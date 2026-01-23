import pandas as pd
import igraph as ig
import json
import os
from collections import defaultdict

class TopologyFilter:
    """
    Stage 1: Centrality Node Extraction (Topology Filter).
    
    Identifies 'Information Hubs' within each community by calculating
    intra-community PageRank scores. This ensures the LLM focuses on
    the most topologically significant nodes.
    """

    def __init__(self, top_k=10):
        self.top_k = top_k
        print(f"Topology Filter initialized (Top-K per community: {top_k})")

    def extract_hubs(self, projection_path, community_map_path):
        """
        Rank nodes within each community by their local PageRank.
        """
        print(f"Loading projection from {projection_path} and community map from {community_map_path}...")
        
        # 1. Load Data
        edges_df = pd.read_csv(projection_path)
        with open(community_map_path, 'r') as f:
            community_map = json.load(f)

        # 2. Group nodes by community
        comm_to_nodes = defaultdict(list)
        for node_id, data in community_map.items():
            comm_to_nodes[data['micro_community']].append(node_id)

        # 3. Process each community
        community_hubs = {}

        for comm_id, nodes in comm_to_nodes.items():
            if len(nodes) < 2:
                # Minimum nodes to form a meaningful graph
                community_hubs[str(comm_id)] = [{"node_id": n, "rank": 1, "score": 1.0} for n in nodes]
                continue

            # Filter edges belonging solely to this community
            comm_edges_df = edges_df[
                (edges_df['source'].astype(str).isin(nodes)) & 
                (edges_df['target'].astype(str).isin(nodes))
            ]

            if comm_edges_df.empty:
                community_hubs[str(comm_id)] = [{"node_id": n, "rank": 1, "score": 1.0} for n in nodes[:self.top_k]]
                continue

            # Build sub-graph for the community
            tuples = [tuple(x) for x in comm_edges_df[['source', 'target', 'weight']].values]
            g = ig.Graph.TupleList(tuples, directed=True, edge_attrs=['weight'])

            # Calculate PageRank
            scores = g.pagerank(weights='weight')
            
            # Map scores back to node names
            node_scores = []
            for idx, name in enumerate(g.vs['name']):
                node_scores.append({
                    "node_id": str(int(name)),
                    "score": scores[idx]
                })

            # Sort and select Top-K
            node_scores.sort(key=lambda x: x['score'], reverse=True)
            top_hubs = node_scores[:self.top_k]
            
            # Add rank
            for rank, hub in enumerate(top_hubs, 1):
                hub['rank'] = rank

            community_hubs[str(comm_id)] = top_hubs

        return community_hubs

    def save_hubs(self, hubs, output_path):
        """Persists the hub node mapping to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(hubs, f, indent=4)
        print(f"Successfully identified hubs for {len(hubs)} communities. Saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    filter_engine = TopologyFilter(top_k=5)
    
    # Paths (Relative to root of script or project)
    # Adjusting based on standard project structure
    base_dir = "../../indexing/clustering/data/processed/"
    proj_file = os.path.join(base_dir, "weighted_projection.csv")
    cmap_file = os.path.join(base_dir, "community_map.json")
    
    if os.path.exists(proj_file) and os.path.exists(cmap_file):
        hubs = filter_engine.extract_hubs(proj_file, cmap_file)
        
        print("\n--- Hub Extraction Sample ---")
        for comm_id, nodes in list(hubs.items())[:2]:
            print(f"Community {comm_id}: {len(nodes)} hubs identified.")
            for hub in nodes[:2]:
                print(f"  - Node {hub['node_id']} (Score: {hub['score']:.4f})")
        
        filter_engine.save_hubs(hubs, "data/processed/community_hubs.json")
    else:
        print("Input files not found. Ensure clustering has been run.")
