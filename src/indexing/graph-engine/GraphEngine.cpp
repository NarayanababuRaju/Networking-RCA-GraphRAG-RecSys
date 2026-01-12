#include <algorithm>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>

/**
 * @typedef PropertyValue
 * @brief Supports multiple types for node/edge properties.
 */
using PropertyValue = std::variant<std::string, int, double, bool>;

/**
 * @class GNode
 * @brief Represents a vertex in the Knowledge Graph.
 */
class GNode {
public:
  uint64_t id;
  std::string label;
  std::unordered_map<std::string, PropertyValue> properties;

  GNode(uint64_t id, const std::string &label) : id(id), label(label) {}

  void setProperty(const std::string &key, PropertyValue value) {
    properties[key] = value;
  }
};

/**
 * @class GEdge
 * @brief Represents a directed relationship between two GNodes.
 */
class GEdge {
public:
  uint64_t id;
  uint64_t sourceId;
  uint64_t targetId;
  std::string label;
  std::unordered_map<std::string, PropertyValue> properties;

  GEdge(uint64_t id, uint64_t src, uint64_t tgt, const std::string &lbl)
      : id(id), sourceId(src), targetId(tgt), label(lbl) {}

  void setProperty(const std::string &key, PropertyValue value) {
    properties[key] = value;
  }
};

/**
 * @class GraphEngine
 * @brief The core storage and management unit for the Knowledge Graph.
 */
class GraphEngine {
public:
  void addNode(std::shared_ptr<GNode> node) { nodes[node->id] = node; }

  void addEdge(std::shared_ptr<GEdge> edge) {
    edges[edge->id] = edge;
    outEdges[edge->sourceId].push_back(edge->id);
    inEdges[edge->targetId].push_back(edge->id);
  }

  std::shared_ptr<GNode> getNode(uint64_t id) const {
    auto it = nodes.find(id);
    return (it != nodes.end()) ? it->second : nullptr;
  }

  /**
   * @brief Performs a multi-hop traversal to find a causal path using BFS.
   */
  std::vector<uint64_t> findPath(uint64_t startId, uint64_t endId) {
    if (nodes.find(startId) == nodes.end() || nodes.find(endId) == nodes.end())
      return {};

    std::unordered_map<uint64_t, uint64_t> parent;
    std::vector<uint64_t> queue;
    queue.push_back(startId);

    std::unordered_map<uint64_t, bool> visited;
    visited[startId] = true;

    size_t head = 0;
    bool found = false;

    while (head < queue.size()) {
      uint64_t curr = queue[head++];
      if (curr == endId) {
        found = true;
        break;
      }

      auto it = outEdges.find(curr);
      if (it != outEdges.end()) {
        for (uint64_t edgeId : it->second) {
          auto edge_it = edges.find(edgeId);
          if (edge_it != edges.end()) {
            uint64_t neighbor = edge_it->second->targetId;
            if (visited.find(neighbor) == visited.end()) {
              visited[neighbor] = true;
              parent[neighbor] = curr;
              queue.push_back(neighbor);
            }
          }
        }
      }
    }

    std::vector<uint64_t> path;
    if (found) {
      uint64_t curr = endId;
      while (curr != startId) {
        path.push_back(curr);
        curr = parent[curr];
      }
      path.push_back(startId);
      std::reverse(path.begin(), path.end());
    }
    return path;
  }

  void debugPrint() const {
    std::cout << "--- Graph Engine State ---" << std::endl;
    std::cout << "Nodes: " << nodes.size() << " | Edges: " << edges.size()
              << std::endl;
  }

private:
  std::unordered_map<uint64_t, std::shared_ptr<GNode>> nodes;
  std::unordered_map<uint64_t, std::shared_ptr<GEdge>> edges;
  std::unordered_map<uint64_t, std::vector<uint64_t>> outEdges;
  std::unordered_map<uint64_t, std::vector<uint64_t>> inEdges;
};

/**
 * @class EntityRegistry
 * @brief Manages unique node resolution (Record Linkage).
 */
class EntityRegistry {
public:
  uint64_t resolveNode(const std::string &label,
                       const std::string &canonicalName, GraphEngine &engine) {
    std::string key = label + "::" + canonicalName;
    if (registry.count(key))
      return registry[key];

    uint64_t newId = ++nextId;
    auto newNode = std::make_shared<GNode>(newId, label);
    newNode->setProperty("canonical_name", canonicalName);
    engine.addNode(newNode);
    registry[key] = newId;
    return newId;
  }

private:
  uint64_t nextId = 0;
  std::unordered_map<std::string, uint64_t> registry;
};

int main() {
  GraphEngine engine;
  EntityRegistry registry;

  std::cout << "--- Graph Engine: Multi-Hop RCA Traversal Test ---"
            << std::endl;

  // Setup a Causal Chain:
  // [LINK_FAILURE] -> (CAUSES) -> [INTERFACE_DOWN] -> (CAUSES) ->
  // [BGP_SESSION_RESET]

  uint64_t linkId =
      registry.resolveNode("PHYSICAL_EVENT", "LINK_FAILURE", engine);
  uint64_t intfId =
      registry.resolveNode("INTERFACE_STATE", "GIGABIT_ETH_DOWN", engine);
  uint64_t bgpId =
      registry.resolveNode("PROTOCOL_EVENT", "BGP_SESSION_RESET", engine);

  // Link them
  engine.addEdge(std::make_shared<GEdge>(1, linkId, intfId, "CAUSES"));
  engine.addEdge(std::make_shared<GEdge>(2, intfId, bgpId, "CAUSES"));

  std::cout << "Graph built with 2-hop causal chain.\n" << std::endl;

  // Query: Find the path from LINK_FAILURE to BGP_SESSION_RESET
  std::cout << "--- Scenario 1: Physical Link Failure causing BGP Reset ---"
            << std::endl;
  std::cout << "Query: Find path from LINK_FAILURE to BGP_SESSION_RESET..."
            << std::endl;
  std::vector<uint64_t> path1 = engine.findPath(linkId, bgpId);

  if (!path1.empty()) {
    std::cout << "Path Found (Reasoning Chain):" << std::endl;
    for (size_t i = 0; i < path1.size(); ++i) {
      auto node = engine.getNode(path1[i]);
      std::cout << "  Step " << i + 1 << ": [" << node->label << "] "
                << std::get<std::string>(node->properties["canonical_name"])
                << std::endl;
      if (i < path1.size() - 1)
        std::cout << "      | (CAUSES) -> " << std::endl;
    }
  }

  std::cout << "\n--- Scenario 2: MTU Mismatch causing Silent Packet Drops ---"
            << std::endl;
  // [MTU_MISMATCH] -> (CAUSES) -> [PMTUD_FAILURE] -> (CAUSES) ->
  // [TCP_RETRANSMISSIONS]

  uint64_t mtuId =
      registry.resolveNode("CONFIG_ERROR", "MTU_MISMATCH_ON_TRUNK", engine);
  uint64_t pmtuId =
      registry.resolveNode("PROTOCOL_BEHAVIOR", "PMTUD_FAILURE", engine);
  uint64_t tcpRetId = registry.resolveNode("SAMPLED_METRIC",
                                           "HIGH_TCP_RETRANSMISSIONS", engine);

  // Link them (Edges 3 and 4)
  engine.addEdge(std::make_shared<GEdge>(3, mtuId, pmtuId, "CAUSES"));
  engine.addEdge(std::make_shared<GEdge>(4, pmtuId, tcpRetId, "CAUSES"));

  std::cout << "Query: Find RCA for HIGH_TCP_RETRANSMISSIONS..." << std::endl;
  std::vector<uint64_t> rcaPath = engine.findPath(mtuId, tcpRetId);

  if (!rcaPath.empty()) {
    std::cout << "Path Found (Reasoning Chain):" << std::endl;
    for (size_t i = 0; i < rcaPath.size(); ++i) {
      auto node = engine.getNode(rcaPath[i]);
      std::cout << "  Step " << i + 1 << ": [" << node->label << "] "
                << std::get<std::string>(node->properties["canonical_name"])
                << std::endl;
    }
  }

  engine.debugPrint();
  return 0;
}
