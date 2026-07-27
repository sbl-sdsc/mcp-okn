import pandas as pd, s2sphere as s2, numpy as np
rc=pd.read_csv('data/reach_county.csv.gz', dtype=str)
rcell=pd.read_csv('data/reach_cells.csv.gz', dtype=str)
m=rc.merge(rcell,on='comid')[['fips','s2']].drop_duplicates()
def ll(cid):
    p=s2.CellId(int(cid)).to_lat_lng(); return p.lat().degrees, p.lng().degrees
m=m.dropna()
sub=m.groupby('fips').head(400)
lat,lng=zip(*[ll(c) for c in sub.s2])
sub=sub.assign(lat=lat,lng=lng)
cen=sub.groupby('fips').agg(lat=('lat','median'), lng=('lng','median')).reset_index()
# add flood-cell derived centroids for counties not in the reach network
j=pd.read_csv('data/flood_cells_joined.csv', dtype={'id':str,'fips':str}).drop_duplicates('id')
la,lo=zip(*[ll(c) for c in j.id])
j2=j.assign(lat=la,lng=lo).groupby('fips').agg(lat=('lat','median'),lng=('lng','median')).reset_index()
cen=pd.concat([cen, j2[~j2.fips.isin(cen.fips)]], ignore_index=True)
cen.to_csv('data/county_centroids.csv',index=False)
print(len(cen))
