import json,glob,os
SRC="/sessions/affectionate-jolly-ramanujan/mnt/.claude/projects/-Users-peter-Library-Application-Support-Claude-local-agent-mode-sessions-add4cb4c-ea1e-402a-94dc-95fef2a8a1da-a3f85abe-537c-4d9f-9d6d-83586c51feaa-local-19f19c01-bebe-451a-b5a8-77d1f9654a77-outputs/bc1023f4-080d-4c12-bc3d-b0e7569137a0/tool-results"
seen={}; 
for f in sorted(glob.glob(SRC+"/*get_query_log*.txt"),key=os.path.getmtime):
    try: q=json.load(open(f))["result"]
    except: continue
    for e in q:
        key=(e.get("timestamp",""),(e.get("sparql","") or "")[:120])
        seen[key]=e
q=sorted(seen.values(),key=lambda e:e.get("timestamp",""))
o=["# Bone Health Spaceflight-Omics Study — SPARQL Reproducibility Transcript","",
"- **Date:** 2026-07-08 · **Model:** claude-opus-4-8",
"- **Endpoint:** OKN federated SPARQL (https://apps.okn.us/federation/sparql)",
"- **Substantive SPARQL queries logged:** %d (merged across log scopes; a create_chat_transcript reset the log mid-run)"%len(q),"",
"KG versions (get_kg_version): spoke-genelab v0.0.2 · spoke-okn v0.0.6 · rdkg v0.0.1 · digcfdekg v0.0.1 · prokn v0.0.5 · biobricks-aopwiki v0.0.4 · gene-expression-atlas-okn v0.0.3 · biohealth v0.0.4 · ubergraph v0.0.2","",
"Rules: Space-Flight-vs-Ground direction; genotype-clean comparability (WT and Nrf2-KO); adj_p<=0.05 primary, |log2FC|>=1 effect cut; ortholog collapse max|log2FC| via IS_ORTHOLOG_MGiG; cross-KG joins on Entrez (direct) and, for GO enrichment, prokn via the Entrez->HGNC gene-symbol bridge (lower-confidence).","","---",""]
for i,e in enumerate(q,1):
    g=e.get("graphs",""); g=", ".join(g) if isinstance(g,list) else g
    o+=["### Query %d — %s"%(i,e.get("timestamp","")),"Graphs: %s · rows returned: %s"%(g,e.get("row_count","?")),"","```sparql",(e.get("sparql","") or "").strip(),"```",""]
open("/sessions/affectionate-jolly-ramanujan/mnt/bone-health/bone_reproducibility_transcript.md","w").write("\n".join(o))
print("merged transcript:",len(q),"queries")
