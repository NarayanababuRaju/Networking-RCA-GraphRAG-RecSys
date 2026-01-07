#include <iostream>
#include <regex>
#include <set>
#include <string>
#include <vector>

/**
 * @brief Negative Knowledge & Exception Tagger.
 * Identifies prohibitions (MUST NOT), deprecations, and exceptions in technical
 * text. This acts as the "Safety Guardrail" for the RCA system.
 */
class NegationTagger {
public:
  struct Constraint {
    std::string type;   // PROHIBITION, DEPRECATION, EXCEPTION
    std::string phrase; // The actual text anchor
    bool isCritical;    // True for MUST NOT/NOT SUPPORTED
  };

  /**
   * @brief Scans text for negative constraints.
   */
  std::vector<Constraint> scan(const std::string &text) {
    std::vector<Constraint> constraints;

    // 1. Detect Prohibitions (MUST NOT, SHOULD NOT, NOT SUPPORTED)
    std::regex prohib(R"(\b(MUST NOT|SHOULD NOT|NOT SUPPORTED|NEVER|DO NOT)\b)",
                      std::regex_constants::icase);
    auto prohib_it = std::sregex_iterator(text.begin(), text.end(), prohib);
    while (prohib_it != std::sregex_iterator()) {
      constraints.push_back({"PROHIBITION", prohib_it->str(), true});
      prohib_it++;
    }

    // 2. Detect Deprecations
    std::regex deprec(R"(\b(DEPRECATED|OBSOLETE|LEGACY|DISCONTINUED)\b)",
                      std::regex_constants::icase);
    auto deprec_it = std::sregex_iterator(text.begin(), text.end(), deprec);
    while (deprec_it != std::sregex_iterator()) {
      constraints.push_back({"DEPRECATION", deprec_it->str(), false});
      deprec_it++;
    }

    // 3. Detect Exceptions/Exclusions
    std::regex except(
        R"(\b(EXCEPT|UNLESS|NOT APPLICABLE|WITH THE EXCEPTION OF)\b)",
        std::regex_constants::icase);
    auto except_it = std::sregex_iterator(text.begin(), text.end(), except);
    while (except_it != std::sregex_iterator()) {
      constraints.push_back({"EXCEPTION", except_it->str(), false});
      except_it++;
    }

    return constraints;
  }

  void printResults(const std::vector<Constraint> &constraints) {
    std::cout << "--- Safety Constraints Found ---" << std::endl;
    if (constraints.empty()) {
      std::cout << "No constraints detected (Positive knowledge)." << std::endl;
      return;
    }

    for (const auto &c : constraints) {
      std::cout << "[" << c.type << "] marker: \"" << c.phrase << "\""
                << (c.isCritical ? " [CRITICAL]" : "") << std::endl;
    }
  }
};

int main() {
  NegationTagger tagger;

  std::string text1 = "The BGP speaker MUST NOT send a NOTIFICATION message if "
                      "the session is Idle.";
  std::string text2 = "This configuration is DEPRECATED and NOT SUPPORTED on "
                      "newer linecards, UNLESS explicitly enabled.";

  std::cout << "🚀 Testing Case 1 (Protocol Prohibition):" << std::endl;
  tagger.printResults(tagger.scan(text1));

  std::cout << "\n🚀 Testing Case 2 (Hardware Exception):" << std::endl;
  tagger.printResults(tagger.scan(text2));

  return 0;
}
