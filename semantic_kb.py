import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

# ---------------------------------------------------------
# App config
# ---------------------------------------------------------
st.set_page_config(page_title="Semantic Keyword Builder", layout="wide")
st.title("🔑 Semantic Keyword Builder")

st.markdown(
    """
This app uses a large language model to generate a semantically enriched keyword universe (EAV-based) for SEO and content strategy.
It groups keywords using topic-level conceptual labels (not formal knowledge-graph entities). It returns a structured keyword list and lets you download everything as CSV.

"""
)

# ---------------------------------------------------------
# Sidebar configuration
# ---------------------------------------------------------
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input("API key", type="password", help="API key for your language model provider.")

model_name = st.sidebar.text_input(
    "Model name",
    value="gemini-2.5-flash",
    help="You can change this to another compatible model if needed."
)

country = st.sidebar.text_input("Country", value="United States")
language = st.sidebar.text_input("Language (for keywords)", value="English")
website = st.sidebar.text_input(
    "Website / brand context",
    value="https://www.example.com/home-renovation"
)
niche = st.sidebar.text_input(
    "Niche / service",
    value="Service for home renovation"
)

approx_keywords = st.sidebar.slider(
    "Approximate number of keywords to generate",
    min_value=30,
    max_value=200,
    value=60,
    step=10,
    help="The model will aim for at least this many unique keywords."
)

seed_keywords_text = st.sidebar.text_area(
    "Optional seed keywords (one per line)",
    value="home renovation\napartment renovation\nkitchen remodel\nbathroom renovation",
    height=140,
    help="Optional. Use to steer the model toward specific sub-topics."
)

run_button = st.sidebar.button("Generate Keyword Universe 🚀")

# ---------------------------------------------------------
# API setup
# ---------------------------------------------------------
if not api_key:
    st.error("Please enter your API key in the sidebar to proceed.")
    st.stop()

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error(f"Error creating model: {e}")
    st.stop()


# ---------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------
def build_keyword_universe_prompt(
    country: str,
    language: str,
    website: str,
    niche: str,
    approx_keywords: int,
    seed_keywords: list[str],
) -> str:
    """
    Build a strict JSON-only prompt for generating the semantic keyword universe.
    """

    seeds_block = "\n".join(f"- {s}" for s in seed_keywords) if seed_keywords else "none"

    return f"""
You are an expert semantic SEO and keyword research assistant.

Your task:
Given the project context, generate a semantic keyword universe with entity-attribute-variable (EAV) annotations.
Focus on queries and language actually used by searchers in the specified country and language.

Project context:
- Country: {country}
- Language for keywords: {language}
- Website / brand: {website}
- Niche / service: {niche}

Optional seed keywords:
{seeds_block}

Methodology you must follow (internally; do NOT explain this in the output):
1) Understand the niche and search context.
2) Build a broad keyword universe:
   - Include head terms, mid-tail, and long-tail queries.
   - Include a mix of informational, commercial, transactional, and navigational intents.
   - Include EAV-style combinations such as:
     - Entities (e.g., renovation types, rooms, services, problems)
     - Attributes (e.g., cost, location, size, condition, purpose)
     - Variables (e.g., 40 sqm, city names, old apartment, budget level).
3) Classify each keyword by:
   - Volume level (qualitative estimate).
   - Primary search intent.
   - Entity, attribute, variable.
   - Topic label and cluster id.

Output requirements:
1) Generate AT LEAST {approx_keywords} unique keywords that are highly relevant to the given niche in the specified country.
2) All natural language in fields like "keyword", "entity", "attribute", "variable", and "topic" MUST be written in {language}.
3) Use qualitative estimates for volume. Do NOT invent exact search volumes.

Return ONLY a valid JSON object in this exact structure, with no commentary, no markdown, and no code fences:

{{
  "project": {{
    "country": "{country}",
    "language": "{language}",
    "website": "{website}",
    "niche": "{niche}",
    "approx_keywords_requested": {approx_keywords}
  }},
  "keywords": [
    {{
      "keyword": "example keyword in {language}",
      "volume_level": "high | medium | low | unknown",
      "intent": "informational | commercial | transactional | navigational | mixed",
      "entity": "main entity for this keyword in {language}",
      "attribute": "attribute in {language}",
      "variable": "variable value in {language}",
      "source": "ai_synthetic | seed | competitor | site_search | other",
      "topic": "human-friendly cluster name in {language}",
      "cluster_id": "C1"
    }}
  ]
}}

Constraints:
- The "keywords" array MUST contain at least {approx_keywords} objects.
- "intent" must be exactly one of:
  ["informational", "commercial", "transactional", "navigational", "mixed"].
- "volume_level" must be exactly one of:
  ["high", "medium", "low", "unknown"].
- "cluster_id" should be a short code like "C1", "C2", etc., reused for keywords in the same topic.
- Do NOT include any explanation, comments, markdown, or extra fields outside this JSON schema.
"""


# ---------------------------------------------------------
# Generation function
# ---------------------------------------------------------
def generate_keyword_universe():
    seed_keywords = [
        line.strip()
        for line in seed_keywords_text.splitlines()
        if line.strip()
    ]

    prompt = build_keyword_universe_prompt(
        country=country,
        language=language,
        website=website,
        niche=niche,
        approx_keywords=approx_keywords,
        seed_keywords=seed_keywords,
    )

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()

        # clean possible ```json fences or ``` wrapping
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.startswith("```"):
            json_text = json_text[3:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        json_text = json_text.strip()

        data = json.loads(json_text)
        return data, json_text

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse model response as JSON: {e}")
        st.text("Raw response that caused the error:")
        st.code(json_text if "json_text" in locals() else "N/A")
        return None, None

    except Exception as e:
        st.error(f"Unexpected error during generation: {e}")
        return None, None


# ---------------------------------------------------------
# Main run
# ---------------------------------------------------------
if run_button:
    with st.spinner("Generating semantic keyword universe..."):
        data, raw = generate_keyword_universe()

    if data is None:
        st.stop()

    project_info = data.get("project", {})
    keywords_list = data.get("keywords", [])

    if not keywords_list:
        st.warning("The model returned no keywords. Please tweak your prompt or try again.")
        if raw:
            with st.expander("Raw JSON response"):
                st.code(raw, language="json")
        st.stop()

    st.caption("Topic entity labels are conceptual clustering labels. KG confidence reflects that these are not resolved knowledge-graph entities.")

    df = pd.DataFrame(keywords_list)
    if "entity" in df.columns:
        df = df.rename(columns={"entity": "topic_entity_label"})

    # Reorder columns for convenience if they exist
    preferred_cols = [
        "keyword",
        "volume_level",
        "intent",
        "topic_entity_label",
        "attribute",
        "variable",
        "source",
        "topic",
        "cluster_id",
    ]
    existing_cols = [c for c in preferred_cols if c in df.columns]
    other_cols = [c for c in df.columns if c not in existing_cols]
    df = df[existing_cols + other_cols]

    st.subheader("📊 Generated Keyword Universe")
    st.dataframe(
        df,
        use_container_width=True,
        height=(min(len(df), 25) + 1) * 35 + 3,
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        data=csv,
        file_name="semantic_keyword_universe.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.subheader("Project metadata")
    st.json(project_info)

    with st.expander("Raw JSON output"):
        st.code(raw, language="json")
else:
    st.info("Configure your project in the sidebar and click 'Generate Keyword Universe 🚀'.")
