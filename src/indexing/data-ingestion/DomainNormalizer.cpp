#include <iostream>
#include <regex>
#include <string>
#include <unordered_map>
#include <vector>

/**
 * @brief Production-grade Domain Normalizer for Networking.
 * Canonicalizes networking aliases (Interface names, Protocols, States)
 * to ensure high-accuracy Entity Extraction and Graph consistency.
 */
class DomainNormalizer {
public:
  DomainNormalizer() {
    // 1. Interface Aliases (Cisco/Juniper style)
    interfaceMap = {{"Gi", "GigabitEthernet"}, {"Te", "TenGigabitEthernet"},
                    {"Fa", "FastEthernet"},    {"Eth", "Ethernet"},
                    {"Po", "Port-Channel"},    {"Lo", "Loopback"}};

    // 2. Protocol Normalization
    protocolMap = {{"BGP-4", "BGP"},
                   {"BGPv4", "BGP"},
                   {"Border Gateway Protocol", "BGP"},
                   {"OSPFv2", "OSPF"},
                   {"OSPFv3", "OSPF-v3"}};

    // 3. State/Status Normalization
    stateMap = {{"Established", "UP"},
                {"Down", "DOWN"},
                {"Shut", "SHUTDOWN"},
                {"Active", "UP"},
                {"Idle", "IDLE"}};
  }

  /**
   * @brief Performs a full normalization pass on technical text.
   */
  std::string normalize(const std::string &input) {
    std::string text = input;

    text = normalizeInterfaces(text);
    text = normalizeProtocols(text);
    text = normalizeStates(text);

    return text;
  }

private:
  std::unordered_map<std::string, std::string> interfaceMap;
  std::unordered_map<std::string, std::string> protocolMap;
  std::unordered_map<std::string, std::string> stateMap;

  /**
   * @brief Expands short interface names (e.g., Gi1/1 -> GigabitEthernet1/1).
   */
  std::string normalizeInterfaces(const std::string &input) {
    std::string result = input;
    for (const auto &[alias, full] : interfaceMap) {
      // Regex to catch Gi1/1 or Te0/0/1, avoiding Gi in middle of words
      std::regex pattern(R"(\b)" + alias + R"((\d+[\/\d+]*)\b)");
      result = std::regex_replace(result, pattern, full + "$1");
    }
    return result;
  }

  /**
   * @brief Maps protocol variations to a standard canonical name.
   */
  std::string normalizeProtocols(const std::string &input) {
    std::string result = input;
    for (const auto &[variation, canonical] : protocolMap) {
      std::regex pattern(R"(\b)" + variation + R"(\b)",
                         std::regex_constants::icase);
      result = std::regex_replace(result, pattern, canonical);
    }
    return result;
  }

  /**
   * @brief Normalizes diverse state terminology into a unified ENUM-like set.
   */
  std::string normalizeStates(const std::string &input) {
    std::string result = input;
    for (const auto &[term, standard] : stateMap) {
      std::regex pattern(R"(\b)" + term + R"(\b)", std::regex_constants::icase);
      result = std::regex_replace(result, pattern, standard);
    }
    return result;
  }
};

int main() {
  DomainNormalizer normalizer;

  std::vector<std::string> testCases = {
      "Interface Gi1/1 is Down due to a BGP-4 failure.",
      "Te0/0/1 state changed to Established.",
      "Border Gateway Protocol is session Idle on Lo0.",
      "Check Ethernet port Eth4/2 status."};

  std::cout << "--- Networking Domain Normalization Test ---" << std::endl;
  for (const auto &test : testCases) {
    std::cout << "\n[Raw]:  " << test << std::endl;
    std::cout << "[Norm]: " << normalizer.normalize(test) << std::endl;
  }

  return 0;
}
