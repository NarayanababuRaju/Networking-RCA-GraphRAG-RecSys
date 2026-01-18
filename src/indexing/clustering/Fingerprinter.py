import json
import hashlib
import os
from collections import defaultdict

class CommunityFingerprinter:
    """
    Stage 5: Community Fingerprinting (The Lazy Trigger).
    
    Generates unique, deterministic hashes for communities to optimize 
    downstream LLM summarization.
    """

    def __init__(self):
        print("Community Fingerprinter initialized.")

    def generate_fingerprints(self, community_map_path):
        """
        Groups nodes by community and hashes their sorted ID lists.
        """
        print(f"Loading community map from {community_map_path}...")
        with open(community_map_path, 'r') as f:
            community_map = json.load(f)

        # 1. Group nodes by their community IDs
        macro_groups = defaultdict(list)
        micro_groups = defaultdict(list)

        for node_id, comms in community_map.items():
            macro_id = comms['macro_community']
            micro_id = comms['micro_community']
            
            macro_groups[macro_id].append(str(node_id))
            micro_groups[micro_id].append(str(node_id))

        # 2. Generate deterministic hashes
        fingerprints = {
            "macro_communities": {},
            "micro_communities": {}
        }

        print(f"Generating fingerprints for {len(macro_groups)} macro and {len(micro_groups)} micro communities...")

        for m_id, nodes in macro_groups.items():
            fingerprints["macro_communities"][str(m_id)] = self._hash_nodes(nodes)

        for m_id, nodes in micro_groups.items():
            fingerprints["micro_communities"][str(m_id)] = self._hash_nodes(nodes)

        return fingerprints

    def _hash_nodes(self, node_list):
        """
        Sorts nodes and generates an SHA-256 hash.
        """
        # Sorting is CRITICAL for determinism
        sorted_nodes = sorted(node_list)
        content = ",".join(sorted_nodes)
        return hashlib.sha256(content.encode()).hexdigest()

    def save_fingerprints(self, fingerprints, output_path):
        """Persists the fingerprints to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(fingerprints, f, indent=4)
        print(f"Fingerprints saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    printer = CommunityFingerprinter()
    
    cmap_file = "data/processed/community_map.json"
    
    if os.path.exists(cmap_file):
        fps = printer.generate_fingerprints(cmap_file)
        printer.save_fingerprints(fps, "data/processed/community_fingerprints.json")
    else:
        print("\n[Logical Verification Test]")
        # Mock data: Two communities
        mock_cmap = {
            "1": {"macro_community": 0, "micro_community": 0},
            "2": {"macro_community": 0, "micro_community": 0},
            "3": {"macro_community": 1, "micro_community": 1}
        }
        
        with open("mock_cmap.json", 'w') as f: json.dump(mock_cmap, f)
        
        test_fps = printer.generate_fingerprints("mock_cmap.json")
        
        print("\n--- Fingerprint Results ---")
        for m_id, h in test_fps["macro_communities"].items():
            print(f"Macro Community {m_id} -> {h[:16]}...")

        # Verify Determinism: Run again, hash must be identical
        test_fps_v2 = printer.generate_fingerprints("mock_cmap.json")
        if test_fps["macro_communities"]["0"] == test_fps_v2["macro_communities"]["0"]:
            print("\n✅ Determinism Check PASSED.")
        
        # Cleanup
        if os.path.exists("mock_cmap.json"): os.remove("mock_cmap.json")
