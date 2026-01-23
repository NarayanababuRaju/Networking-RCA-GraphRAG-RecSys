import json
import os
import time

class KnowledgeSynthesizer:
    """
    Stage 3: Knowledge Synthesis.
    
    Uses an LLM to synthesize technical biographies into structured JSON briefs.
    Supports both real LLM backends (OpenAI/Ollama) and a Mock mode for verification.
    """

    def __init__(self, mode="mock", model="mistral"):
        self.mode = mode
        self.model = model
        print(f"Knowledge Synthesizer initialized (Mode: {mode}, Model: {model})")

    def synthesize(self, context_path):
        """
        Processes the technical biographies and generates Knowledge Briefs.
        """
        print(f"Synthesizing knowledge from {context_path}...")
        
        # 1. Load context
        with open(context_path, 'r') as f:
            community_context = json.load(f)

        briefs = {}

        for comm_id, profiles in community_context.items():
            print(f"Synthesizing Brief for Community {comm_id}...")
            
            # Construct the prompt context
            context_string = self._build_prompt_context(profiles)
            
            # Call LLM (Real or Mock)
            if self.mode == "mock":
                brief = self._mock_synthesis(comm_id, profiles)
            else:
                brief = self._llm_synthesis(context_string)
                
            briefs[comm_id] = brief

        return briefs

    def _build_prompt_context(self, profiles):
        """Converts profiles into a text block for the LLM prompt."""
        context_blocks = []
        for p in profiles:
            block = f"Node ID: {p['node_id']}\nRole: {p['biography']}\nRelationships:\n"
            block += "\n".join([f" - {r}" for r in p['relationships']])
            context_blocks.append(block)
        return "\n---\n".join(context_blocks)

    def _mock_synthesis(self, comm_id, profiles):
        """Generates a deterministic mock brief for testing."""
        # Detect themes from biographies
        all_text = " ".join([p['biography'] for p in profiles]).lower()
        
        if "bgp" in all_text:
            title = "BGP Routing & Peer Stability"
            summary = "Focuses on BGP adjacency states and timer-based failures."
        elif "mtu" in all_text or "packet" in all_text:
            title = "Physical & L2 Interface Constraints"
            summary = "Concerns MTU mismatches and packet drop scenarios."
        else:
            title = f"Fault Domain {comm_id}"
            summary = "A technical cluster identified by graph topology."

        return {
            "title": title,
            "summary": summary,
            "symptoms": [p['biography'] for p in profiles[:3]],
            "potential_causes": ["Configuration Mismatch", "Hardware Fault", "Protocol Timeout"],
            "confidence_score": 0.85
        }

    def _llm_synthesis(self, context_string):
        """Placeholder for real LLM integration (Ollama/OpenAI)."""
        # In a real implementation, you would use requests.post to Ollama 
        # or the openai-python client.
        print("Real LLM call not configured. Falling back to Mock.")
        return self._mock_synthesis("N/A", [])

    def save_briefs(self, briefs, output_path):
        """Persists the Knowledge Briefs to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(briefs, f, indent=4)
        print(f"Successfully synthesized {len(briefs)} Knowledge Briefs. Saved to {output_path}")

if __name__ == "__main__":
    # 🔬 Verification Script
    synthesizer = KnowledgeSynthesizer(mode="mock")
    
    # Path relative to summarization folder
    context_file = "data/processed/community_context.json"
    
    if os.path.exists(context_file):
        briefs = synthesizer.synthesize(context_file)
        
        print("\n--- Knowledge Brief Sample (Community 0) ---")
        if "0" in briefs:
            print(json.dumps(briefs["0"], indent=4))
            
        synthesizer.save_briefs(briefs, "data/processed/community_briefs.json")
    else:
        print(f"Error: Context file {context_file} not found. Run ContextBuilder.py first.")
