#include <ctime>
#include <iostream>
#include <regex>
#include <string>
#include <vector>

/**
 * @brief Temporal & Stability Signal Annotator.
 * Extracts dates, document status (Proposed, Draft, Standard), and
 * calculates the 'Knowledge Decay' factor.
 */
class TemporalAnnotator {
public:
  struct TemporalSignal {
    std::string dateStr;
    std::string status;    // Draft, Proposed Standard, Internet Standard
    double stabilityScore; // 0.0 (unstable/draft) to 1.0 (long-term stable)
    int yearsOld;
  };

  /**
   * @brief Extracts time-based signals and determines knowledge stability.
   */
  TemporalSignal annotate(const std::string &text) {
    TemporalSignal signal;
    signal.dateStr = extractPattern(
        text,
        R"(\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b)");

    // Determine status
    if (regexMatch(text, R"(\bInternet Standard\b)")) {
      signal.status = "Internet Standard";
      signal.stabilityScore = 1.0;
    } else if (regexMatch(text, R"(\bProposed Standard\b)")) {
      signal.status = "Proposed Standard";
      signal.stabilityScore = 0.8;
    } else if (regexMatch(text, R"(\b(Draft|Internet-Draft)\b)")) {
      signal.status = "Draft";
      signal.stabilityScore = 0.3;
    } else {
      signal.status = "Informational / Unknown";
      signal.stabilityScore = 0.5;
    }

    // Calculate age (Simplified)
    if (!signal.dateStr.empty()) {
      std::regex yearPattern(R"(\d{4})");
      std::smatch m;
      if (std::regex_search(signal.dateStr, m, yearPattern)) {
        int pubYear = std::stoi(m[0].str());
        int currentYear = 2026; // Simulated current year based on context
        signal.yearsOld = currentYear - pubYear;

        // Decay stability for extremely old documents unless they are Internet
        // Standards
        if (signal.yearsOld > 15 && signal.status != "Internet Standard") {
          signal.stabilityScore *= 0.7;
        }
      }
    }

    return signal;
  }

  void printResults(const TemporalSignal &s) {
    std::cout << "--- Temporal Intelligence ---" << std::endl;
    std::cout << "[Publication Date]: "
              << (s.dateStr.empty() ? "Unknown" : s.dateStr) << std::endl;
    std::cout << "[Document Status]:   " << s.status << std::endl;
    std::cout << "[Stability Score]:   " << s.stabilityScore << " (Scale 0-1)"
              << std::endl;
    std::cout << "[Knowledge Age]:     " << s.yearsOld << " years" << std::endl;
  }

private:
  std::string extractPattern(const std::string &text,
                             const std::string &regexStr) {
    std::regex pattern(regexStr, std::regex_constants::icase);
    std::smatch match;
    if (std::regex_search(text, match, pattern))
      return match[0].str();
    return "";
  }

  bool regexMatch(const std::string &text, const std::string &regexStr) {
    std::regex pattern(regexStr, std::regex_constants::icase);
    return std::regex_search(text, pattern);
  }
};

int main() {
  TemporalAnnotator annotator;

  std::string text1 =
      "RFC 4271 - BGP - January 2006. Category: Draft Standard.";
  std::string text2 =
      "Internet-Draft: BGP Flowspec Extensions. September 2023. Status: Draft.";

  std::cout << "🚀 Testing Case 1 (Mature Protocol):" << std::endl;
  annotator.printResults(annotator.annotate(text1));

  std::cout << "\n🚀 Testing Case 2 (Emerging Technology):" << std::endl;
  annotator.printResults(annotator.annotate(text2));

  return 0;
}
