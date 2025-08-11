import os
import gradio as gr
from checklist_data import CHECKLISTS
from process_detection import detect_process_type
from detectors import check_jurisdiction, check_missing_signatory
from rag_index import RagIndex
from sentence_transformers import SentenceTransformer
from docx_utils import annotate_and_save

# Load RAG index
RAG = RagIndex()
EMBED_MODEL = None
if os.path.exists("adgm_index_data.pkl"):
    try:
        RAG.load_from_pickle("adgm_index_data.pkl")
    except Exception as e:
        print("Failed to load index:", e)
else:
    print("No RAG index found — citations will be 'Pending'.")

def ensure_embed_model():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return EMBED_MODEL

def process_docs(files, selected_process):
    all_issues = []
    file_paths = [file.name if hasattr(file, "name") else file for file in files]

    # Detect or use selected process type
    process_type = None
    if selected_process == "Auto Detect":
        process_type = detect_process_type(file_paths)
    else:
        process_type = selected_process.lower().replace(" ", "_")

    checklist_summary = {}
    if process_type and process_type in CHECKLISTS:
        required_docs = CHECKLISTS[process_type]
        uploaded_names = [os.path.basename(p).lower() for p in file_paths]

        # Find missing documents
        missing_docs = []
        for req in required_docs:
            if not any(req.lower() in name for name in uploaded_names):
                missing_docs.append(req)

        checklist_summary = {
            "process": process_type.replace("_", " ").title(),
            "documents_uploaded": len(file_paths),
            "total_required": len(required_docs),
            "uploaded_count": len(required_docs) - len(missing_docs),
            "missing_count": len(missing_docs),
            "missing_docs": missing_docs
        }

        # Add missing doc warning to issues
        if missing_docs:
            all_issues.append({
                "document": None,
                "para_index": None,
                "match_text": "",
                "issue_text": f"Missing required documents for {process_type.replace('_', ' ').title()}",
                "severity": "High",
                "suggestion": f"Upload the missing documents: {', '.join(missing_docs)}",
                "citation": "Checklist reference — ADGM requirements"
            })

    # Run red flag checks for each doc
    for file_path in file_paths:
        issues = []
        issues.extend(check_jurisdiction(file_path))
        issues.extend(check_missing_signatory(file_path))

        # Add citations via RAG
        for iss in issues:
            q = iss.get("match_text", "")
            if q and RAG.index is not None:
                try:
                    model = ensure_embed_model()
                    vec = model.encode([q], convert_to_numpy=True)[0]
                    results = RAG.query(vec, k=2)
                    if results:
                        top = results[0]
                        iss["citation"] = (
                            f"Source: {top['metadata']['url']} | "
                            f"Excerpt: {top['chunk'][:300]} (dist={top['distance']:.3f})"
                        )
                except Exception as e:
                    iss["citation"] = f"Citation lookup failed: {e}"
            else:
                iss["citation"] = iss.get("citation") or "Pending — no local index loaded"

            iss["document"] = os.path.basename(file_path)

        # Save annotated docx
        out_path = f"{os.path.splitext(file_path)[0]}_reviewed.docx"
        annotate_and_save(file_path, issues, out_path)

        all_issues.extend(issues)

    return checklist_summary, all_issues

def review_interface(files, process_choice):
    checklist, issues = process_docs(files, process_choice)
    return [
        {"process": checklist.get("process"),
         "documents_uploaded": checklist.get("documents_uploaded"),
         "issues_found": issues},
        files[0].name.replace(".docx", "_reviewed.docx")
    ]

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## ADGM Corporate Agent — Demo")

    with gr.Row():
        uploaded_files = gr.File(label="Upload .docx files", file_types=[".docx"], file_count="multiple", type="filepath")

    process_dropdown = gr.Dropdown(
        choices=["Auto Detect", "Company Incorporation", "Licensing", "NDA"],
        value="Auto Detect",
        label="Process (auto-detect possible)"
    )

    review_btn = gr.Button("Review Documents")

    json_output = gr.JSON(label="JSON Report")
    download_output = gr.File(label="Download reviewed .docx")

    review_btn.click(
        fn=review_interface,
        inputs=[uploaded_files, process_dropdown],
        outputs=[json_output, download_output]
    )

if __name__ == "__main__":
    demo.launch()
