#include <iostream>
// nlohmann/json or JsonCpp would be used in a full production environment
#include <string>
#include <unordered_map>
#include <vector>

/**
 * @brief Professional Metadata Enricher for Networking Knowledge.
 * Adds source authority, versioning, and trust scores to technical chunks.
 */
class MetadataEnricher {
public:
  enum class SourceType { RFC, VENDOR_DOC, INTERNAL_SME, PUBLIC_BLOG, UNKNOWN };

  struct Metadata {
    std::string sourceId;
    SourceType type;
    double authorityScore;
    std::string softwareVersion;
    std::vector<std::string> domainTags;
  };

  MetadataEnricher() {
    // Initialize Authority Scoring Rules
    authorityRules[SourceType::RFC] = 1.0;
    authorityRules[SourceType::VENDOR_DOC] = 0.85;
    authorityRules[SourceType::INTERNAL_SME] = 0.75;
    authorityRules[SourceType::PUBLIC_BLOG] = 0.3;
    authorityRules[SourceType::UNKNOWN] = 0.1;
  }

  /**
   * @brief Enriches a text chunk with technical metadata.
   */
  std::string enrich(const std::string &text, const std::string &sourceName) {
    Metadata meta = identifySource(sourceName);

    // In a real C++ system, we would return a structured JSON string or
    // Protobuf object for ingestion into the Graph DB.
    std::string enrichedOutput = "--- METADATA START ---\n";
    enrichedOutput += "Source: " + meta.sourceId + "\n";
    enrichedOutput += "Type: " + typeToString(meta.type) + "\n";
    enrichedOutput +=
        "Authority Score: " + std::to_string(meta.authorityScore) + "\n";
    enrichedOutput += "Tags: ";
    for (const auto &tag : meta.domainTags)
      enrichedOutput += "[" + tag + "] ";
    enrichedOutput += "\n--- CONTENT ---\n";
    enrichedOutput += text;

    return enrichedOutput;
  }

private:
  std::unordered_map<SourceType, double> authorityRules;

  /**
   * @brief Logic to detect source type based on filename/string markers.
   */
  Metadata identifySource(const std::string &name) {
    Metadata m;
    m.sourceId = name;

    if (name.find("RFC") != std::string::npos) {
      m.type = SourceType::RFC;
      m.domainTags = {"Standard", "Protocol", "Protocol-Grammar"};
    } else if (name.find("Cisco") != std::string::npos ||
               name.find("Juniper") != std::string::npos) {
      m.type = SourceType::VENDOR_DOC;
      m.domainTags = {"Hardware", "Implementation", "Vendor-Specific"};
    } else if (name.find("KB") != std::string::npos ||
               name.find("Internal") != std::string::npos) {
      m.type = SourceType::INTERNAL_SME;
      m.domainTags = {"Troubleshooting", "Experience-Based", "Best-Practice"};
    } else {
      m.type = SourceType::PUBLIC_BLOG;
      m.domainTags = {"Opinion", "Community-Fix"};
    }

    m.authorityScore = authorityRules[m.type];
    return m;
  }

  std::string typeToString(SourceType t) {
    switch (t) {
    case SourceType::RFC:
      return "RFC (Gold Standard)";
    case SourceType::VENDOR_DOC:
      return "Vendor Specification";
    case SourceType::INTERNAL_SME:
      return "Internal SME Knowledge";
    case SourceType::PUBLIC_BLOG:
      return "External Community Blog";
    default:
      return "Unknown";
    }
  }
};

int main() {
  MetadataEnricher enricher;

  std::string rfcContent = "BGP Keepalive timer should be set to 60 seconds.";
  std::string blogContent = "Hey everyone, I found that setting BGP keepalive "
                            "to 1s makes things super fast!";

  std::cout << "🚀 Enriching RFC Source:" << std::endl;
  std::cout << enricher.enrich(rfcContent, "IETF-RFC-4271.txt") << std::endl;

  std::cout << "\n🚀 Enriching Blog Source:" << std::endl;
  std::cout << enricher.enrich(blogContent, "FastBGP-Blog-Post.html")
            << std::endl;

  return 0;
}
