# PHASE 0 — PROJECT DEFINITION
## TASK 00 — FREEZE THE PROJECT SCOPE

**Project:** Environmental Intelligence System for the Darukaa.Earth AI Biodiversity Intelligence challenge.
**Status:** FROZEN 🧊
**Date:** 2026-09-16

This document serves as the governing architecture principle for the entire project. All subsequent development must adhere to these rules.

---

### 1. PROJECT IDENTITY

**PROJECT TYPE:** Environmental Intelligence System

The system must behave like an AI environmental scientist that:
- understands environmental data,
- identifies relationships between environmental variables,
- retrieves relevant scientific/environmental knowledge,
- evaluates evidence,
- reasons across multiple environmental variables,
- identifies ecological risks,
- and produces specific, scientifically grounded interventions.

This is **NOT** primarily a conversational AI application.

---

### 2. WHAT WE ARE NOT BUILDING

**STRICTLY DO NOT TURN THE PROJECT INTO:**
- ❌ Generic chatbot
- ❌ LLM wrapper
- ❌ Simple RAG chatbot
- ❌ Question-answering bot over documents
- ❌ Static recommendation engine
- ❌ Hardcoded rule-based recommendation system
- ❌ UI-only project
- ❌ Dashboard that only displays environmental statistics
- ❌ System that generates recommendations without explaining the environmental reasoning
- ❌ System where the LLM invents scientific facts without evidence

The LLM is a reasoning component, NOT the intelligence source by itself.

---

### 3. CORE INTELLIGENCE PIPELINE

Every major environmental assessment must conceptually follow:

```
Environmental Data
        ↓
Risk / Relationship Analysis
        ↓
Scientific Knowledge Retrieval
        ↓
Evidence Extraction
        ↓
Multi-Metric Environmental Reasoning
        ↓
Specific Intervention
        ↓
Expected Environmental Impact
        ↓
Evidence / Confidence
```

Implement the architecture so these stages are distinguishable. Do not collapse the entire pipeline into one LLM prompt.

---

### 4. CONVERSATIONAL CLARIFICATION

The system must identify incomplete environmental input and ask relevant clarifying questions before producing a major environmental assessment when necessary.

**Requirements:**
- The system must detect missing or insufficient environmental information.
- It should ask targeted clarification questions for the missing variables.
- Questions should be relevant to the user's environmental context.
- It must not fabricate missing environmental values.
- If sufficient information is available, it should proceed without unnecessary questions.
- The clarification process must support the environmental intelligence pipeline rather than turning the system into a generic chatbot.

**Example:**
*User:* "Biodiversity is declining on my land."
*System:* "To assess the likely causes, please provide: soil organic carbon, rainfall pattern, and land-use type."
The system should then use the provided information in subsequent reasoning.

---

### 5. MULTI-TURN MEMORY / CONTEXT

The system must support multi-turn environmental conversations and retain relevant context.

**Requirements:**
- The system should remember relevant environmental information provided earlier in the conversation.
- Later questions should be interpreted using previously provided environmental context when applicable.
- The system should avoid repeatedly asking for information that is already available.
- Memory must be scoped to relevant environmental/project context.
- New information provided by the user should update or refine the existing context.
- Memory must never be used to invent environmental measurements or scientific facts.
- The reasoning engine must receive the relevant structured context rather than relying on an uncontrolled conversational history alone.

**Example:**
*Turn 1:* User provides rainfall, soil carbon, land-use and location.
*Turn 2:* User asks: "What should I change?"
The system should use the environmental information from Turn 1 when generating the assessment.

---

### 6. TEXT INPUT

**TEXT INPUT IS MANDATORY.**

The system must accept natural-language environmental descriptions from users.

**Examples:**
- "My farmland has low soil organic carbon and rainfall has decreased."
- "Vegetation has declined in this region."
- "Biodiversity is decreasing around this forest."
- "What could be causing habitat degradation here?"

**Requirements:**
- The system must extract relevant environmental entities, variables, observations, locations, time periods, and contextual information from the text where possible.
- Text extraction must NOT create measurements that were not provided.
- Extracted information should be converted into structured data that can be passed to the environmental analysis pipeline.

---

### 7. STRUCTURED INPUT / JSON

The system must support structured environmental input in JSON or an equivalent structured format.

**Example:**
```json
{
  "location": "Example Region",
  "soil": {
    "organic_carbon": 0.3,
    "ph": 6.2,
    "moisture": 18
  },
  "climate": {
    "rainfall": 420,
    "temperature": 31
  },
  "land_use": "monoculture"
}
```

**Requirements:**
- Structured input must be validated before analysis.
- Missing fields must be identified explicitly.
- Invalid values must not silently become environmental measurements.
- Structured data should feed directly into the data validation and environmental analysis pipeline.
- The system must preserve units and metadata where available.
- Structured input and text input should ultimately be convertible into a common internal environmental representation.

---

### 8. ENVIRONMENTAL DATA

The system should be capable of working with multiple environmental variables. Examples include:
- Rainfall, Temperature
- Soil Organic Carbon, Soil Moisture, Soil pH
- Land Use / Land Cover
- Vegetation Index, NDVI, Vegetation density
- Elevation, Slope
- Water availability
- Biodiversity indicators, Species richness, Species abundance
- Habitat fragmentation, Forest cover
- Pollution indicators, Climate variables, Human disturbance indicators

The exact variables depend on available datasets.

**Rules:**
- Do NOT fabricate environmental measurements.
- If data is missing: explicitly identify the missing variable, continue with available evidence where scientifically valid, and avoid pretending that unavailable data exists.

---

### 9. MULTI-VARIABLE REASONING — CRITICAL

This is one of the most important requirements.

When sufficient environmental data exists, every major recommendation should reason across **AT LEAST 3** environmental variables.

**Example:**
`Rainfall + Soil Organic Carbon + Land Use + Species Richness` → `Integrated ecological assessment` → `Specific intervention`

The system should NOT produce: *"Rainfall is low, therefore plant more trees."*
Instead, it should reason about relationships such as rainfall conditions, soil condition, land-use pressure, biodiversity condition, and habitat suitability, and determine how these variables interact before generating an intervention.

The number of variables should be data-driven. If only two meaningful variables are available, do not fabricate a third simply to satisfy the requirement.

---

### 10. RELATIONSHIP ANALYSIS

The system must analyze relationships between environmental variables rather than treating each metric independently.

**Examples:**
- `Rainfall ↔ Soil Moisture`
- `Rainfall + Temperature → Water Stress`
- `Land Use + Habitat Fragmentation → Biodiversity Risk`
- `Soil Organic Carbon + Land Use → Soil Degradation Risk`
- `Vegetation Density + Rainfall + Temperature → Vegetation Stress`
- `Species Richness + Habitat Fragmentation + Land Cover → Biodiversity Pressure`
- `NDVI Change + Rainfall + Land Use → Vegetation Change Interpretation`

The system should identify meaningful relationships using thresholds where scientifically justified, correlations, trends, changes over time, spatial relationships, derived indicators, domain knowledge, or other appropriate analytical methods.

**Rule:** Do NOT invent correlations.

---

### 11. SCIENTIFIC KNOWLEDGE RETRIEVAL

Scientific/environmental knowledge must be retrieved from a grounded knowledge source whenever possible.

**Potential sources:** peer-reviewed research, government environmental datasets, biodiversity databases, recognized scientific organizations, ecological reports, climate datasets, conservation literature, authoritative environmental documentation.

The retrieval layer should provide relevant evidence for the environmental reasoning. The system should answer: *"What scientific evidence supports this interpretation?"* rather than simply *"What does the LLM think?"*

---

### 12. EVIDENCE

Major environmental conclusions should be traceable to evidence. For each important assessment, aim to provide:
1. environmental observation
2. detected relationship
3. scientific evidence
4. interpretation
5. intervention
6. expected impact

Where possible, expose evidence to the user through: source name, title, publication/organization, year, relevant evidence snippet or summarized finding, and source link.

**Rules:**
- Do not generate fake citations.
- If reliable evidence cannot be found, clearly state that evidence is limited.

---

### 13. REASONING LAYER

The reasoning engine must combine:
1. Actual environmental data
2. Derived metrics
3. Environmental relationships
4. Retrieved scientific knowledge
5. Ecological context
6. Risk assessment

The LLM may be used to synthesize and explain the reasoning, but it must receive structured environmental evidence as input.

Avoid prompts such as: *"Analyze this area and give recommendations."*
Instead, provide structured inputs (Observations, Derived Indicators, Detected Relationships, Scientific Evidence) and ask the reasoning layer to produce a scientifically grounded assessment.

---

### 14. INTERVENTION GENERATION

Recommendations must be:
- specific, location/context aware
- tied to measured environmental conditions
- connected to identified risks
- supported by evidence
- actionable
- and explain WHY the intervention is appropriate.

Avoid generic recommendations such as: ❌ "Plant more trees." ❌ "Protect biodiversity."

**Example Structure:**
- **INTERVENTION:** Restore native vegetation in degraded habitat corridors.
- **WHY:** High habitat fragmentation + declining vegetation condition + reduced species richness indicate increasing habitat pressure.
- **TARGET:** Specific degraded/fragmented zones.
- **METHOD:** Use locally appropriate native species and restore corridor connectivity.
- **EXPECTED EFFECT:** Improved habitat continuity and potential biodiversity recovery.
- **EVIDENCE:** Relevant ecological research / authoritative source.

---

### 15. NO STATIC RECOMMENDATION ENGINE

Do NOT hardcode: `IF rainfall < X THEN recommend Y.`

Rules may be used as supporting analytical logic where scientifically justified, but the final assessment must integrate: `environmental data + relationships + scientific evidence + context + reasoning.`

The architecture must allow recommendations to change when environmental data changes.

---

### 16. TEMPORAL REASONING

Where historical data exists, analyze change over time (e.g., NDVI trend, rainfall trend, biodiversity trend).
Do not only analyze a single snapshot when temporal data is available.

---

### 17. SPATIAL REASONING

Where spatial information exists, use it. The system should be able to reason about geographic zones, habitat patches, land-use regions, environmental hotspots, degraded areas, etc.
Recommendations should ideally identify WHERE an intervention is most relevant.

---

### 18. OUTPUT STRUCTURE

A major environmental assessment should follow this structure:
1. **ENVIRONMENTAL STATUS:** Summarize the observed environmental conditions.
2. **KEY VARIABLES:** List the important environmental variables used.
3. **DETECTED RELATIONSHIPS:** Explain how the variables interact.
4. **RISK ASSESSMENT:** Identify the environmental/ecological risk.
5. **SCIENTIFIC EVIDENCE:** Show the supporting knowledge retrieved from reliable sources.
6. **INTEGRATED REASONING:** Explain how the evidence and environmental variables lead to the conclusion.
7. **SPECIFIC INTERVENTION:** Give an actionable intervention.
8. **EXPECTED IMPACT:** Explain what environmental improvement is expected.
9. **CONFIDENCE / LIMITATIONS:** Explain data limitations and uncertainty.

---

### 19. AI ENVIRONMENTAL SCIENTIST BEHAVIOR

The system should behave like:
`DATA SCIENTIST + ECOLOGIST + ENVIRONMENTAL ANALYST + RESEARCH ASSISTANT + DECISION SUPPORT SYSTEM`

The goal is: *"Use AI to understand environmental systems and support evidence-based ecological decisions."*
NOT: *"Use an LLM to answer environmental questions."*

---

### 20. ARCHITECTURE PRINCIPLE

Maintain clear separation between layers:
`TEXT / STRUCTURED INPUT` → `INPUT VALIDATION` → `CONTEXT / MEMORY` → `DATA PROCESSING` → `FEATURE / METRIC ENGINE` → `RELATIONSHIP ANALYSIS` → `RISK DETECTION` → `SCIENTIFIC RETRIEVAL` → `EVIDENCE PROCESSING` → `REASONING ENGINE` → `INTERVENTION ENGINE` → `EXPLANATION / VISUALIZATION`

Each layer should have a clear responsibility. Do not put all intelligence into frontend code or a single backend LLM call.

Conversational clarification should occur whenever required information is missing. Multi-turn memory should provide relevant previously supplied context to the pipeline.

---

### 21. ANTI-HALLUCINATION REQUIREMENT

The system must NEVER:
- fabricate environmental values, species, scientific papers, citations.
- claim unsupported ecological relationships.
- claim certainty when evidence is insufficient.

When information is uncertain: **STATE THE UNCERTAINTY.**

---

### 22. ACCEPTANCE TEST

Before considering any major feature complete, verify:
- [ ] Does it use real/available environmental data?
- [ ] Does it analyze environmental relationships?
- [ ] Does it use 3+ environmental variables when sufficient data exists?
- [ ] Does it retrieve relevant scientific/environmental knowledge?
- [ ] Is the evidence traceable?
- [ ] Does reasoning combine the data and evidence?
- [ ] Is the recommendation specific rather than generic?
- [ ] Does the recommendation change when environmental conditions change?
- [ ] Does the system explain WHY the recommendation was generated?
- [ ] Does it identify uncertainty or missing data?
- [ ] Is the feature more than a chatbot response?
- [ ] Does the system support natural-language text input?
- [ ] Does the system support structured input such as JSON?
- [ ] Does the system validate structured environmental input?
- [ ] Does the system identify missing environmental information?
- [ ] Does the system ask relevant clarification questions when necessary?
- [ ] Does the system retain relevant environmental context across multiple turns?
- [ ] Does the system avoid asking again for information already available?
- [ ] Can text and structured input be converted into a common internal environmental representation?
- [ ] Does memory/context avoid fabricating environmental information?

---

### 23. GOLDEN EXAMPLE

**INPUT:** Rainfall, Soil Organic Carbon, Land Use, Species Richness, NDVI, Temperature
**ANALYSIS:** Detect reduced rainfall, elevated temp, low SOC, intensive land use, declining NDVI, reduced richness.
**RELATIONSHIP ANALYSIS:**
- Rainfall + Temp → water stress
- Land Use + Soil Carbon → soil degradation pressure
- Land Use + Habitat + Species Richness → biodiversity pressure
- NDVI + Rainfall + Temp → vegetation stress
**SCIENTIFIC RETRIEVAL:** Retrieve ecological research supporting detected relationships.
**INTEGRATED REASONING:** Combine measured conditions + relationships + scientific evidence.
**INTERVENTION:** Recommend specific restoration/conservation targeted to conditions/location.
**EXPECTED IMPACT:** Explain which variables will improve.
**EVIDENCE + CONFIDENCE:** Show supporting sources and limitations.

---

### 24. FINAL DEVELOPMENT RULE

**FROM THIS POINT FORWARD:**
Do not implement features merely because they look impressive. Prioritize features that increase:
`DATA INTELLIGENCE + ENVIRONMENTAL REASONING + SCIENTIFIC GROUNDING + MULTI-VARIABLE ANALYSIS + ACTIONABLE ECOLOGICAL DECISION SUPPORT`

Every new feature must strengthen the Environmental Intelligence System identity.
