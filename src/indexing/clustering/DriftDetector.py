import json
import os

class DriftDetector:
    """
    Stage 4: Temporal Stability Analysis (Drift Detector).
    
    Identifies 'Concept Drift' in the knowledge graph by comparing node 
    community memberships over time.
    """

    def __init__(self, drift_threshold=0.5):
        self.threshold = drift_threshold
        print(f"Drift Detector initialized (Sensitivity: {drift_threshold})")

    def detect_drift(self, current_map_path, baseline_map_path):
        """
        Detects nodes that have migrated between communities.
        """
        print(f"Comparing {current_map_path} against baseline {baseline_map_path}...")
        
        with open(current_map_path, 'r') as f:
            current_map = json.load(f)
        
        with open(baseline_map_path, 'r') as f:
            baseline_map = json.load(f)

        drift_results = {
            "stable_nodes": [],
            "migrated_nodes": [],
            "new_nodes": [],
            "summary": {
                "total_nodes": 0,
                "drift_count": 0,
                "stability_index": 0.0
            }
        }

        all_node_ids = set(current_map.keys()).union(set(baseline_map.keys()))
        drift_results["summary"]["total_nodes"] = len(all_node_ids)

        for node_id in current_map.keys():
            curr = current_map[node_id]
            prev = baseline_map.get(node_id)

            if not prev:
                drift_results["new_nodes"].append(node_id)
                continue

            # Check for changes in Macro or Micro communities
            is_macro_drift = curr['macro_community'] != prev['macro_community']
            is_micro_drift = curr['micro_community'] != prev['micro_community']

            if is_macro_drift or is_micro_drift:
                drift_results["migrated_nodes"].append({
                    "node_id": node_id,
                    "from_macro": prev['macro_community'],
                    "to_macro": curr['macro_community'],
                    "from_micro": prev['micro_community'],
                    "to_micro": curr['micro_community'],
                    "drift_type": "MACRO" if is_macro_drift else "MICRO"
                })
                drift_results["summary"]["drift_count"] += 1
            else:
                drift_results["stable_nodes"].append(node_id)

        # Calculate Stability Index
        total = drift_results["summary"]["total_nodes"]
        if total > 0:
            drift_results["summary"]["stability_index"] = 1.0 - (drift_results["summary"]["drift_count"] / total)

        return drift_results

    def save_analysis(self, results, output_path):
        """Persists the drift analysis to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Drift Analysis complete. Stability Index: {results['summary']['stability_index']:.2f}")
        print(f"Results saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    detector = DriftDetector()
    
    current_file = "data/processed/community_map.json"
    baseline_file = "data/processed/community_map_baseline.json"
    
    # Check if files exist, otherwise run with mocks
    if os.path.exists(current_file) and os.path.exists(baseline_file):
        results = detector.detect_drift(current_file, baseline_file)
        detector.save_analysis(results, "data/processed/drift_analysis.json")
    else:
        print("\n[Logical Verification Test]")
        # Mocking a shift: Node 1 stays stable, Node 2 migrates to new community
        mock_baseline = {
            "1": {"macro_community": 0, "micro_community": 0},
            "2": {"macro_community": 0, "micro_community": 0}
        }
        mock_current = {
            "1": {"macro_community": 0, "micro_community": 0}, # Stable
            "2": {"macro_community": 1, "micro_community": 1}, # DRIFT!
            "3": {"macro_community": 1, "micro_community": 1}  # New Node
        }
        
        with open("mock_baseline.json", 'w') as f: json.dump(mock_baseline, f)
        with open("mock_current.json", 'w') as f: json.dump(mock_current, f)
        
        test_results = detector.detect_drift("mock_current.json", "mock_baseline.json")
        print(f"--- Logic Test Results ---")
        print(f"Total Nodes: {test_results['summary']['total_nodes']}")
        print(f"Drifted Nodes: {test_results['summary']['drift_count']}")
        for m in test_results["migrated_nodes"]:
            print(f"Node {m['node_id']} MIGRATED: {m['from_macro']} -> {m['to_macro']}")
        
        # Cleanup
        if os.path.exists("mock_baseline.json"): os.remove("mock_baseline.json")
        if os.path.exists("mock_current.json"): os.remove("mock_current.json")
