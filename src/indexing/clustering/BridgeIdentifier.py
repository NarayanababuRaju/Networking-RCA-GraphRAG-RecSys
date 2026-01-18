import pandas as pd
import json
import os

class BridgeIdentifier:
    """
    Stage 3: Bridge Node Identification (Bottleneck Detection).
    
    Identifies nodes that connect disparate communities. These are critical
    for understanding failure propagation in networking RCA.
    """

    def __init__(self, bridge_threshold=1):
        self.threshold = bridge_threshold
        print(f"Bridge Identifier initialized (Threshold: {bridge_threshold})")

    def identify_bridges(self, projection_path, community_map_path):
        """
        Detects bridge nodes by checking for inter-community edges.
        """
        print(f"Loading data from {projection_path} and {community_map_path}...")
        df = pd.read_csv(projection_path)
        with open(community_map_path, 'r') as f:
            community_map = json.load(f)

        bridge_data = {}

        # Iterate through every edge in the weighted projection
        for _, row in df.iterrows():
            src_id = str(int(row['source']))
            tgt_id = str(int(row['target']))

            # Get communities for source and target
            src_comm = community_map.get(src_id)
            tgt_comm = community_map.get(tgt_id)

            if not src_comm or not tgt_comm:
                continue

            # 1. Macro Bridge Check
            if src_comm['macro_community'] != tgt_comm['macro_community']:
                self._update_score(bridge_data, src_id, "macro_bridge_score")
                self._update_score(bridge_data, tgt_id, "macro_bridge_score")

            # 2. Micro Bridge Check
            if src_comm['micro_community'] != tgt_comm['micro_community']:
                self._update_score(bridge_data, src_id, "micro_bridge_score")
                self._update_score(bridge_data, tgt_id, "micro_bridge_score")

        # Convert to list and sort by importance
        bridges = []
        for node_id, scores in bridge_data.items():
            bridges.append({
                "node_id": node_id,
                "macro_score": scores.get("macro_bridge_score", 0),
                "micro_score": scores.get("micro_bridge_score", 0)
            })

        # Sort by macro score primarily, then micro
        bridges.sort(key=lambda x: (x['macro_score'], x['micro_score']), reverse=True)
        return bridges

    def _update_score(self, data, node_id, key):
        if node_id not in data:
            data[node_id] = {}
        data[node_id][key] = data[node_id].get(key, 0) + 1

    def save_bridges(self, bridges, output_path):
        """Persists the bridge nodes to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(bridges, f, indent=4)
        print(f"Successfully identified {len(bridges)} bridge candidates. Saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    identifier = BridgeIdentifier()
    
    proj_file = "data/processed/weighted_projection.csv"
    cmap_file = "data/processed/community_map.json"
    
    # 1. Real Data Execution
    if os.path.exists(proj_file) and os.path.exists(cmap_file):
        print("\n[Executing on Real Data]")
        bridges = identifier.identify_bridges(proj_file, cmap_file)
        if not bridges:
            print("Note: Current graph is a single community. No actual bridges yet.")
    
    # 2. Logical Unit Test (The "WOW" Verification)
    print("\n[Logical Verification Test]")
    mock_proj = pd.DataFrame([
        {"source": 1, "target": 2, "weight": 1.0}, # Intra-community (Comm A)
        {"source": 2, "target": 3, "weight": 1.0}  # BRIDGE EDGE (Comm A -> Comm B)
    ])
    mock_cmap = {
        "1": {"macro_community": 0, "micro_community": 0}, # Comm A
        "2": {"macro_community": 0, "micro_community": 0}, # Comm A
        "3": {"macro_community": 1, "micro_community": 1}  # Comm B
    }
    
    # Write temp files for test
    mock_proj.to_csv("mock_proj.csv", index=False)
    with open("mock_cmap.json", 'w') as f: json.dump(mock_cmap, f)
    
    test_bridges = identifier.identify_bridges("mock_proj.csv", "mock_cmap.json")
    print("--- Logic Test Results ---")
    for b in test_bridges:
        print(f"Node {b['node_id']} flagged as Bridge! | Score: {b['macro_score']}")
    
    # Cleanup
    if os.path.exists("mock_proj.csv"): os.remove("mock_proj.csv")
    if os.path.exists("mock_cmap.json"): os.remove("mock_cmap.json")
