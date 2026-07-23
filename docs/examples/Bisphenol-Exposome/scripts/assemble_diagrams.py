#!/usr/bin/env python3
"""Pair each verbatim logged query (data/qN.rq) with its sparql_to_mermaid diagram,
write diagrams.json for readd_query_diagrams.py."""
import json
M = {
 0:"graph TD\nclassDef projected fill:lightgreen;\nclassDef literal fill:orange;\nclassDef iri fill:yellow;\n  v12(\"?ac50\"):::projected \n  v11(\"?ac50EP\")\n  v6(\"?assayEP\")\n  v7(\"?assayName\"):::projected \n  v4(\"?callEP\")\n  v3(\"?chem\")\n  v2(\"?chemLabel\"):::projected \n  v1(\"?dtxsid\"):::projected \n  v9(\"?effect\"):::projected \n  v8(\"?gene\"):::projected \n  v5(\"?mg\")\n  v10(\"?target\"):::projected \n  subgraph graph0[\"GRAPH biobricks-ice\"]\n    v3 --\"a\"--> c2([biolink:ChemicalEntity])\n    v4 --\"obo:IAO_0000136\"--> v3\n    v4 --\"sio:SIO_000300\"--> a([Active])\n    v4 --\"rdfs:label\"--> c([Call])\n    v3 --\"obo:RO_0000056\"--> v5\n    v5 --\"obo:OBI_0000299\"--> v4\n    v3 --\"edam:has_identifier\"--> v1\n    v6 --\"bao:BAO_0000209\"--> v5\n    v6 --\"ice:assay_entrez_gene_id\"--> v8\n    v6 --\"ice:mayInformOn\"--> v9\n    v6 --\"ice:throughMechanisticTarget\"--> v10\n  end",
 1:"graph TD\n  v3(\"?aop\") --\"obo:NCIT_C54571\"--> v4(\"?stressor\")\n  v4 --\"aop:has_chemical_entity\"--> v2(\"?chem\")\n  v3 --\"aop:has_molecular_initiating_event\"--> v7(\"?mie\")\n  v3 --\"aop:has_adverse_outcome\"--> v9(\"?ao\")\n  v3 --\"a\"--> c3([aop:AdverseOutcomePathway])",
 2:"graph TD\n  bind[/\"VALUES ?aop (152,314,522,535)\"/] --> v1(\"?aop\")\n  v1 --\"aop:has_key_event\"--> v2(\"?ke\")\n  v2 -.\"dc:title\".-> v3(\"?keTitle\")\n  v2 -.\"aop:OrganContext\".-> v5(\"?organ\")",
 3:"graph TD\n  bind[/\"VALUES ?gene (178 Entrez)\"/] --> v2(\"?gene\")\n  v2 --\"biolink:related_to\"--> v1(\"?disease MONDO\")\n  v1 --\"rdfs:label\"--> v3(\"?dlabel\")\n  v2 --\"rdfs:label\"--> v4(\"?sym\")",
 4:"graph TD\n  v4(\"?g\") --\"biolink:related_to\"--> v3(\"?d MONDO\")\n  v4 --\"biolink:category\"--> c([biolink:Gene])\n  bind[/\"count(?g) AS ?n_bg\"/]",
 5:"graph TD\n  bind[/\"VALUES ?d (232 MONDO)\"/] --> v2(\"?d\")\n  v5(\"?g\") --\"biolink:related_to\"--> v2\n  v5 --\"biolink:category\"--> c([biolink:Gene])\n  cnt[/\"count(?g) AS ?K\"/]",
 6:"graph TD\n  bind[/\"VALUES ?sym (183 symbols)\"/] --> v2(\"?sym\")\n  v4(\"?gene\") --\"rdfs:label\"--> v2\n  v4 --\"sio:010078\"--> v3(\"?prot\")\n  v3 --\"RO:0000056\"--> v1(\"?pw R-HSA\")\n  v1 --\"a\"--> c([up:Pathway])",
 7:"graph TD\n  bind[/\"VALUES ?sym (183 symbols)\"/] --> v1(\"?sym\")\n  v2(\"?gene\") --\"rdfs:label\"--> v1\n  v2 --\"sio:010078\"--> v3(\"?prot\")\n  v3 --\"RO:0002331\"--> v4(\"?go\")",
 8:"graph TD\n  v5(\"?gene\") --\"rdfs:label\"--> v6(\"?sym\")\n  v5 --\"sio:010078\"--> v4(\"?prot\")\n  v4 --\"RO:0000056\"--> v3(\"?pw R-HSA\")\n  v3 --\"a\"--> c([up:Pathway])\n  cnt[/\"count(?sym) AS ?N_react\"/]",
 9:"graph TD\n  v3(\"?gene\") --\"rdfs:label\"--> v5(\"?sym\")\n  v3 --\"sio:010078\"--> v4(\"?prot\")\n  v4 --\"RO:0002331\"--> v6(\"?go\")\n  cnt[/\"count(?sym) AS ?N_go\"/]",
 10:"graph TD\n  bind[/\"VALUES ?pw (42 R-HSA)\"/] --> v2(\"?pw\")\n  v5(\"?gene\") --\"rdfs:label\"--> v7(\"?sym\")\n  v5 --\"sio:010078\"--> v6(\"?prot\")\n  v6 --\"RO:0000056\"--> v2\n  cnt[/\"count(?sym) AS ?K\"/]",
 11:"graph TD\n  bind[/\"VALUES ?go (47 GO terms)\"/] --> v2(\"?go\")\n  v5(\"?gene\") --\"rdfs:label\"--> v7(\"?sym\")\n  v5 --\"sio:010078\"--> v6(\"?prot\")\n  v6 --\"RO:0002331\"--> v2\n  cnt[/\"count(?sym) AS ?K\"/]",
 12:"graph TD\n  v3(\"?chem\") --\"a\"--> c([biolink:ChemicalEntity])\n  v3 --\"obo:RO_0000056\"--> v5(\"?mg\")\n  v5 --\"obo:OBI_0000299\"--> v4(\"?ep\")\n  v4 --\"obo:IAO_0000136\"--> v3\n  v4 --\"rdfs:label\"--> v2(\"?useType (Functional Use)\")\n  v4 --\"sio:SIO_000300\"--> v6(\"?useValue\")",
 13:"graph TD\n  bind[/\"VALUES ?g (183 Entrez)\"/] --> v1(\"?g\")\n  v1 --\"rdfs:label\"--> v2(\"?sym\")\n  v1 --\"digcfdekg:geneToTrait\"--> v3(\"?trait\")\n  v3 -.\"rdfs:label\".-> v4(\"?tlabel\")",
 14:"graph TD\n  v4(\"?chem\") --\"a\"--> c([biolink:ChemicalEntity])\n  v4 --\"edam:has_identifier\"--> v1(\"?cas\")\n  v4 --\"edam:has_identifier\"--> v2(\"?dtxsid\")\n  v4 --\"rdfs:label\"--> v3(\"?label\")",
 15:"graph TD\n  bind[/\"VALUES ?g (71 Entrez targets)\"/] --> v1(\"?g\")\n  v1 --\"rdfs:label\"--> v2(\"?sym\")\n  v1 -.\"rdfs:comment\".-> v3(\"?name\")",
}
out=[]
for i in range(16):
    sparql=open(f"data/q{i}.rq").read().strip()
    out.append({"sparql":sparql,"mermaid":M[i]})
json.dump(out,open("diagrams.json","w"),indent=1)
print("wrote diagrams.json with",len(out),"pairs")
