#include <iostream>
#include <regex>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

/**
 * @struct Entity
 * @brief Represents a technical entity extracted from networking text.
 */
struct Entity {
  std::string type;  // e.g., "IP_ADDRESS", "INTERFACE", "ERROR_CODE"
  std::string value; // The actual extracted string
  double confidence; // 1.0 for deterministic extraction
};

/**
 * @class DeterministicExtractor
 * @brief A high-performance, regex-based engine for extracting structured
 * networking entities.
 *
 * LEAD DEVELOPER NOTE:
 * We use C++ Regex for this stage because the entities (IPs, MACs, ASNs) follow
 * strict, non-ambiguous patterns.
 *
 * TRADE-OFF ANALYSIS:
 * - PRO: Zero "Hallucination" risk. Deterministic rules ensure 100% precision.
 * - PRO: Extreme speed. Microsecond-level extraction suitable for real-time
 * streaming logs.
 * - CON: Brittle. Does not handle semantically similar but structurally
 * different terms (e.g., "The first port" vs "Eth1/1").
 * - CON: Maintenance overhead. If a vendor changes their log format, the regex
 * must be updated manually.
 */
class DeterministicExtractor {
public:
  DeterministicExtractor() {
    // Define high-precision networking patterns

    // 1. IPv4 Address (Standard decimal-dot notation)
    patterns["IP_ADDRESS"] = std::regex(
        R"(\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)");

    // 2. ASN (Autonomous System Number - matches "AS" followed by 1-10 digits)
    patterns["ASN"] =
        std::regex(R"(\bAS\d{1,10}\b)", std::regex_constants::icase);

    // 3. Interface Names (Match canonical forms like GigabitEthernet1/1/1 or
    // TenGigabitEthernet0/1)
    patterns["INTERFACE"] = std::regex(
        R"(\b(?:GigabitEthernet|TenGigabitEthernet|FastEthernet|Ethernet|Loopback|Port-Channel)\d+(?:\/\d+)*\b)");

    // 4. Cisco/Juniper Style Error Codes (e.g., %BGP-3-NOTIFICATION,
    // %LINEPROTO-5-UPDOWN)
    patterns["ERROR_CODE"] = std::regex(R"(%[A-Z0-9_\-]+-\d+-[A-Z0-9_\-]+)");

    // 5. MAC Address (Standard colon or hyphen separated hex)
    patterns["MAC_ADDRESS"] =
        std::regex(R"(\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b)");
  }

  /**
   * @brief Extracts all recognized entities from a given text chunk.
   * @param text The cleaned/normalized networking text.
   * @return A vector of extracted Entity objects.
   */
  std::vector<Entity> extract(const std::string &text) {
    std::vector<Entity> results;

    for (const auto &[type, pattern] : patterns) {
      auto words_begin =
          std::sregex_iterator(text.begin(), text.end(), pattern);
      auto words_end = std::sregex_iterator();

      for (std::sregex_iterator i = words_begin; i != words_end; ++i) {
        std::smatch match = *i;
        results.push_back({type, match.str(), 1.0});
      }
    }

    return results;
  }

private:
  std::unordered_map<std::string, std::regex> patterns;
};

int main() {
  DeterministicExtractor extractor;

  // Test text containing multiple high-precision entities
  std::string sampleText = "BGP Neighbor 192.168.1.10 in AS65001 reported "
                           "%BGP-3-NOTIFICATION on GigabitEthernet1/0/2. "
                           "Source MAC: 00:1A:2B:3C:4D:5E. Interface "
                           "TenGigabitEthernet0/1/0 is flaps.";

  std::cout << "--- Deterministic Entity Extraction Test ---" << std::endl;
  std::cout << "Input Text: " << sampleText << "\n" << std::endl;

  auto entities = extractor.extract(sampleText);

  if (entities.empty()) {
    std::cout << "No entities found." << std::endl;
  } else {
    std::cout << "Extracted Entities:" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    for (const auto &e : entities) {
      std::cout << "Type: [" << e.type << "] | Value: " << e.value
                << " | Confidence: " << e.confidence << std::endl;
    }
    std::cout << "----------------------------------------" << std::endl;
  }

  /*
   * LEAD DEVELOPER TRADE-OFF RECAP:
   * Note how we correctly extracted 192.168.1.10 and AS65001.
   * However, the word "flaps" at the end was NOT extracted as an entity
   * because it is an "Event/Action" rather than a "Structural Asset."
   * This is where Python "Semantic Extractor" (Stage 2) will take over.
   */

  return 0;
}
