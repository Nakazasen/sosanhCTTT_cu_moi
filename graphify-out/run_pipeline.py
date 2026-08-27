import json
import os
import multiprocessing
from pathlib import Path
from datetime import datetime, timezone
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report
from graphify.detect import save_manifest
from graphify.cli import _stamped_manifest_files

def main():
    root_path = '.'
    
    # 1. Semantic fallback
    sem_path = Path('graphify-out/.graphify_semantic.json')
    if not sem_path.exists():
        sem_path.write_text(json.dumps({'nodes':[],'edges':[],'hyperedges':[],'input_tokens':0,'output_tokens':0}), encoding='utf-8')
    
    # 2. Merge AST + Semantic
    ast = json.loads(Path('graphify-out/.graphify_ast.json').read_text(encoding='utf-8'))
    sem = json.loads(sem_path.read_text(encoding='utf-8'))
    
    seen = {n['id'] for n in ast['nodes']}
    merged_nodes = list(ast['nodes'])
    for n in sem['nodes']:
        if n['id'] not in seen:
            merged_nodes.append(n)
            seen.add(n['id'])
            
    merged_edges = ast['edges'] + sem['edges']
    merged_hyperedges = sem.get('hyperedges', [])
    merged = {
        'nodes': merged_nodes,
        'edges': merged_edges,
        'hyperedges': merged_hyperedges,
        'input_tokens': sem.get('input_tokens', 0),
        'output_tokens': sem.get('output_tokens', 0),
    }
    Path('graphify-out/.graphify_extract.json').write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Merged: {len(merged_nodes)} nodes, {len(merged_edges)} edges ({len(ast['nodes'])} AST + {len(sem['nodes'])} semantic)")

    # 3. Build Graph
    extraction = merged
    detection = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding='utf-8'))
    
    G = build_from_json(extraction, root=root_path, directed=False)
    if G.number_of_nodes() == 0:
        print("ERROR: Graph is empty.")
        return
        
    communities = cluster(G)
    cohesion = score_all(G, communities)
    tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    
    # Generate intelligent semantic labels for communities
    labels = {}
    for cid, nodes in communities.items():
        node_names = " ".join([str(n) for n in nodes[:15]]).lower()
        if "comparator" in node_names or "compare" in node_names or "diff" in node_names:
            labels[cid] = "Comparison Engine & Image Diffing"
        elif "excel" in node_names or "sheet" in node_names or "workbook" in node_names:
            labels[cid] = "Excel COM & Preprocessing"
        elif "pdf" in node_names or "render" in node_names or "fitz" in node_names:
            labels[cid] = "PDF Service & PageSetup"
        elif "ui" in node_names or "window" in node_names or "widget" in node_names or "style" in node_names:
            labels[cid] = "Modern Tkinter UI & Theme"
        elif "report" in node_names or "cleanup" in node_names:
            labels[cid] = "Reporting & Memory Cleanup"
        elif "test" in node_names:
            labels[cid] = "Automated Test Suite"
        elif "config" in node_names or "settings" in node_names or "utils" in node_names:
            labels[cid] = "Utilities & Configuration"
        else:
            labels[cid] = f"Community {cid} Components"
            
    questions = suggest_questions(G, communities, labels)
    
    to_json(G, communities, 'graphify-out/graph.json')
    report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, root_path, suggested_questions=questions)
    Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    Path('graphify-out/.graphify_labels.json').write_text(json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding='utf-8')
    
    # 4. Diagnostics
    summary = diagnose_extraction(extraction, directed=False, root=root_path)
    print(format_diagnostic_report(summary))
    
    # 5. Export HTML
    os.system("graphify export html")
    
    # 6. Save Manifest
    try:
        _corpus = detection.get('all_files') or detection['files']
        _manifest_files = _stamped_manifest_files(_corpus, extraction, Path(root_path))
        _scan = {f for fl in _corpus.values() for f in fl}
        save_manifest(_manifest_files, root=root_path, scan_corpus=_scan)
    except Exception as e:
        print(f"Manifest note: {e}")
    
    # 7. Cost tracker
    cost_path = Path('graphify-out/cost.json')
    cost = {'runs': [], 'total_input_tokens': 0, 'total_output_tokens': 0}
    cost['runs'].append({
        'date': datetime.now(timezone.utc).isoformat(),
        'input_tokens': 0,
        'output_tokens': 0,
        'files': detection.get('total_files', 0),
    })
    cost_path.write_text(json.dumps(cost, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print(f"Graph complete: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities.")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
