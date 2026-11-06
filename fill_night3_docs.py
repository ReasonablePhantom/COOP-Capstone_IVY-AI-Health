"""Fill the Pod 2 Team Charter and AI Disclosure Statement for Capstone Night 3.

Reads the copies in Docs/, writes new files named per the capstone convention
(Pod_#_Deliverable_v#). Originals are left untouched.
"""
import copy
from docx import Document
from docx.shared import Pt

BASE = "Docs/"
CHARTER_IN = BASE + "[Cohort C690] [Pod 2] Team Charter .docx"
CHARTER_OUT = BASE + "Pod_2_TeamCharter_v1.docx"
AI_IN = BASE + "[Cohort  C690] [Pod 2] AI Disclosure Statement.docx"
AI_OUT = BASE + "Pod_2_AIDisclosureStatement_v1.docx"

TABLE_SIZE = Pt(9.5)


def set_cell(cell, text, size=TABLE_SIZE):
    """Replace a cell's text, keeping the first run's formatting."""
    p = cell.paragraphs[0]
    for r in list(p.runs)[1:]:
        r._element.getparent().remove(r._element)
    if p.runs:
        p.runs[0].text = text
        if p.runs[0].font.size is None:
            p.runs[0].font.size = size
    else:
        run = p.add_run(text)
        run.font.size = size
    for extra in list(cell.paragraphs[1:]):
        extra._element.getparent().remove(extra._element)


def clone_last_row(table):
    tr = copy.deepcopy(table.rows[-1]._tr)
    table._tbl.append(tr)
    return table.rows[-1]


def find_para(doc, needle, style=None):
    for p in doc.paragraphs:
        if needle in p.text and (style is None or p.style.name == style):
            return p
    raise LookupError(needle)


def replace_para_text(p, text):
    """Keep the first run's formatting, drop the rest."""
    runs = p.runs
    for r in runs[1:]:
        r._element.getparent().remove(r._element)
    if runs:
        runs[0].text = text
    else:
        p.add_run(text)


def add_run_like(p, text, ref_p):
    """Append a run copying font name/size from a reference paragraph."""
    run = p.add_run(text)
    if ref_p is not None and ref_p.runs:
        src = ref_p.runs[0]
        run.font.name = src.font.name
        run.font.size = src.font.size
    return run


def insert_para_after(p, text, ref_p=None):
    """Insert a new paragraph immediately after p."""
    new_p = copy.deepcopy(p._p)
    p._p.addnext(new_p)
    from docx.text.paragraph import Paragraph
    np = Paragraph(new_p, p._parent)
    replace_para_text(np, text)
    if ref_p is not None:
        return np
    return np


# ---------------------------------------------------------------- Team Charter
charter = Document(CHARTER_IN)

# Part 2: split the duplicated scorecard ownership (two members held the same title)
roles = {"Alyssa": "Scorecard lead (Desirability and Feasibility)",
         "Derek": "Scorecard lead (Viability and pricing)"}
role_table = charter.tables[2]
for row in role_table.rows[1:]:
    name = row.cells[0].text.strip()
    if name in roles:
        set_cell(row.cells[1], roles[name])

# Part 3: five team agreements (replace the five placeholder lines)
agreements = [
    "We agree to reply to pod messages within 24 hours and to flag a problem on the day we find it.",
    "We agree to send each piece of owned work to its backup at least 24 hours before it is due.",
    "We agree to tell the Pod lead and the captain before we miss a night or a deadline, not after.",
    "We agree to load our row in the running agenda before the Daily Standup opens.",
    "We agree that peer review talks about work and evidence only, and that a disagreement is settled the same night.",
]
placeholders = [p for p in charter.paragraphs if p.text.strip() == "Insert agreement here"]
assert len(placeholders) == 5, len(placeholders)
for p, text in zip(placeholders, agreements):
    replace_para_text(p, text)

# Part 3: competencies table has 5 data rows but the pod has 7 members
comp_table = charter.tables[4]
comp_rows = [
    ("Bruce", "Initiative and Results-Driven; Resource Management",
     "Built a reproducible pipeline from scrape to database, so every score can be traced to a dated source."),
    ("Emilio", "Collaboration; Adaptability",
     "Will merge the four pod sections into one deck and restructure them when the evidence changes."),
    ("Jermaine", "Resource Management; Collaboration",
     "Will keep the AI Disclosure current and check each tool against the pod's agreements."),
    ("Alyssa", "Resource Management; Initiative",
     "Will write one evidence sentence and one dated source for every Desirability and Feasibility score."),
    ("Derek", "Workload Management; Resource Management",
     "Will keep pricing and competitor baselines dated and complete for Viability."),
    ("Fion", "Collaboration; Workload Management",
     "Will run the nights, merge the deck and keep the pod on its dates."),
    ("Jasmine", "Initiative; Collaboration",
     "Will draft the memo section so the two choices appear in the first two sentences."),
]
while len(comp_table.rows) - 1 < len(comp_rows):
    clone_last_row(comp_table)
for i, (name, comps, how) in enumerate(comp_rows, start=1):
    row = comp_table.rows[i]
    set_cell(row.cells[0], name)
    set_cell(row.cells[1], comps)
    set_cell(row.cells[2], how)

# Part 4: Daily Standup drafts for Nights 1-3 (pod rep left blank for the pod)
standup = {
    1: ("Team Charter and AI Disclosure Statement copied and shared with our captain; Pod lead elected (Fion).",
        "Pod formed and the seven roles with backups recorded in Part 2. The scoring anchors were not yet rewritten for our line.",
        "Form the pod, elect the Pod lead, and decide how we rank our product line."),
    2: ("Preliminary Discovery submitted with a draft scorecard.",
        "Discovery built on the review corpus; 25 most recent reviews per app tagged; sources table started.",
        "Explore Ivy's pages and open data, and turn the gaps into research questions."),
    3: ("Team Alignment draft prepared; to be confirmed in this session. AI Disclosure brought up to date.",
        "Files to move into the Project Folder under the naming rule; first peer review round this session.",
        "Align on how we work together and hold the first peer review round."),
}
standup_table = charter.tables[5]
for night, (status, progress, goal) in standup.items():
    row = standup_table.rows[night]  # row 0 is the header
    set_cell(row.cells[2], status)
    set_cell(row.cells[3], progress)
    set_cell(row.cells[4], goal)

# Part 5: Team Alignment answers (Night 3)
alignment = [
    "Discovery went in on time at the Night 2 deadline. The evidence base grew from a 25-review sample to the full review "
    "corpus with a de-duplicated, queryable database, so each score can be traced to a dated source.",
    "The process records lagged the analysis: Parts 3 to 5 of this charter and most of the AI Disclosure were blank, two "
    "members held the scorecard title with no split of the work, and the AI log has no entries after 11/2.",
    "Bruce: Discovery and the sources table final, one evidence sentence per score. Alyssa: Desirability and Feasibility "
    "scores. Derek: Viability and pricing baselines. Emilio: the Pod 2 section of the cohort deck and who presents each "
    "part. Jermaine: AI Disclosure complete and every log entry current. Jasmine: the memo section and scorecard exhibit. "
    "Fion: charter current and the merged deck.",
    "The pod rep updates the running agenda and the AI log in the last five minutes of each night, before the regroup, "
    "instead of catching up later.",
]
align_table = charter.tables[6]
for i, text in enumerate(alignment, start=1):
    set_cell(align_table.rows[i].cells[1], text)

# Mark Part 5 as a draft prepared in advance
part6_heading = find_para(charter, "Part 6: Final review")
note = part6_heading.insert_paragraph_before(
    "Draft answers prepared on 11/6/26 from the pod's work to date. Confirm and rewrite them in the Night 3 conversation; "
    "the captain's input line stays for Sheila.", style="normal")
add_run_like(note, "", None)  # keep style consistent

charter.save(CHARTER_OUT)
print("saved", CHARTER_OUT)


# ------------------------------------------------------- AI Disclosure Statement
ai = Document(AI_IN)

# Part 1: point ownership at the charter
p_deadline = find_para(ai, "Each of us will be able to explain our work and meet deadlines")
own = insert_para_after(p_deadline, "Ownership of each piece of work is recorded in Part 2 of the Pod 2 Team Charter.")
own.paragraph_format.space_before = Pt(0)

# Part 2: relevance ranking 0-10 with a reason (template asks for a rank and an explanation)
ratings = {
    "Brainstorming and Planning": "8/10. Fastest way to frame research questions and outline the deck; we still choose the question.",
    "Research and Insights": "7/10. Speeds up finding sources, but every figure is checked against the original page.",
    "Writing and Communicating": "6/10. Useful for a first draft and for tightening sentences; the argument stays ours.",
    "Content Creation": "4/10. Limited value; AI helped lay out one slide template.",
    "Data Analysis": "9/10. Used to write and debug the Python scraping, cleaning and tagging scripts.",
    "App Building": "1/10. We are not building an app.",
    "App Deployment": "0/10. Not applicable to this project.",
}
for label, answer in ratings.items():
    p = None
    for cand in ai.paragraphs:
        if cand.text.strip() == label:
            p = cand
            break
    assert p is not None, label
    p.runs[-1].text = p.runs[-1].text.rstrip()
    add_run_like(p, f" — {answer}", p)

# Part 3: toolkit links and descriptions
tools = {
    "Claude": "https://claude.ai — chat assistant used for drafting, debugging and reviewing scripts and written sections.",
    "ChatGPT": "https://chatgpt.com — chat assistant used as a second opinion on wording and on data questions.",
    "Google Gemini": "https://gemini.google.com — chat assistant used for quick research and for the deck's visual roadmap.",
}
for label, answer in tools.items():
    p = None
    for cand in ai.paragraphs:
        if cand.text.strip() == label:
            p = cand
            break
    assert p is not None, label
    p.runs[-1].text = p.runs[-1].text.rstrip()
    add_run_like(p, f" — {answer}", p)

# Part 4: the pod's five agreements on quality, accountability and ethics
new_agreements = [
    "1. We agree that every number, source and date is checked against the original page by the member who records it, before it reaches a scorecard.",
    "2. We agree never to put personal health details, another fellow's personal information, or client-confidential material into a public AI model.",
    "3. We agree to log each use in Part 5 on the day it happens, with date, member, tool and use case, and never to backfill silently.",
    "4. We agree that AI-written code is run and explained by the member who submits it before it touches the pod's data.",
    "5. We agree that scores and the recommendation are made by us, not by a model, and that any member can ask another to reproduce a result.",
]
part5_heading = find_para(ai, "Part 5 Ongoing Use Case Log")
anchor = part5_heading
inserted = []
for text in new_agreements:
    np = anchor.insert_paragraph_before(text, style="normal")
    inserted.append(np)
# remove the two empty placeholder paragraphs between the example and Part 5
for p in list(ai.paragraphs):
    if p.text.strip() == "" and p._p.getparent() is not None:
        pass

# Part 5: log gaps
log = ai.tables[0]
for row in log.rows[1:]:
    if row.cells[2].text.strip().lower() == "claude" and not row.cells[3].text.strip():
        set_cell(row.cells[3], "Use case not recorded — to be completed by Fion.")

# note about the missing 11/3-11/6 entries
p_log = find_para(ai, "Maintain an active and ongoing log")
note = insert_para_after(
    p_log,
    "Gap to close: no entries between 11/3/26 and 11/6/26, although the cleaning, de-duplication, tagging and database "
    "work happened in that window. Each member who used a tool adds their own rows before Night 4.")

ai.save(AI_OUT)
print("saved", AI_OUT)
