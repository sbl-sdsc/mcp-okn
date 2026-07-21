import sys
sys.path.insert(0,'/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/scripts')
from mechanistic_map import render_mechanistic_map
# Modules are a DECLARED synthesis over the Tier-A/B consensus core (report §5.1) grouped by the
# GO / Reactome enrichment of §6.1-6.2. Every gene and drug shown was actually retrieved by a
# logged federated query; the module assignment is the only authored layer.
modules = {
 "APP processing &\nAβ generation":        ["APP","BACE1","PSEN1","PSEN2","NCSTN","APH1B","ADAM10"],
 "Aβ clearance &\nendolysosomal traffic":  ["SORL1","PICALM","BIN1","CD2AP","IDE","MME","ABCA7"],
 "Lipid & cholesterol\nmetabolism":        ["APOE","CLU","ABCA1","APOC1","DHCR24","LRP1","SORT1"],
 "Microglial &\ncomplement immunity":      ["TREM2","CR1","CD33","MS4A4A","MS4A6A","INPP5D","PLCG2"],
 "Tau, kinases &\ncytoskeleton":           ["MAPT","GSK3A","GSK3B","MARK4","CDK5","PTK2B","FERMT2"],
 "Synaptic & neuronal\nfunction":          ["DLG4","SYN1","SYP","GRIN2B","RIMS1","NEFL","BDNF"],
 "Proteostasis, mitochondria\n& oxidative stress": ["SQSTM1","PRKN","PINK1","SOD1","HMOX1","TOMM40","SHARPIN"],
 "Vascular & BBB\nintegrity":              ["ACE","NOS3","A2M","PECAM1","HSPG2","AGER","CST3"],
}
# drugs are keyed BY MODULE (the class each compound acts through)
drugs = {
 "APP processing &\nAβ generation":        ["lecanemab","donanemab","verubecestat","semagacestat","tramiprosate"],
 "Aβ clearance &\nendolysosomal traffic":  ["bumetanide","sirolimus"],
 "Lipid & cholesterol\nmetabolism":        ["simvastatin","bexarotene","obicetrapib","pioglitazone"],
 "Microglial &\ncomplement immunity":      ["masitinib","pepinemab","montelukast","celecoxib"],
 "Tau, kinases &\ncytoskeleton":           ["semorinemab","tideglusib","lithium","saracatinib","nilotinib"],
 "Synaptic & neuronal\nfunction":          ["donepezil","memantine","rivastigmine","galantamine","levetiracetam"],
 "Proteostasis, mitochondria\n& oxidative stress": ["vorinostat","curcumin"],
 "Vascular & BBB\nintegrity":              ["telmisartan","perindopril","nilvadipine"],
}
render_mechanistic_map(
    anchor="Alzheimer disease\n(MONDO:0004975)",
    modules=modules, drugs=drugs,
    out_path="/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/figures/fig10_mechanistic_map.png",
    title="Alzheimer's disease mechanistic map: anchor → module → gene → therapeutic class",
    subtitle="Genes: cross-KG consensus core (spoke-okn · digcfdekg · prokn · biomarkerkg · rdkg · gene-expression-atlas-okn). Drugs: prokn AD indications + targets.",
    footnote="Hypothesis-generating. Module assignment is an author synthesis over the enrichment, not a KG assertion; drug approval status varies within a class (see §6.3).",
    anchor_kind="Disease",
)
print("ok")
