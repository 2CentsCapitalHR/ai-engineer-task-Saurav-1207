# ADGM-Compliant Corporate Agent with Document Intelligence
DEMO LINK:https://www.loom.com/share/ecc29d3b2b8f4543bea027a95e5dea4e?sid=8c85385e-133a-409e-be77-38f1de93094b
## 📌 Overview
The **Corporate Agent** is an AI-powered legal assistant designed to review, validate, and help users prepare documentation for **business incorporation and compliance** within the **Abu Dhabi Global Market (ADGM)** jurisdiction.  

This agent:
- Accepts `.docx` legal documents.
- Checks compliance with ADGM rules.
- Highlights red flags.
- Inserts contextual comments referencing official ADGM regulations.
- Identifies missing mandatory documents from a predefined checklist.
- Produces a **reviewed `.docx`** file and a **structured JSON/Python report**.

The system uses **Retrieval-Augmented Generation (RAG)** to ensure all analysis aligns with real ADGM laws, regulations, and processes.

---

## ✨ Features
1. **Document Upload & Parsing**  
   - Accepts `.docx` files.  
   - Detects document type (e.g., AoA, MoA, UBO Form).  

2. **Checklist Verification**  
   - Recognizes the legal process (incorporation, licensing, etc.).  
   - Compares uploaded documents to required ADGM checklist.  
   - Notifies user of missing documents.

3. **Red Flag Detection**  
   - Invalid/missing clauses.  
   - Incorrect jurisdiction references.  
   - Ambiguous language.  
   - Missing signatory sections.  
   - Non-compliance with ADGM templates.

4. **Inline Commenting**  
   - Inserts contextual comments into `.docx`.  
   - Cites exact ADGM law/article.  
   - Suggests alternative wording (optional).

5. **Output Formats**  
   - Reviewed `.docx` file with highlights/comments.  
   - Structured `JSON` or Python dictionary summarizing findings.

---

## 🛠️ Tech Stack
- **Language:** Python  
- **Frameworks:** Streamlit / Gradio for UI  
- **LLM & RAG:** OpenAI / Gemini / Ollama / Claude (configurable)  
- **Document Parsing:** `python-docx`, `docx2python`, `docx-comment` libraries  
- **Search & Retrieval:** Vector store (e.g., FAISS, ChromaDB) with ADGM references  

---

## 📂 Folder Structure
```
.
adgm-corporate-agent/
├─ app.py                     # Gradio app
├─ docx_utils.py              # parse .docx, annotate, save reviewed docx
├─ rag_index.py               # index ADGM refs & retrieve evidence
├─ detectors.py               # red-flag checks and rules
├─ report_schema.py           # JSON schema for output
├─ requirements.txt
├─ README.md
└─ examples/
   ├─ example_before.docx
   └─ example_after_reviewed.docx
```

---

## ⚙️ Installation
```bash
# Clone repository
git clone https://github.com/yourusername/adgm-corporate-agent.git
cd adgm-corporate-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage
```bash

python app.py
```

1. Upload `.docx` files.  
2. The system detects the process type & verifies checklist.  
3. Highlights red flags & inserts comments.  
4. Downloads the reviewed `.docx` & JSON report.

---

## 📌 Example Output (JSON)
```json
{
  "process": "Company Incorporation",
  "documents_uploaded": 4,
  "required_documents": 5,
  "missing_document": "Register of Members and Directors",
  "issues_found": [
    {
      "document": "Articles of Association",
      "section": "Clause 3.1",
      "issue": "Jurisdiction clause does not specify ADGM",
      "severity": "High",
      "suggestion": "Update jurisdiction to ADGM Courts."
    }
  ]
}
```

---

## 📜 ADGM Resources
- [ADGM Companies Regulations 2020](https://www.adgm.com)
- [Official ADGM Guidance Notes](https://www.adgm.com)

---
