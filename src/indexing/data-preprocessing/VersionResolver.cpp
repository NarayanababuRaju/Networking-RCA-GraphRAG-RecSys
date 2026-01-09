#include <iostream>
#include <regex>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

/**
 * @brief Version & Applicability Resolver for Networking Docs.
 * Responsible for extracting RFC numbers, Obsoletes/Updates links,
 * software versions (IOS-XR, JunOS), and hardware signatures.
 */
class VersionResolver {
public:
  struct ApplicabilityContext {
    std::string rfcNumber;
    std::string obsoletes;
    std::string updates;
    std::set<std::string> osVersions;
    std::set<std::string> hardwarePlatforms;
  };

  /**
   * @brief Scans technical text to extract versioning and compatibility
   * context.
   */
  ApplicabilityContext resolve(const std::string &text) {
    ApplicabilityContext ctx;

    ctx.rfcNumber = extractPattern(text, R"(RFC\s*(\d+))");
    ctx.obsoletes = extractPattern(text, R"(Obsoletes:\s*RFC\s*(\d+))");
    ctx.updates = extractPattern(text, R"(Updates:\s*RFC\s*(\d+))");

    // Extract OS Versions (e.g., IOS-XR 7.1, JunOS 21.4)
    ctx.osVersions = extractAll(
        text, R"((IOS-XR|JunOS|Cisco\s*IOS|NX-OS)\s*(\d+\.\d+[\.\d+]*))");

    // Extract Hardware signatures (e.g., Jericho2, Trident+, ASIC, NCS-5500)
    ctx.hardwarePlatforms = extractAll(
        text,
        R"(\b(Jericho\d*|Trident[+\d]*|NCS-\d+|ASR-\d+|Linecard|ASIC)\b)");

    return ctx;
  }

  /**
   * @brief Pretty prints the context for verification.
   */
  void printContext(const ApplicabilityContext &ctx) {
    std::cout << "--- Version Applicability Matrix ---" << std::endl;
    if (!ctx.rfcNumber.empty())
      std::cout << "[RFC ID]:   " << ctx.rfcNumber << std::endl;
    if (!ctx.obsoletes.empty())
      std::cout << "[OBSOLETES]: " << ctx.obsoletes << std::endl;
    if (!ctx.updates.empty())
      std::cout << "[UPDATES]:   " << ctx.updates << std::endl;

    if (!ctx.osVersions.empty()) {
      std::cout << "[SOFTWARE]:  ";
      for (const auto &v : ctx.osVersions)
        std::cout << v << " ";
      std::cout << std::endl;
    }

    if (!ctx.hardwarePlatforms.empty()) {
      std::cout << "[HARDWARE]:  ";
      for (const auto &hw : ctx.hardwarePlatforms)
        std::cout << hw << " ";
      std::cout << std::endl;
    }
  }

private:
  /**
   * @brief Extracts first match of a captured group.
   */
  std::string extractPattern(const std::string &text,
                             const std::string &regexStr) {
    std::regex pattern(regexStr, std::regex_constants::icase);
    std::smatch match;
    if (std::regex_search(text, match, pattern) && match.size() > 1) {
      return match[1].str();
    }
    return "";
  }

  /**
   * @brief Extracts all occurrences of a pattern.
   */
  std::set<std::string> extractAll(const std::string &text,
                                   const std::string &regexStr) {
    std::set<std::string> results;
    std::regex pattern(regexStr, std::regex_constants::icase);
    auto words_begin = std::sregex_iterator(text.begin(), text.end(), pattern);
    auto words_end = std::sregex_iterator();

    for (std::sregex_iterator i = words_begin; i != words_end; ++i) {
      results.insert(i->str());
    }
    return results;
  }
};

int main() {
  VersionResolver resolver;

  // Test Case 1: RFC Header style
  std::string rfcText = "RFC 4271 - A Border Gateway Protocol 4 (BGP-4). "
                        "Obsoletes: RFC 1771. Updates: RFC 1654.";

  // Test Case 2: Vendor Release Note style
  std::string vendorText =
      "In IOS-XR 7.1.1, the Jericho2 linecard supports enhanced BGP-LS. Not "
      "applicable for NCS-5500 with older ASICs.";

  std::cout << "🚀 Test Case 1 (Standard RFC):" << std::endl;
  resolver.printContext(resolver.resolve(rfcText));

  std::cout << "\n🚀 Test Case 2 (Vendor Implementation):" << std::endl;
  resolver.printContext(resolver.resolve(vendorText));

  return 0;
}
