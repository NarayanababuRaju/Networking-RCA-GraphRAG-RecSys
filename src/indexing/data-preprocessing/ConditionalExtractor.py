import re
import json

class ConditionalExtractor:
    """
    Advanced Logic Extractor for Networking Knowledge.
    Transforms conditional English prose into structured 'If-Then' logic.
    """
    def __init__(self):
        # Triggers for conditions
        self.condition_triggers = [
            r"if\s+(.*?),", 
            r"when\s+(.*?),", 
            r"unless\s+(.*?),",
            r"until\s+(.*?),",
            r"once\s+(.*?),"
        ]
        
        # Outcomes typically follow the comma in the triggers above
        # or follow keywords like "then", "the speaker shall", "the session will"
        self.outcome_markers = [
            r"then\s+(.*)",
            r"the\s+speaker\s+shall\s+(.*)",
            r"the\s+session\s+will\s+(.*)",
            r"must\s+(.*)",
            r"results\s+in\s+(.*)"
        ]

    def extract(self, text):
        results = []
        # Split text into sentences for more precise extraction
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            logic = self._parse_sentence(sentence)
            if logic:
                results.append(logic)
        
        return results

    def _parse_sentence(self, sentence):
        logic = {"raw": sentence, "condition": None, "outcome": None, "trigger_word": None}
        
        # Find Condition
        for pattern in self.condition_triggers:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                logic["condition"] = match.group(1).strip()
                logic["trigger_word"] = re.search(r"^\w+", pattern.split("\\s+")[0]).group(0) # Extract "if", "when", etc.
                
                # Try to find outcome in the remaining part of the sentence
                remainder = sentence[match.end():].strip()
                for o_pattern in self.outcome_markers:
                    o_match = re.search(o_pattern, remainder, re.IGNORECASE)
                    if o_match:
                        logic["outcome"] = o_match.group(1).strip()
                        break
                
                # If no specific outcome marker, use the whole remainder
                if not logic["outcome"]:
                    logic["outcome"] = remainder
                
                return logic
        
        return None

if __name__ == "__main__":
    extractor = ConditionalExtractor()
    
    test_texts = [
        "If the HOLD_TIMER expires before KEEPALIVE is received, the speaker shall send a NOTIFICATION.",
        "Unless the session is in Established state, the KEEPALIVE messages are ignored.",
        "When a BGP-4 session starts, the open message is sent."
    ]
    
    print("🧠 --- Conditional Logic Extraction ---")
    for text in test_texts:
        logic_list = extractor.extract(text)
        for logic in logic_list:
            print(f"\n[Source]: {logic['raw']}")
            print(f"  └─ TRIGGER:   {logic['trigger_word'].upper()}")
            print(f"  └─ CONDITION: {logic['condition']}")
            print(f"  └─ OUTCOME:   {logic['outcome']}")
