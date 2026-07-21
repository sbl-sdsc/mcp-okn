import sys, json; sys.path.insert(0,'scripts')
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import okn_figstyle as F; F.apply_style()
D='data'; FIG='figures'
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','sky':'#56B4E9','grey':'#7f7f7f'}
NICE={'CHR_poor_or_fair_health':'Poor/fair self-rated health','CHR_frequent_physical_distress':'Frequent physical distress',
 'CHR_children_in_poverty':'Children in poverty','CDCP_NO_PHY_ACTV_ADULT_A':'No leisure physical activity',
 'SAIPE_PCT_POV':'Poverty rate (SAIPE)','ACS_PCT_LT_HS':'Adults without high-school diploma',
 'CHR_high_school_completion':'High-school completion','CDCSVI':'CDC Social Vulnerability Index',
 'CHR_children_eligible_for_free_or_reduced_price_lunch':'Free/reduced-price school lunch',
 'CHR_premature_age-adjusted_mortality':'Premature age-adjusted mortality','FEA_SNAP_BENEFITS_PER_CAPITA':'SNAP benefits per capita',
 'CHR_premature_death':'Premature death (YPLL)','CDCP_SLEEP_LESS7HR_ADULT_A':'Short sleep (<7 h)',
 'ACS_PCT_HH_FOOD_STMP':'Households on food stamps','ACS_PCT_HH_PUB_ASSIST':'Households on public assistance',
 'CHR_life_expectancy':'Life expectancy','ACS_PER_CAPITA_INC':'Per-capita income','ACS_MEDIAN_HH_INC':'Median household income',
 'CHR_food_environment_index':'Food environment index','ACS_PCT_BACHELOR_DGR':'Adults with a bachelor degree',
 'CHR_broadband_access':'Broadband access','ACS_PCT_MEDICAID_ANY':'Any Medicaid coverage','MHSVI_RPL_THEMES_ALL':'Minority-health SVI (all themes)',
 'ACS_PCT_UNINSURED':'Uninsured (ACS)','CHR_uninsured_adults':'Uninsured adults (CHR)','CHR_rural':'Rural population share',
 'CHR_limited_access_to_healthy_foods':'Limited access to healthy foods','ACS_GINI_INDEX':'Income inequality (Gini)',
 'PM25_conc':'PM$_{2.5}$ concentration','places_county_prev':'PLACES place-level prevalence (aggregated)'}
nice=lambda s: NICE.get(s,s.replace('_',' '))
co=pd.read_csv(D+'/county_sdoh_correlations.csv'); mv=pd.read_csv(D+'/county_multivariable_model.csv')
co=co[co.variable!='places_county_prev']
fig,axes=plt.subplots(1,2,figsize=(14.6,7.0))
ax=axes[0]
d=co.reindex(co.pearson_r.abs().sort_values(ascending=False).index).head(20).iloc[::-1]
cols=[OK['red'] if v>0 else OK['blue'] for v in d.pearson_r]
ax.barh(range(len(d)),d.pearson_r,color=cols,height=0.72)
ax.set_yticks(range(len(d))); ax.set_yticklabels([nice(s) for s in d.variable],fontsize=8.5)
ax.axvline(0,color='#333',lw=0.8); ax.set_xlabel("Pearson r vs county diabetes prevalence")
ax.set_xlim(-1,1)
for i,(r,n) in enumerate(zip(d.pearson_r,d.n)):
    ax.text(r+(0.03 if r>0 else -0.03),i,f'{r:+.2f}',va='center',ha='left' if r>0 else 'right',fontsize=7.5)
F.panel_title(ax,'A','Univariable association (all FDR<0.05)')
ax=axes[1]
m=mv[mv.predictor!='(intercept)'].copy().iloc[::-1]
cols=[OK['red'] if v>0 else OK['blue'] for v in m.beta]
ax.barh(range(len(m)),m.beta,xerr=1.96*m.se,color=cols,height=0.68,error_kw=dict(ecolor='#333',lw=1.0,capsize=2.5))
ax.set_yticks(range(len(m))); ax.set_yticklabels([nice(s) for s in m.predictor],fontsize=8.5)
ax.axvline(0,color='#333',lw=0.8)
ax.set_xlabel('standardized β (percentage points per 1 SD) ± 95% CI')
for i,(b,p) in enumerate(zip(m.beta,m.p)):
    lab='n.s.' if p>=0.05 else ('***' if p<1e-3 else ('**' if p<1e-2 else '*'))
    ax.text(b+(0.045 if b>0 else -0.045),i,lab,va='center',ha='left' if b>0 else 'right',fontsize=8)
r2=float(mv.r2.iloc[0]); n=int(mv.n.iloc[0])
F.panel_title(ax,'B',f'Multivariable model (n={n}, R²={r2:.3f})')
F.finalize(fig,7,f'{FIG}/fig7_sdoh.png')
print('fig7 done')
