#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

/**
 * @struct ResolvedEntity
 * @brief Represents an entity after disambiguation.
 */
struct ResolvedEntity {
  std::string originalTerm;
  std::string resolvedSense;
  double confidence;
};

/**
 * @class Disambiguator
 * @brief Context-aware entity disambiguation for networking terms.
 *
 * Disambiguation is the art of distinguishing "BGP" (the protocol standard)
 * from "BGP" (a specific process instance on a router).
 *
 * TRADE-OFF ANALYSIS:
 * ------------------
 * 1. METHOD: Context Window vs. Global Embedding
 *    - PRO: Context windows (this implementation) are O(W) where W is window
 * size. Extremely fast and requires no GPU.
 *    - CON: Can be fooled by complex sentences where the 'Sense' marker is far
 *      from the term.
 *
 * 2. KNOWLEDGE BASE: Rigid Dictionary vs. LLM
 *    - PRO: Expert-defined keyword maps ensure zero 'hallucination' in
 *      critical infrastructure.
 *    - CON: Needs manual updates for new technologies.
 */
class Disambiguator {
public:
  struct SenseProfile {
    std::string label;
    std::vector<std::string> keywords;
    double weight;
  };

  Disambiguator() {
    // Define common ambiguous networking terms and their 'Sense Profiles'

    // Term: "Session"
    profiles["session"] = {
        {"PROTOCOL_INSTANCE",
         {"bgp", "ospf", "established", "neighbor", "keepalive", "holdtime"},
         1.0},
        {"USER_ACCESS",
         {"terminal", "ssh", "telnet", "login", "vty", "console"},
         0.8}};

    // Term: "Interface"
    profiles["interface"] = {
        {"PHYSICAL_PORT",
         {"gigabit", "tengig", "optic", "cable", "plugged", "slot"},
         1.0},
        {"LOGICAL_CONFIG",
         {"vlan", "tunnel", "loopback", "subinterface", "virtual"},
         0.9}};

    // Term: "Reset"
    profiles["reset"] = {{"PROTOCOL_EVENT",
                          {"notification", "peer", "collision", "fsm", "state"},
                          1.0},
                         {"HARDWARE_ACTION",
                          {"button", "power", "reload", "chassis", "voltage"},
                          1.1}};
  }

  /**
   * @brief Resolves the specific sense of a term based on its surrounding
   * context.
   * @param term The ambiguous term to resolve.
   * @param contextWindow The words surrounding the term.
   */
  ResolvedEntity resolve(const std::string &term,
                         const std::string &contextWindow) {
    std::string lowerTerm = term;
    std::transform(lowerTerm.begin(), lowerTerm.end(), lowerTerm.begin(),
                   ::tolower);

    if (profiles.find(lowerTerm) == profiles.end()) {
      return {term, "UNKNOWN", 0.0};
    }

    std::string lowerContext = contextWindow;
    std::transform(lowerContext.begin(), lowerContext.end(),
                   lowerContext.begin(), ::tolower);

    std::string bestSense = "AMBIGUOUS";
    double maxScore = 0.0;

    for (const auto &profile : profiles[lowerTerm]) {
      double currentScore = 0.0;
      for (const auto &kw : profile.keywords) {
        if (lowerContext.find(kw) != std::string::npos) {
          currentScore += profile.weight;
        }
      }

      if (currentScore > maxScore) {
        maxScore = currentScore;
        bestSense = profile.label;
      }
    }

    // Normalize confidence (Max score relative to total possible weights found)
    double confidence = (maxScore > 0) ? std::min(1.0, maxScore / 2.0) : 0.0;

    return {term, bestSense, confidence};
  }

private:
  std::unordered_map<std::string, std::vector<SenseProfile>> profiles;
};

int main() {
  Disambiguator disambiguator;

  // Test Case 1: Protocol Session
  std::string term1 = "Session";
  std::string context1 =
      "The BGP neighbor reported a session reset due to holdtime expiry.";

  // Test Case 2: User Session
  std::string context2 =
      "User admin opened a new terminal session via SSH on VTY 0.";

  // Test Case 3: Physical Interface
  std::string term2 = "Interface";
  std::string context3 =
      "The Gigabit optic cable was removed from the interface.";

  std::cout << "--- Entity Disambiguation Test ---" << std::endl;

  auto res1 = disambiguator.resolve(term1, context1);
  std::cout << "[Term]: " << term1 << " | [Sense]: " << res1.resolvedSense
            << " | [Conf]: " << res1.confidence << std::endl;
  std::cout << "  Context: \"" << context1 << "\"\n" << std::endl;

  auto res2 = disambiguator.resolve(term1, context2);
  std::cout << "[Term]: " << term1 << " | [Sense]: " << res2.resolvedSense
            << " | [Conf]: " << res2.confidence << std::endl;
  std::cout << "  Context: \"" << context2 << "\"\n" << std::endl;

  auto res3 = disambiguator.resolve(term2, context3);
  std::cout << "[Term]: " << term2 << " | [Sense]: " << res3.resolvedSense
            << " | [Conf]: " << res3.confidence << std::endl;
  std::cout << "  Context: \"" << context3 << "\"\n" << std::endl;

  return 0;
}
