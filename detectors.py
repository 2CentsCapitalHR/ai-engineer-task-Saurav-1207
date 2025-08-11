import re
from typing import List, Dict

JURISDICTION_KEYWORDS = ['abu dhabi global market', 'adgm', 'adgm courts']

def check_jurisdiction(paragraphs: List[str]) -> List[Dict]:
    issues = []
    for i, p in enumerate(paragraphs):
        lower = p.lower()
        if ('jurisdiction' in lower or 'court' in lower) and not any(k in lower for k in JURISDICTION_KEYWORDS):
            issues.append({
                'para_index': i,
                'match_text': p,
                'issue_text': 'Jurisdiction clause does not specify ADGM.',
                'severity': 'High',
                'suggestion': 'Update jurisdiction clause to specify Abu Dhabi Global Market (ADGM) courts.',
                'citation': ''
            })
    return issues

def check_missing_signatory(paragraphs: List[str]) -> List[Dict]:
    issues = []
    text = ' '.join(paragraphs).lower()
    if 'signature' not in text and 'signed' not in text and 'signatory' not in text:
        issues.append({
            'para_index': len(paragraphs)-1 if paragraphs else 0,
            'match_text': paragraphs[-1] if paragraphs else '',
            'issue_text': 'Document appears to lack a signatory block or signature lines.',
            'severity': 'High',
            'suggestion': 'Add signatory panel with printed name, title, date and signature.',
            'citation': ''
        })
    return issues
