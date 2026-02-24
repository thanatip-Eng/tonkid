# Tonkid — ต้นคิด

## Overview

AI chatbot that facilitates critical thinking exercises for Thai students using OpenAI GPT-4o. Students go through a structured 5-round Socratic dialogue about WEF 2026 global trends, receive a score (out of 20), and export their transcript for submission.

Two versions:
- **Streamlit version** (`tonkid-highschool-app.py`) — for high school students
- **Matthew AI version** (`matthew/`) — for ~3,000 Chiang Mai University students, deployed on CMU's Matthew AI platform

## Tech Stack

- **Python 3.11**
- **Streamlit** (>=1.28.0) — web UI framework (high school version)
- **OpenAI API** (>=1.0.0) — GPT-4o model
- **Matthew AI** — CMU's AI platform (university version, supports GPT-4o/4.1/5/5-mini)
- **Dev Container** — GitHub Codespaces support

## Project Structure

```
tonkid/
├── config/
│   ├── system_prompt_highschool.txt   # System prompt for high school version
│   └── knowledge_base.txt            # WEF 2026 knowledge base (6 categories, 25+ bullet points)
├── matthew/
│   ├── matthew_instruction.md         # Chatbot instruction for Matthew AI (≤20,000 chars)
│   ├── matthew_knowledge_base.md      # Knowledge base file to upload to Matthew AI
│   └── research_survey_th.md          # Research survey questions for MS Forms (~45 items)
├── .devcontainer/devcontainer.json    # Dev Container config (Python 3.11, port 8501)
├── tonkid-highschool-app.py           # Main Streamlit app (~360 lines)
├── requirements.txt                   # Dependencies (streamlit, openai)
└── CLAUDE.md                          # This file
```

## Running the App (Streamlit version)

```bash
pip install -r requirements.txt
streamlit run tonkid-highschool-app.py
```

The app runs on **port 8501**.

### Required Secret

Configure `OPENAI_API_KEY` in Streamlit secrets before running:

```bash
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-..."' > .streamlit/secrets.toml
```

Do NOT commit `.streamlit/secrets.toml`.

## Architecture

### Streamlit Version

Single-file Streamlit app. No database — all state is ephemeral via `st.session_state`. System prompt and knowledge base are loaded from `config/` files at startup, combined into `FULL_PROMPT`.

#### Config Loading

```python
SYSTEM_PROMPT = load_config('config/system_prompt_highschool.txt')
KNOWLEDGE_BASE = load_config('config/knowledge_base.txt')
FULL_PROMPT = SYSTEM_PROMPT + "\n\n# ข้อมูลอ้างอิง\n" + KNOWLEDGE_BASE
```

#### Session State Keys

| Key | Type | Purpose |
|-----|------|---------|
| `authenticated` | bool | Login status |
| `user_email` | str | Student email |
| `user_name` | str | Student name (Thai) |
| `sis_id` | str | Canvas LMS SIS ID |
| `messages` | list[dict] | Chat history (`role`/`content`) |
| `conversation_started` | bool | Whether first AI message was sent |
| `round_count` | int | Number of student messages |

#### Key Functions

| Function | Purpose |
|----------|---------|
| `load_config(filepath)` | Loads text config files relative to script dir |
| `get_openai_response(messages_history)` | Calls GPT-4o (temp=0.7, max_tokens=1500) |
| `export_conversation_txt()` | Generates .txt transcript for submission |
| `export_conversation_html()` | Generates styled .html transcript |
| `simple_login()` | Login form (email, name, SIS ID) |
| `main_chat()` | Chat UI with sidebar downloads |
| `main()` | Entry point, checks API key, routes auth |

### Matthew AI Version

Deployed on CMU's Matthew AI platform. Two components:
1. **Chatbot instruction** (`matthew/matthew_instruction.md`) — paste into Matthew's instruction field (≤20,000 chars)
2. **Knowledge base** (`matthew/matthew_knowledge_base.md`) — upload as file to Matthew

### Conversation Flow (both versions)

1. **Introduction** — greet, set mindset, explain activity
2. **Topic selection** — offer 3-4 topics based on student's field of interest
3. **5-round dialogue** — Explore → Analyze → Challenge → Connect → Synthesize
4. **Scoring** — rubric with 5 criteria, 4 points each (20 total), with detailed descriptors (1-4 per criterion)
5. **Completion** — verification code: `TK-[ID last 4]-[score]-[rounds]R-D26`

### Key Differences Between Versions

| Aspect | High School (Streamlit) | University (Matthew) |
|--------|------------------------|---------------------|
| Step 1 question | "คณะที่สนใจจะเข้า" | "คณะที่กำลังเรียน + สิ่งที่กำลังศึกษา" |
| Round 5 level | Evaluating | Creating ("ถ้าเธอเป็นผู้กำหนดนโยบาย...") |
| Login | Email + Name + SIS ID | CMU Account (Matthew handles) |
| Export | Download .txt/.html from sidebar | Export .txt from Matthew |

### System Prompt Features

- **Rubric descriptors** — detailed 1-4 level descriptions for each of 5 scoring criteria
- **Assumptions questions** (Round 2) — probes hidden assumptions in student reasoning
- **Implications questions** (Round 4) — explores consequences and broader impact
- **Devil's Advocate** — graduated intensity (mild → medium → strong) across rounds 2-4
- **Safety net** — reduces intensity if student gives very short answers or says "ไม่รู้"
- **Bidirectional challenge** — if student is pessimistic, show optimistic view and vice versa
- **Source links** — verifiable WEF URLs provided to students

### Knowledge Base Categories

1. ภูมิรัฐศาสตร์ (Geopolitics)
2. AI และนวัตกรรม (AI & Innovation)
3. แรงงานและทักษะ (Labor & Skills)
4. สิ่งแวดล้อม (Environment)
5. ความเหลื่อมล้ำ (Inequality)
6. สุขภาพ (Health)

Each category includes both pessimistic and optimistic data points with source attribution.

## Research Survey

`matthew/research_survey_th.md` contains a ~45-item research survey (Thai) for MS Forms:
- Retrospective pre-post CT disposition (Sosu's CTDS)
- Perceived CT improvement
- Technology Acceptance Model (TAM)
- Trust in AI
- Engagement, difficulty, satisfaction
- Open-ended questions
- Attribution of change

## Conventions

- **Language:** Thai-only UI and prompts (English for technical terms only)
- **Persona:** ต้นคิด calls itself "ต้นคิด", calls students "เธอ", never "คุณ"
- **Styling:** Custom CSS via `st.markdown(unsafe_allow_html=True)` — purple gradient branding
- **No tests** — verify manually by running the Streamlit app
- **No .gitignore** — be careful not to commit `.streamlit/secrets.toml`

## Token Estimates (per student)

~295,000 tokens per session (285K input + 10K output across 9 API calls). Cost for 3,000 students ranges from ~5,300 THB (GPT-4o-mini) to ~87,700 THB (GPT-4o).

## Known Issues

- `.devcontainer/devcontainer.json` references `app.py` — should be `tonkid-highschool-app.py`
- DevContainer also opens `README.md` which does not exist
