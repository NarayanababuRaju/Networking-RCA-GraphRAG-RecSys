import pandas as pd
import json
import os
from collections import defaultdict

class ContextBuilder:
    """
    Stage 1.5: Context Builder (Semantic Glue).
    
    Transforms Hub Node IDs into descriptive technical biographies.
    Aggregates node attributes (from knowledge_vectors.json) and
    causal triplets (from weighted_projection.csv).
    """

    def __init__(self):
        print("Context Builder initialized.")

    def build_context(self, hub_path, projection_path, attributes_path):
        """
        Creates technical biographies for each community based on its hubs.
        """
        print(f"Building context from:\n - Hubs: {hub_path}\n - Projection: {projection_path}\n - Attributes: {attributes_path}")
        
        # 1. Load Data
        with open(hub_path, 'r') as f:
            community_hubs = json.load(f)
        
        edges_df = pd.read_csv(projection_path)
        
        with open(attributes_path, 'r') as f:
            attr_list = json.load(f)
            # Create lookup map for O(1) attribute access
            attr_map = {str(item['id']): item['text'] for item in attr_list}

        # 2. Build Biographies
        community_context = {}

        for comm_id, hubs in community_hubs.items():
            print(f"Processing Community {comm_id}...")
            hub_profiles = []

            for hub in hubs:
                node_id = str(hub['node_id'])
                node_text = attr_map.get(node_id, "Unknown Entity")
                
                # Fetch causal triplets for this hub
                # We look at both incoming and outgoing edges in the projection
                related_edges = edges_df[
                    (edges_df['source'].astype(str) == node_id) | 
                    (edges_df['target'].astype(str) == node_id)
                ]

                triplets = []
                for _, row in related_edges.iterrows():
                    src_id = str(int(row['source']))
                    tgt_id = str(int(row['target']))
                    rel_type = row.get('type', 'related_to')
                    
                    # Resolve names/text for triplets
                    src_text = attr_map.get(src_id, f"Node_{src_id}")
                    tgt_text = attr_map.get(tgt_id, f"Node_{tgt_id}")
                    
                    if src_id == node_id:
                        triplet_desc = f"Maintains a '{rel_type}' relationship with: {tgt_text}"
                    else:
                        triplet_desc = f"Is influenced by: {src_text} (Type: {rel_type})"
                    
                    triplets.append(triplet_desc)

                # Aggregate profile
                hub_profiles.append({
                    "node_id": node_id,
                    "biography": node_text,
                    "rank": hub['rank'],
                    "relationships": triplets
                })

            community_context[comm_id] = hub_profiles

        return community_context

    def save_context(self, context, output_path):
        """Persists the technical biographies to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(context, f, indent=4)
        print(f"Successfully generated biographies for {len(context)} communities. Saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    builder = ContextBuilder()
    
    # Paths assuming standard execution from summarization folder
    hub_file = "data/processed/community_hubs.json"
    proj_file = "../../indexing/clustering/data/processed/weighted_projection.csv"
    attr_file = "../../../data/processed/knowledge_vectors.json"
    
    if os.path.exists(hub_file) and os.path.exists(proj_file) and os.path.exists(attr_file):
        context = builder.build_context(hub_file, proj_file, attr_file)
        
        print("\n--- Context Generation Sample ---")
        for comm_id, profiles in list(context.items())[:1]:
            print(f"Community {comm_id} Biographies:")
            for p in profiles[:2]:
                print(f"  - Node {p['node_id']} (Rank {p['rank']}):")
                print(f"    Desc: {p['biography']}")
                print(f"    Links: {len(p['relationships'])} relationships identified.")
        
        builder.save_context(context, "data/processed/community_context.json")
    else:
        print("Required input data files not found. Ensure previous stages are run.")
