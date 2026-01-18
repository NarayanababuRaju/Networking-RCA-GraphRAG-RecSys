import igraph as ig
import leidenalg as la
import pandas as pd
import json
import os

class LeidenEngineHierarchical:
    """
    Stage 2 (Enhanced): True Hierarchical Clustering.
    
    Generates an N-level community hierarchy based on a list of resolutions.
    This allows navigating from broad fault domains to granular states.
    """

    def __init__(self, resolutions=[0.01, 0.1, 1.0]):
        self.resolutions = sorted(resolutions)
        print(f"Hierarchical Leiden Engine initialized with resolutions: {self.resolutions}")

    def cluster(self, projection_path):
        """
        Performs multi-level clustering and builds a community tree.
        """
        print(f"Loading weighted projection from {projection_path}...")
        df = pd.read_csv(projection_path)
        
        # 1. Build Graph
        tuples = [tuple(x) for x in df[['source', 'target', 'weight']].values]
        g = ig.Graph.TupleList(tuples, directed=True, edge_attrs=['weight'])
        
        # 2. Generate Multi-Level Partitions
        hierarchical_map = {}
        for node_name in g.vs['name']:
            hierarchical_map[str(int(node_name))] = {"path": []}

        # Community Tree structure
        tree = {"levels": []}

        for i, res in enumerate(self.resolutions):
            print(f"Running Level {i} Partitioning (Resolution: {res})...")
            partition = la.find_partition(
                g, 
                la.RBConfigurationVertexPartition, 
                weights='weight', 
                resolution_parameter=res
            )
            
            # Map membership to each node path
            level_data = {"resolution": res, "communities": {}}
            for idx, node_name in enumerate(g.vs['name']):
                comm_id = partition.membership[idx]
                hierarchical_map[str(int(node_name))]["path"].append(comm_id)
                
                if comm_id not in level_data["communities"]:
                    level_data["communities"][comm_id] = []
                level_data["communities"][comm_id].append(str(int(node_name)))
            
            tree["levels"].append(level_data)

        return hierarchical_map, tree

    def save_results(self, community_map, tree, output_dir):
        """Persists both the node map and the community tree."""
        os.makedirs(output_dir, exist_ok=True)
        
        map_path = os.path.join(output_dir, "hierarchical_community_map.json")
        with open(map_path, 'w') as f:
            json.dump(community_map, f, indent=4)
            
        tree_path = os.path.join(output_dir, "community_tree.json")
        with open(tree_path, 'w') as f:
            json.dump(tree, f, indent=4)
            
        # Compatibility Save
        compat_map = {}
        for node_id, data in community_map.items():
            compat_map[node_id] = {
                "macro_community": data["path"][0],
                "micro_community": data["path"][-1]
            }
        
        compat_path = os.path.join(output_dir, "community_map.json")
        with open(compat_path, 'w') as f:
            json.dump(compat_map, f, indent=4)
            
        print(f"Hierarchical results successfully saved to {output_dir}")

if __name__ == "__main__":
    engine = LeidenEngineHierarchical(resolutions=[0.01, 0.1, 1.0])
    proj_file = "data/processed/weighted_projection.csv"
    if os.path.exists(proj_file):
        hmap, tree = engine.cluster(proj_file)
        engine.save_results(hmap, tree, "data/processed/")
