# process_detection.py
# Very simple heuristic process type detector.

import os

def detect_process_type(file_paths):
    """
    Detect process type based on keywords in filenames.
    Returns a process_type key matching CHECKLISTS.
    """
    names = [os.path.basename(p).lower() for p in file_paths]

    if any("incorporation" in n or "articles" in n for n in names):
        return "company_incorporation"
    if any("license" in n or "licence" in n for n in names):
        return "licensing"
    if any("nda" in n or "non-disclosure" in n for n in names):
        return "nda"

    return None
