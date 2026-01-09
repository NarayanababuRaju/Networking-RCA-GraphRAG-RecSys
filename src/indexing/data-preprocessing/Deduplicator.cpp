#include <algorithm>
#include <functional>
#include <iomanip>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

/**
 * @brief Production-grade Deduplication Engine with LSH (Locality Sensitive
 * Hashing). Uses the 'Bands & Rows' technique to scale search to O(1).
 */
class Deduplicator {
public:
  Deduplicator(int numHashes = 200, int shingleSize = 5, int bands = 20,
               int rows = 10)
      : numHashes(numHashes), shingleSize(shingleSize), bands(bands),
        rows(rows) {

    if (numHashes != bands * rows) {
      std::cerr
          << "Warning: numHashes should equal bands * rows for optimal layout."
          << std::endl;
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint64_t> dist(1, MAX_PRIME - 1);

    for (int i = 0; i < numHashes; ++i) {
      hashCoeffsA.push_back(dist(gen));
      hashCoeffsB.push_back(dist(gen));
    }
  }

  /**
   * @brief Generates a MinHash signature.
   */
  std::vector<uint64_t> generateSignature(const std::string &text) {
    std::set<std::string> shingles = getShingles(text);
    std::vector<uint64_t> signature(numHashes,
                                    std::numeric_limits<uint64_t>::max());

    for (const auto &shingle : shingles) {
      uint64_t shingleHash = std::hash<std::string>{}(shingle);
      for (int i = 0; i < numHashes; ++i) {
        uint64_t val =
            (hashCoeffsA[i] * shingleHash + hashCoeffsB[i]) % MAX_PRIME;
        signature[i] = std::min(signature[i], val);
      }
    }
    return signature;
  }

  /**
   * @brief Adds a document signature to the LSH index (Bucketing).
   */
  void indexDocument(int docId, const std::vector<uint64_t> &signature) {
    for (int b = 0; b < bands; ++b) {
      uint64_t bandHash = hashBand(signature, b);
      lshBuckets[b][bandHash].push_back(docId);
    }
    allSignatures[docId] = signature;
  }

  /**
   * @brief Finds near-duplicate candidates using LSH buckets.
   */
  std::vector<int> findCandidates(const std::vector<uint64_t> &querySignature) {
    std::unordered_set<int> candidates;
    for (int b = 0; b < bands; ++b) {
      uint64_t bandHash = hashBand(querySignature, b);
      if (lshBuckets[b].count(bandHash)) {
        for (int docId : lshBuckets[b][bandHash]) {
          candidates.insert(docId);
        }
      }
    }
    return std::vector<int>(candidates.begin(), candidates.end());
  }

  /**
   * @brief Final verification: Calculate exact similarity for candidates.
   */
  double calculateSimilarity(const std::vector<uint64_t> &sig1,
                             const std::vector<uint64_t> &sig2) {
    int matchCount = 0;
    for (size_t i = 0; i < std::min(sig1.size(), sig2.size()); ++i) {
      if (sig1[i] == sig2[i])
        matchCount++;
    }
    return static_cast<double>(matchCount) / numHashes;
  }

  const std::vector<uint64_t> &getSignature(int docId) {
    return allSignatures[docId];
  }

private:
  int numHashes, shingleSize, bands, rows;
  const uint64_t MAX_PRIME = 4294967291ull;
  std::vector<uint64_t> hashCoeffsA;
  std::vector<uint64_t> hashCoeffsB;

  // LSH Index: Band Index -> (Band Hash -> List of Doc IDs)
  std::unordered_map<int, std::unordered_map<uint64_t, std::vector<int>>>
      lshBuckets;
  std::unordered_map<int, std::vector<uint64_t>> allSignatures;

  /**
   * @brief Hashes a single band of the signature.
   */
  uint64_t hashBand(const std::vector<uint64_t> &signature, int bandIdx) {
    uint64_t h = 0;
    int start = bandIdx * rows;
    for (int i = 0; i < rows; ++i) {
      // Simple robust hash combining for the band's values
      h ^= signature[start + i] + 0x9e3779b9 + (h << 6) + (h >> 2);
    }
    return h;
  }

  std::set<std::string> getShingles(const std::string &text) {
    std::set<std::string> shingles;
    if (text.length() < (size_t)shingleSize)
      return {text};
    for (size_t i = 0; i <= text.length() - shingleSize; ++i) {
      shingles.insert(text.substr(i, shingleSize));
    }
    return shingles;
  }
};

int main() {
  Deduplicator engine(200, 5, 20, 10); // 200 hashes = 20 bands * 10 rows

  std::string docSource =
      "The BGP Finite State Machine consists of 6 states: Idle, Connect, "
      "Active, OpenSent, OpenConfirm, and Established.";
  std::string docNearDup =
      "The BGP Finite State Machine consists of six states: Idle, Connect, "
      "Active, OpenSent, OpenConfirm, and Established.";
  std::string docDifferent = "Address Resolution Protocol (ARP) maps IP "
                             "addresses to MAC hardware addresses.";

  // 1. Indexing
  engine.indexDocument(101, engine.generateSignature(docSource));
  engine.indexDocument(102, engine.generateSignature(docDifferent));

  std::cout << "--- LSH Scalability Test ---" << std::endl;

  // 2. Querying with near-duplicate
  auto querySig = engine.generateSignature(docNearDup);
  std::vector<int> candidates = engine.findCandidates(querySig);

  std::cout << "Found " << candidates.size() << " candidates in buckets."
            << std::endl;

  for (int candId : candidates) {
    double sim =
        engine.calculateSimilarity(querySig, engine.getSignature(candId));
    std::cout << "-> Checking Candidate ID " << candId
              << " | Similarity: " << (sim * 100) << "%" << std::endl;
    if (sim > 0.8) {
      std::cout << "   [!] NEAR-DUPLICATE DETECTED: Source matches Query."
                << std::endl;
    }
  }

  return 0;
}
