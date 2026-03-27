
# to run the API from command line:
# > uvicorn main:app --reload

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import ollama
import fitz  # PyMuPDF
from prompts import INSTRUCTIONS, TITLE_PROMPT, AUTHORS_PROMPT, FOCUS_PROMPT, TABFIG_PROMPT, CHUNK_PROMPT, SUMMARY_PROMPT
import os
import re
from dotenv import load_dotenv
from ollama import Client
import json
import ast
from openai import OpenAI


load_dotenv() # load value from our environment variable file

print(f"DEBUG: Assigned port is: {os.getenv('PORT')}")

ERROR = "Generation error"

### Nvidia models
MODEL = "mistralai/mixtral-8x22b-instruct-v0.1"
API_KEY = os.getenv("NVIDIA_API_KEY")

# Use nvidia models API
client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = API_KEY
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/config")
async def get_config():
    # This sends the key from your .env to the browser
    return {
        "api_key": os.getenv("NVIDIA_API_KEY"),
        "model_name": MODEL
        }


# def verify_api_key(x_api_key: str = Header(None)):
#     credits = API_KEY_CREDITS.get(x_api_key, 0)
#     if credits <= 0:
#         raise HTTPException(status_code=401, detail="Invalid API Key")
#     return x_api_key


def extract_item(text, prompt_type, temp, tokens):
    PROMPT = prompt_type.replace("{{DATA}}", text)

    completion = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "system", "content":INSTRUCTIONS},
    {"role":"user","content":PROMPT}],
    temperature=temp,
    top_p=0.1,
    max_tokens=tokens,
    stream=False
    )
    result = completion.choices[0].message.content

    # Delete superfluous generated content
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        result = match.group(0)
    print(f"**{result}**\n")
    return result


def parse_item(raw, sep, key):
    """
    convert json file into dictionary
    """
    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        raw = json.loads(raw)
        return sep.join(raw[key])
    except Exception as e:
        print(e)
        return ERROR


def parse_chunk(chunk):
    """
    convert json file into dictionary
    """
    try:
        chunk = chunk.replace("```json", "").replace("```", "").strip()
        chunk = json.loads(chunk)
        return chunk
    except Exception as e:
        print(e)
        return ERROR


def remove_duplicate(list_items):
    """
    This function aims to remove duplicate figures or tables that were identified more than once by the LLM
    """
    try:
        set_items = set()
        new_list_items = []
        for item in list_items:
            first = item.split(":")[0]
            if first not in set_items:
                set_items.add(first)
                new_list_items.append(item)

        return new_list_items
    except Exception as e:
        print(e)
        return [ERROR]


def extract_tabfig(tab_fig_chunks):
    """
    Remove tables and figures duplicates.
    Returns a string of two bullet lists of tables and figures.
    """
    try:
        tabs = remove_duplicate(tab_fig_chunks['Tables'])
        figs = remove_duplicate(tab_fig_chunks['Figures'])

        nb_tbl = len(tabs)
        nb_fig = len(figs)
        if nb_tbl > 1:
            tables = f"{nb_tbl} tables were found :\n" + "\u2022 " + "\n\u2022 ".join(tabs) + "\n"
        elif nb_tbl == 1:
            tables = f"{nb_tbl} table was found :\n" + "\u2022 " + "\n\u2022 ".join(tabs) + "\n"
        else:
            tables = "No tables were found\n"
        if nb_fig > 1:
            figures = f"{nb_fig} figures were found :\n" + "\u2022 " + "\n\u2022 ".join(figs) + "\n"
        elif nb_fig == 1:
            figures = f"{nb_fig} figure was found :\n" + "\u2022 " + "\n\u2022 ".join(figs) + "\n"
        else:
            figures = "No figures were found\n"

        return tables + "\n" + figures
    except Exception as e:
        print(e)
        return ERROR


def extract_data_1stpage(doc):
    """
    Analyze the first page to extract the title, authors, and main focus of the paper.
    """
    try:
        page_0 = doc[0].get_text()
        title_raw = extract_item(page_0, TITLE_PROMPT, 0.0, 512)
        authors_raw = extract_item(page_0, AUTHORS_PROMPT, 0.0, 512)
        focus_raw = extract_item(page_0, FOCUS_PROMPT, 0.0, 1024)
        title = parse_item(title_raw, " ", 'Title')
        authors = parse_item(authors_raw, ", ", 'Authors')
        focus = parse_item(focus_raw, " ", 'Focus')
        return title, authors, focus
    except Exception as e:
        print(e)
        return ERROR, ERROR, ERROR


def renumber_items(item_list, label):
    try:
        new_list = []
        # Remove any item with 'None'
        item_list = [item for item in item_list if "None" not in item]
        item_list = [item for item in item_list if "not" not in item]
        item_list = [item for item in item_list if "Not" not in item]
        for i, item in enumerate(item_list, 1):
            print(f"i={i}, item={item}")
            # looks for "label X:" 
            # and replaces it with the current index "label i:"
            dynamic_pattern = rf"{label} \d+:"
            new = f"{label} {i}:"

            # If the pattern exists in item, replace existing label with new label; otherwise, just keep the item
            new_item = re.sub(dynamic_pattern, new, item)
            new_list.append(new_item)
        return new_list
    except Exception as e:
        print(e)
        return [ERROR]


def extract_data(sum_id_chunks):
    """
    Create a summary of the paper.
    Return a bullet list of main ideas presented in the paper
    """
    try:
        raw_summary = "\n".join(sum_id_chunks['Summary'])
        summary = extract_item(raw_summary, SUMMARY_PROMPT, 0.2, 2048)
        ideas_raw = sum_id_chunks['Ideas']
        ideas_list = renumber_items(ideas_raw , "idea")
        ideas = "\u2022 " + "\n\u2022 ".join(ideas_list)
        return summary, ideas
    except Exception as e:
        print(e)
        return ERROR, ERROR


def analyze_chunks(doc):
    """
    Analyze paper in chunks, then regroup the findings
    Extract:
    - Tables and Figures
    - Main ideas mentionned in the paper
    - Paper summary
    """
    try:
        group_pages = 3
        nb_pages = len(doc)
        tab_fig_chunks = {"Tables" : [], "Figures" : []}
        sum_id_chunks = {"Summary" : [],  "Ideas" : []}
        for i in range(0, nb_pages, group_pages):
            chunk_text = ""
            for page_num in range(i, min(i + group_pages, nb_pages)):
                chunk_text += doc[page_num].get_text()
            with open("text.txt", "a", encoding="utf-8") as file:
                file.write(chunk_text)
            tabfig = parse_chunk(extract_item(chunk_text, TABFIG_PROMPT, 0.1, 4096))
            chunk = parse_chunk(extract_item(chunk_text, CHUNK_PROMPT, 0.1, 4096))

            # combine all elements found into dictionaries
            for key, value in tabfig.items(): tab_fig_chunks[key] += value
            for key, value in chunk.items(): sum_id_chunks[key] += value

        tables_figures = extract_tabfig(tab_fig_chunks)
        summary, ideas = extract_data(sum_id_chunks)

        return summary, ideas, tables_figures
    except Exception as e:
        print(e)
        return ERROR, ERROR, ERROR


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("results.html", "r") as f:
        return f.read()


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    # Check file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    # Check MIME Type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid MIME type.")
    
    # Extract text from PDF
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    print(f"Type of file: {type(doc)}, number of pages: {len(doc)}")

    # Analyze the first page to extract the title, authors, and main focus of the paper.
    title, authors, focus = extract_data_1stpage(doc)

    # Analyze paper in chunks, then regroup the findings
    summary, ideas, tables_figures = analyze_chunks(doc)

    print(f"\nsummary\n\n")
    return {
        "title": title,
        "authors": authors,
        "summary": summary,
        "primary_focus": focus,
        "ideas": ideas,
        "tables_figures": tables_figures,
    }
