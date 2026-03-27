INSTRUCTIONS = """
You are a specialized research analyzer."""
"""
- Output ONLY the requested data. No chatter."
- Do not include any introductory remarks, preambles, or conversational filler.
- Do not acknowledge the instructions. Provide ONLY the requested structure.
- Do not include (Bullet Points) or any if not specifically requested.
"""

TITLE_PROMPT = """
<ROLE>
You are an extraction agent specialized in academic literature.
</ROLE>

<TASK>
Extract the full Title within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

<CONSTRAINTS>
- Read only the first 300 tokens of the text within the <DATA_SOURCE> tags.
- Return ONLY a valid JSON object. No preamble, no markdown blocks, no postamble.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Title": ["Extract the full title as a list of strings. Exclude journal names, volume numbers, or conference proceedings"],
}
</RESPONSE FORMAT>

"""

AUTHORS_PROMPT = """
<ROLE>
You are an extraction agent specialized in academic literature.
</ROLE>

<TASK>
Extract the Authors names within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

<CONSTRAINTS>
- Read only the first 300 tokens of the text within the <DATA_SOURCE> tags.
- Return ONLY a valid JSON object. No preamble, no markdown blocks, no postamble.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Authors": ["Extract all author names as a list of strings. REMOVE all numerical citations, symbols (e.g., *, †), and affiliations from the name itself."],
}
</RESPONSE FORMAT>

"""

FOCUS_PROMPT = """
<ROLE>
You are an extraction agent specialized in academic literature.
</ROLE>

<TASK>
Extract the Main Focus from the provided text within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

<CONSTRAINTS>
- Stop processing once you reach the "Introduction" or "References" section.
- Return ONLY a valid JSON object. No preamble, no markdown blocks, no postamble.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Focus": ["Read the Abstract only. Provide a 2-3 sentences summary of the core research objective and methodology."],
}
</RESPONSE FORMAT>

"""

TABFIG_PROMPT1 = """
<ROLE>
You are an extraction agent specialized in academic literature.
</ROLE>

<TASK>
Extract tables and figures descriptions from the provided chunk of text within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

<EXTRACTION RULES>
1. **Tables**: 
   - List and number using the Table label any tables found in the text, with descriptions - max 100 chars per line.
   - ONLY include items explicitly detailed or labeled in the chunk. 
   - If no table is present, return an empty list [].
   - Format: "Table 1: Description".
2. **Figures**:
   - List and number using the Figure label the title of any figures found with descriptions - max 100 chars per line. Do not mention any figure mentionned in the text paragraph.
   - ONLY include items explicitly detailed or labeled in the text. 
   - If no figure is present, return an empty list [].
   - Format: "Figure 1: Description".
</EXTRACTION RULES>

<CONSTRAINTS>
- Return ONLY a valid JSON object. No preamble, no markdown blocks, no postamble, no chatter.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Tables": ["Table 1: Description"],
  "Figures": ["Figure 1: Description"]
}
</RESPONSE FORMAT>
"""
  #  - List and number using the Table label any tables found in the text, with descriptions - max 100 chars per line. If a table is mentionned in the study but not found in the current analyzed text, do not mentionned it.
  #  - List and number using the Figure label the title of any figures found with descriptions - max 100 chars per line. Do not mention any figure mentionned in the text paragraph.



TABFIG_PROMPT = """
<ROLE>
You are an expert scientific researcher. Analyze the provided text chunk and extract structured insights.
</ROLE>

<TASK>
Extract tables and figures descriptions from the provided text within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

<EXTRACTION RULES>
1. **Tables**: 
   - ONLY include items explicitly detailed or labeled in this chunk. 
   - If none are present, return an empty list [].
   - Format: "Table 1: Description".
   - MAX 100 characters
2. **Figures**:
   - ONLY include items explicitly detailed or labeled in this chunk. 
   - If none are present, return an empty list [].
   - Format: "Figure 1: Description".
   - MAX 100 characters
</EXTRACTION RULES>

<CONSTRAINTS>
- Return ONLY a valid JSON object with the requested data. 
- NO PREAMBLE: Do not include introductory text like **Summary:** or "Here is the summary.
- No markdown blocks and no chatter.
- NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.
- Maintain a professional tone in your summary.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Tables": ["Table 1: Description"],
  "Figures": ["Figure 1: Description"]
}
</RESPONSE FORMAT>
"""

CHUNK_PROMPT = """
<ROLE>
You are an expert scientific researcher. Analyze the provided text and extract structured insights.
</ROLE>

<TASK>
Extract a list of distinct key concepts from the provided text within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

<EXTRACTION RULES>
1. Create a professional summary of the core findings in this text.
2. Extract a list of descriptions of distinct key concepts presented in the text.
</EXTRACTION RULES>

<CONSTRAINTS>
- Return ONLY a valid JSON object. No preamble, no markdown blocks, no postamble, no chatter.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Summary": ["A single long string containing the entire professional summary"],
  "Ideas": ["Idea", "Idea"],
}
</RESPONSE FORMAT>
"""


SUMMARY_PROMPT = """
<ROLE>
You are an AI assistant specialized in creating summaries. Your output must be strictly limited to the data requested.
</ROLE>

<TASK>
Combined and create a summary from the text ideas within the <DATA_SOURCE> tags.
</TASK>

<CONSTRAINTS>
- Only return the summary. 
- Do not add any extra flourishes such as “Summary” or extra punctuation such as * or "
- NO PREAMBLE: Do not include introductory text like "Here is the analysis."
- NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.
- Maintain a professional tone in your summary.
</CONSTRAINTS>

<DATA_SOURCE>
{{DATA}}
</DATA_SOURCE>

"""
