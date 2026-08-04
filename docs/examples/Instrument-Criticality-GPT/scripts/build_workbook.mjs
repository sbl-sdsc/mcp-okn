import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";
import JSZip from "jszip";

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),"..");
const dataDir=path.join(root,"data");
const outPath=path.join(root,"Instrument-Criticality-GPT_results.xlsx");
const previewDir="/tmp/instrument-criticality-previews";
const read=async n=>JSON.parse(await fs.readFile(path.join(dataDir,n),"utf8"));
const [stats,ranked,instruments,platforms,archives,routes,people,countries,cities,substitution]=await Promise.all([
  read("analysis_stats.json"),read("ranked_instruments.json"),read("catalog_instruments.json"),
  read("catalog_platforms.json"),read("catalog_archives.json"),read("dependency_routes.json"),
  read("cross_side_people.json"),read("country_attention.json"),read("city_attention_flagged.json"),
  read("substitutability.json")
]);

const wb=Workbook.create();
const navy="#17365D", blue="#3366CC", light="#D9EAF7", orange="#F28E2B", green="#59A14F", grey="#666666";

function clean(v){ return v===undefined||v===null ? "" : v; }
function matrix(rows,cols){ return rows.map(r=>cols.map(c=>clean(r[c.key]))); }
function styleTitle(sheet,lastCol,title,note){
  sheet.mergeCells(`A1:${lastCol}1`);
  sheet.getRange("A1").values=[[title]];
  sheet.getRange(`A1:${lastCol}1`).format={fill:navy,font:{bold:true,color:"#FFFFFF"},rowHeight:28};
  sheet.mergeCells(`A2:${lastCol}2`);
  sheet.getRange("A2").values=[[note]];
  sheet.getRange(`A2:${lastCol}2`).format={fill:"#EEF3F8",font:{italic:true,color:"#44546A"},wrapText:true,rowHeight:34};
  sheet.showGridLines=false;
}
function addDataSheet(name,title,note,rows,cols,tableName){
  const s=wb.worksheets.add(name);
  const last=String.fromCharCode(64+cols.length);
  styleTitle(s,last,title,note);
  const block=[cols.map(c=>c.label),...matrix(rows,cols)];
  s.getRangeByIndexes(3,0,block.length,cols.length).values=block;
  s.getRange(`A4:${last}4`).format={fill:blue,font:{bold:true,color:"#FFFFFF"},wrapText:true,rowHeight:30,borders:{preset:"all",style:"thin",color:"#D9E1F2"}};
  if(rows.length){
    s.getRange(`A5:${last}${rows.length+4}`).format={borders:{preset:"all",style:"thin",color:"#E7E6E6"},verticalAlignment:"top",wrapText:true};
    const t=s.tables.add(`A4:${last}${rows.length+4}`,true,tableName); t.style="TableStyleMedium2"; t.showFilterButton=true;
  }
  s.freezePanes.freezeRows(4);
  s.getRange(`A4:${last}${Math.max(5,rows.length+4)}`).format.autofitColumns();
  s.getRange(`A4:${last}${Math.max(5,rows.length+4)}`).format.autofitRows();
  return s;
}

// Dashboard
const dash=wb.worksheets.add("Dashboard");
styleTitle(dash,"N","Instrument-Criticality decision dashboard","Federation-only scientific-dependence priority. Mission status and engineering substitute readiness must be checked separately.");
dash.getRange("A4:H6").values=[
  ["Spaceborne instruments",stats.space_instruments,"Named/rankable",stats.ranked_named_instruments,"With measured uptake",stats.instruments_with_any_uptake,"Cross-community ORCIDs",stats.exact_people_orcids],
  ["Tier A",stats.tier_A,"Tier B",stats.tier_B,"No uptake",stats.instruments_no_uptake,"High footprint/no uptake",stats.high_footprint_no_uptake],
  ["Top instrument",stats.top_instrument,"Top score",stats.top_score,"Spearman(score, footprint)",stats.spearman_score_dataset,"Exact DOI papers",stats.matched_doi_papers]
];
dash.getRange("A4:H6").format={borders:{preset:"all",style:"thin",color:"#B4C7E7"},wrapText:true};
dash.getRange("A4:H6").conditionalFormats.add("colorScale",{criteria:[{type:"lowestValue",color:"#FFFFFF"},{type:"highestValue",color:"#D9EAF7"}]});
const top=ranked.filter(r=>r.specificity==="named instrument").sort((a,b)=>a.rank-b.rank).slice(0,15);
dash.getRange("A9:B24").values=[["Instrument","Criticality score"],...top.map(r=>[r.instrument_name,r.criticality_score])];
dash.getRange("D9:E13").values=[["Uptake band","Instrument count"],["0",stats.uptake_zero],["1–5",stats.uptake_one_to_five],["6–20",stats.uptake_six_to_twenty],[">20",stats.uptake_over_twenty]];
for(const rg of ["A9:B24","D9:E13"]){dash.getRange(rg).format={borders:{preset:"all",style:"thin",color:"#D9E1F2"}};}
dash.getRange("A9:B9").format={fill:blue,font:{bold:true,color:"#FFFFFF"}};
dash.getRange("D9:E9").format={fill:orange,font:{bold:true,color:"#FFFFFF"}};
const c1=dash.charts.add("bar",dash.getRange("A9:B24")); c1.title="Top 15 evidence-based criticality scores"; c1.hasLegend=false; c1.setPosition("G9","N25");
const c2=dash.charts.add("bar",dash.getRange("D9:E13")); c2.title="Distribution of evaluation-context model uptake"; c2.hasLegend=false; c2.setPosition("A27","H41");
dash.getRange("A43:N46").merge(); dash.getRange("A43").values=[["Decision rule: use Tier A/B as an evidence-review queue. Before acting, require current mission status, replacement readiness, channel-level equivalence, calibration overlap, product lineage, and an observing-system denial or sensitivity analysis."]];
dash.getRange("A43:N46").format={fill:"#FFF2CC",font:{bold:true,color:"#7F6000"},wrapText:true,verticalAlignment:"center"};
dash.freezePanes.freezeRows(2); dash.showGridLines=false;

// Ranked results
const rankedCols=[
 {key:"rank",label:"Rank"},{key:"instrument_name",label:"Instrument"},{key:"criticality_score",label:"Score"},{key:"tier",label:"Tier"},
 {key:"evaluation_models",label:"Eval models"},{key:"text_models",label:"Instrument-text models"},{key:"doi_models",label:"DOI models"},
 {key:"platform_text_models",label:"Platform-text models"},{key:"route_count",label:"Route count"},{key:"union_models",label:"Union models"},
 {key:"space_dataset_count",label:"Dataset footprint*"},{key:"unique_variable_count",label:"Unique variables"},{key:"minimum_alternatives",label:"Minimum alternatives"},
 {key:"platforms",label:"Platforms"},{key:"routes",label:"Evidence routes"},{key:"specificity",label:"Specificity"}
];
const rankedRows=ranked.filter(r=>r.specificity==="named instrument").sort((a,b)=>a.rank-b.rank);
const rs=addDataSheet("Ranked Results","Ranked observing infrastructure","*Dataset footprint is a platform-mediated upper bound, not bytes or direct instrument records. Route counts overlap and must not be summed.",rankedRows,rankedCols,"RankedResultsTable");
rs.getRange(`C5:C${rankedRows.length+4}`).conditionalFormats.add("colorScale",{criteria:[{type:"lowestValue",color:"#F2F2F2"},{type:"percentile",value:80,color:"#FFF2CC"},{type:"highestValue",color:"#C6E0B4"}]});
rs.getRange(`N5:P${rankedRows.length+4}`).format.columnWidth=34;

// Catalog sheets
addDataSheet("Instrument Catalogue","NASA instrument catalogue","All 921 instrument nodes. Counts are graph-record counts and platform-mediated where noted.",instruments,[
 {key:"instrument_name",label:"Instrument"},{key:"platform_count",label:"Platforms"},{key:"dataset_count",label:"Datasets*"},{key:"archive_count",label:"Archives*"},{key:"publication_count",label:"Publications*"},{key:"science_keyword_count",label:"Science keywords"},{key:"instrument",label:"IRI"}
],"InstrumentCatalogueTable");
addDataSheet("Platform Catalogue","NASA platform catalogue","All 455 platform nodes, including non-spaceborne platform types.",platforms,[
 {key:"platform_name",label:"Platform"},{key:"platform_type",label:"Type"},{key:"instrument_count",label:"Instruments"},{key:"dataset_count",label:"Datasets"},{key:"archive_count",label:"Archives"},{key:"publication_count",label:"Publications"},{key:"platform",label:"IRI"}
],"PlatformCatalogueTable");
addDataSheet("Archives","Archive and data-center catalogue","All 189 data centers; counts follow NASA graph links.",archives.sort((a,b)=>(b.dataset_count||0)-(a.dataset_count||0)),[
 {key:"center_name",label:"Archive/data center"},{key:"dataset_count",label:"Datasets"},{key:"platform_count",label:"Platforms"},{key:"instrument_count",label:"Instruments"},{key:"publication_count",label:"Publications"},{key:"center",label:"IRI"}
],"ArchiveTable");

// Dependency route table
const routeRows=[];
for(const [route,arr] of Object.entries(routes)){
 for(const r of arr){routeRows.push({route,...r});}
}
addDataSheet("Dependency Routes","Route-specific dependency evidence","Each row is route-specific; routes overlap. Text routes identify mentions, while DOI–dataset–platform is structural but sensor attribution is indirect.",routeRows,[
 {key:"route",label:"Route"},{key:"instrument_name",label:"Instrument"},{key:"evaluation_models",label:"Eval models"},{key:"text_models",label:"Text models"},
 {key:"doi_models",label:"DOI models"},{key:"platform_text_models",label:"Platform-text models"},{key:"union_models",label:"Union models"},
 {key:"evaluation_papers",label:"Eval papers"},{key:"text_papers",label:"Text papers"},{key:"doi_climate_papers",label:"DOI papers"},{key:"platform_text_papers",label:"Platform papers"}
],"DependencyRoutesTable");

// People / places
addDataSheet("Cross-side People","People spanning modelling and observation","Conservative identity: exact author name inside the same DOI-matched paper; ORCID reported when available.",people.sort((a,b)=>(b.models||0)-(a.models||0)),[
 {key:"author_name",label:"Author"},{key:"orcid",label:"ORCID"},{key:"shared_doi_papers",label:"Shared DOI papers"},{key:"models",label:"Model sources"},{key:"nasa_datasets",label:"NASA datasets"}
],"PeopleTable");
addDataSheet("Country Attention","Country-level research-attention proxy","Text mentions, not study sites. Thin evidence means fewer than three model+instrument papers.",countries.sort((a,b)=>(b.instrument_model_papers||0)-(a.instrument_model_papers||0)),[
 {key:"country_name",label:"Country"},{key:"iso",label:"ISO"},{key:"papers",label:"All papers"},{key:"model_papers",label:"Model papers"},{key:"instrument_model_papers",label:"Model+instrument papers"},{key:"models",label:"Model sources"},{key:"latitude",label:"Latitude*"},{key:"longitude",label:"Longitude*"}
],"CountryAttentionTable");
addDataSheet("City Mentions FLAGGED","City mention extract — not for decisions","Visible homonym/geocoding errors make this an audit extract only. Do not treat coordinates as study sites.",cities,[
 {key:"city_name",label:"City"},{key:"country_code",label:"Country code"},{key:"latitude",label:"Latitude"},{key:"longitude",label:"Longitude"},{key:"papers",label:"All papers"},{key:"model_papers",label:"Model papers"},{key:"instrument_model_papers",label:"Model+instrument papers"},{key:"models",label:"Model sources"}
],"CityFlaggedTable");
addDataSheet("Substitution Proxy","Sparse variable-based substitution proxy","Only 30 of 82 exact-matched space instruments have variable semantics. Zero alternatives means no alternative in this graph subset, not no physical substitute.",substitution.sort((a,b)=>(b.unique_variable_count||0)-(a.unique_variable_count||0)),[
 {key:"instrument_name",label:"Instrument"},{key:"variable_count",label:"Variables"},{key:"unique_variable_count",label:"Unique variables"},{key:"minimum_alternatives",label:"Minimum alternatives"},{key:"mean_alternatives",label:"Mean alternatives"}
],"SubstitutionTable");

// Methods
const methods=wb.worksheets.add("Methods & Rules");
styleTitle(methods,"H","Methods, scoring, and limitations","This sheet is the visible audit trail for ranking interpretation.");
const methodRows=[
 ["Abbreviations","E = evaluation-context models; T = direct instrument-text models; D = DOI–dataset–platform models; P = platform-text models; U = unique graph variables"],
 ["Score formula","100 × [0.45·L(E) + 0.15·L(max(T−E,0)) + 0.25·L(D) + 0.10·L(P) + 0.05·I(U>0)]"],
 ["Scaling","L(x)=log1p(x)/log1p(maximum observed on that axis)"],
 ["E","Distinct models in evaluation-context instrument-text route"],
 ["T","Distinct models in direct instrument-text route"],
 ["D","Distinct models in DOI–dataset–platform route"],
 ["P","Distinct models in platform-text route"],
 ["U","Variables with zero alternatives among exact-matched space instruments"],
 ["Tiers","A ≥70; B 40–69.9; C <40; generic labels not rankable"],
 ["Many-model risk",">20 evaluation-context models"],
 ["Scarce-variable candidate","≤5 evaluation-context models and ≥1 unique graph variable"],
 ["High-footprint/no-uptake","Dataset footprint >75th percentile (80) and zero measured uptake"],
 ["Spaceborne scope","Earth Observation Satellites; Solar/Space Observation Satellites; Navigation Satellites; Space Stations/Crewed Spacecraft; Space-based Platforms; Spacecraft"],
 ["Primary limitation","No direct Dataset→Instrument edge and no byte-volume field"],
 ["Operational limitation","No populated platform start/end date or mission-status field"],
 ["Substitution limitation","Variable semantics present for 30/82 exact-matched space instruments"],
 ["Geography limitation","Country/city nodes are text mentions, not study sites; city homonyms are unreliable"],
 ["People limitation","Global exact names are ambiguous; conservative count requires same DOI context"],
 ["Corpus limitation","2,000 climate papers; zero uptake means absent from measured routes only"],
 ["Literature labels","SUPPORTED; PARTIALLY SUPPORTED; NOVEL; UNRESOLVED; CONTRADICTED"],
 ["KG versions","nasa-gesdisc-kg v0.0.6; climatemodelskg v0.0.15"],
 ["External evidence","Paperclip discovery; NASA, JAXA, NOAA, and NSIDC primary records"]
];
methods.getRange("A4:B26").values=[["Rule/field","Definition"],...methodRows];
methods.getRange("A4:B4").format={fill:navy,font:{bold:true,color:"#FFFFFF"}};
methods.getRange("A4:B26").format={borders:{preset:"all",style:"thin",color:"#D9E1F2"},wrapText:true,verticalAlignment:"top"};
methods.getRange("A:B").format.columnWidth=34; methods.getRange("B:B").format.columnWidth=90; methods.freezePanes.freezeRows(4); methods.showGridLines=false;

await fs.mkdir(path.dirname(outPath),{recursive:true});
const out=await SpreadsheetFile.exportXlsx(wb); await out.save(outPath);
await fs.mkdir(previewDir,{recursive:true});
for(const name of ["Dashboard","Ranked Results","Instrument Catalogue","Platform Catalogue","Archives","Dependency Routes","Cross-side People","Country Attention","City Mentions FLAGGED","Substitution Proxy","Methods & Rules"]){
  const blob=await wb.render({sheetName:name,range:"A1:N40",scale:0.8,format:"png"});
  await fs.writeFile(path.join(previewDir,name.replaceAll(" ","_")+".png"),new Uint8Array(await blob.arrayBuffer()));
}
// Normalize artifact-tool's namespace-prefixed workbook.xml to the equivalent
// default-namespace form expected by strict OOXML readers and the report validator.
const zip=await JSZip.loadAsync(await fs.readFile(outPath));
const workbookXml=await zip.file("xl/workbook.xml").async("string");
const normalized=workbookXml
  .replace('xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main"','xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"')
  .replaceAll("<x:","<").replaceAll("</x:","</");
zip.file("xl/workbook.xml",normalized);
await fs.writeFile(outPath,await zip.generateAsync({type:"nodebuffer"}));
const summary=await wb.inspect({kind:"sheet",include:"id,name",maxChars:4000});
console.log(summary.ndjson||summary);
console.log(`saved ${outPath}`);
