import sys; sys.path.insert(0,'/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics/scripts')
from mechanistic_map import render_mechanistic_map
D='/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics'
modules={
 "Mitochondrial ATP synthase / OXPHOS":["ATP5F1A","ATP5F1C","ATP5F1D","ATP5PO","ATP5PD","UQCRH","COX7C","NDUFB1","MFN2","HIGD1A"],
 "ER stress / unfolded-protein response":["HSPA5","HSP90B1","HSP90AA1","PDIA6","SDF2L1","CRELD2","MANF","SSR1","BAG3"],
 "Fluid / ion & pressure regulation":["AQP1","CA8","CA9","NPPA","CLIC5","SLN","ATP2A3","TRPC1"],
 "Retinal / phototransduction & RPE":["RLBP1","PRSS56","PDE2A","RGS9BP","CABP5","STOML3","CALB1"],
 "Vascular remodelling / ECM":["APLNR","UNC5B","P4HA1","GFPT2","FRZB","DKK3","TLL1","UST"],
 "Circadian & immediate-early stress":["ARNTL","DBP","NFIL3","NR4A1","NR4A3","GADD45A","MSRA"],
}
drugs={
 "Mitochondrial ATP synthase / OXPHOS":["Idebenone","Elamipretide*"],
 "ER stress / unfolded-protein response":["4-PBA*","TUDCA*"],
 "Fluid / ion & pressure regulation":["Acetazolamide","Amiloride*"],
 "Retinal / phototransduction & RPE":["Retinoid supplementation*"],
 "Vascular remodelling / ECM":["Pazopanib (probe)*"],
 "Circadian & immediate-early stress":["Timed light / melatonin*"],
}
render_mechanistic_map(
  anchor="Spaceflight-Associated\nNeuro-ocular Syndrome (SANS)",
  modules=modules, drugs=drugs,
  out_path=f"{D}/figures/fig6_mechanistic_map.png",
  title="SANS gene–module–countermeasure mechanistic map (entities retrieved from Proto-OKN sources)")
print("fig6 done")
