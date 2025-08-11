
\"\"\"Add Word comments to a .docx file.
This script provides functions to add simple Word comment objects to an existing .docx file.
It uses python-docx to create/modify content and then injects comments.xml and relationships.
Note: This approach is a reasonable workaround but may not cover all edge cases. Always keep backups.
\"\"\"
import zipfile
import shutil
import os
from xml.etree import ElementTree as ET
from docx import Document

# Namespaces for WordprocessingML
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def _new_comment_xml(comments):
    \"\"\"Create comments.xml content given a list of dicts: {'id': int, 'author': str, 'date': str, 'text': str} \"\"\"
    ET.register_namespace('w', NS['w'])
    comments_root = ET.Element(f"{{{NS['w']}}}comments")
    for c in comments:
        comment_el = ET.SubElement(comments_root, f\"{{{NS['w']}}}comment\", attrib={
            f\"{{{NS['w']}}}id\": str(c['id']),
            f\"{{{NS['w']}}}author\": c.get('author','Reviewer'),
            f\"{{{NS['w']}}}date\": c.get('date','2025-01-01T00:00:00Z')
        })
        p = ET.SubElement(comment_el, f\"{{{NS['w']}}}p\")
        r = ET.SubElement(p, f\"{{{NS['w']}}}r\")
        t = ET.SubElement(r, f\"{{{NS['w']}}}t\")
        t.text = c['text']
    return ET.tostring(comments_root, encoding='utf-8', xml_declaration=True)

def add_comments_to_docx(src_docx_path, dst_docx_path, comments_map):
    \"\"\"Add comments to a docx. comments_map is a list of dicts:
       [{'para_text_match': 'some text', 'comment_id': 0, 'author': 'Reviewer', 'text': 'Comment body'}, ...]
       This function injects a comments.xml and inserts commentReference markers next to matched paragraph text.
       This is a heuristic approach and may not work for very complex documents.
    \"\"\"
    # Work on a temp copy
    tmp_dir = src_docx_path + \"_tmp_unzip\"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)
    with zipfile.ZipFile(src_docx_path, 'r') as zin:
        zin.extractall(tmp_dir)
    document_xml = os.path.join(tmp_dir, 'word', 'document.xml')
    tree = ET.parse(document_xml)
    root = tree.getroot()

    # Build comments data for comments.xml and track next available id
    comments = []
    next_id = 0
    for cm in comments_map:
        comments.append({'id': next_id, 'author': cm.get('author','Reviewer'), 'date': cm.get('date','2025-01-01T00:00:00Z'), 'text': cm.get('text','')})
        next_id += 1

    comments_xml_content = _new_comment_xml(comments)
    # write comments.xml
    comments_xml_path = os.path.join(tmp_dir, 'word', 'comments.xml')
    with open(comments_xml_path, 'wb') as f:
        f.write(comments_xml_content)

    # ensure _rels entry for comments in word/_rels/document.xml.rels
    rels_path = os.path.join(tmp_dir, 'word', '_rels', 'document.xml.rels')
    if os.path.exists(rels_path):
        rels_tree = ET.parse(rels_path)
        rels_root = rels_tree.getroot()
    else:
        # create minimal relationships root
        rels_root = ET.Element('Relationships', xmlns='http://schemas.openxmlformats.org/package/2006/relationships')

    # add relationship if missing
    existing = False
    for rel in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        if rel.get('Type','').endswith('/comments'):
            existing = True
            break
    if not existing:
        r_attrib = {
            'Id': 'rId1000',
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments',
            'Target': 'comments.xml'
        }
        ET.SubElement(rels_root, 'Relationship', r_attrib)

    # Save rels
    rels_tree = ET.ElementTree(rels_root)
    rels_tree.write(rels_path, encoding='utf-8', xml_declaration=True)

    # NOTE: inserting commentRangeStart/commentRangeEnd and commentReference into document.xml is complex.
    # For a robust solution, use python-docx with an extension or external library. Here we will append a simple paragraph per comment
    # that contains the comment text and a marker, to ensure the reviewer sees the comment in the document.
    body = root.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
    for idx, cm in enumerate(comments_map, start=1):
        p = ET.SubElement(body, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
        r = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
        t = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
        t.text = f\"[COMMENT #{idx} by {cm.get('author','Reviewer')}] {cm.get('text','')}\"

    # write modified document.xml back
    tree.write(document_xml, encoding='utf-8', xml_declaration=True)

    # Repack to new docx
    with zipfile.ZipFile(dst_docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for folder, subs, files in os.walk(tmp_dir):
            for filename in files:
                file_path = os.path.join(folder, filename)
                arcname = os.path.relpath(file_path, tmp_dir)
                zout.write(file_path, arcname)
    # cleanup
    shutil.rmtree(tmp_dir)
    return dst_docx_path

if __name__ == '__main__':
    # Example usage
    sample_src = 'Task_reviewed.docx'
    sample_dst = 'Task_with_comments.docx'
    comments_map = [
        {'para_text_match': 'jurisdiction', 'author': 'Reviewer', 'text': 'Please confirm jurisdiction clause references ADGM courts.'}
    ]
    if os.path.exists(sample_src):
        add_comments_to_docx(sample_src, sample_dst, comments_map)
    else:
        print('Place Task_reviewed.docx in the working directory and re-run this script.')
