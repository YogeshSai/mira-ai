#!/usr/bin/env python3
"""Rebuild the Fund Check NAV snapshot from rajadilipkolli/historical-mf-nav-data.
Usage: python3 build_data.py  (downloads funds.db.zst if missing, writes funds_data.json.gz)"""
import sqlite3,json,gzip,os,re,urllib.request,datetime as dt
URL="https://github.com/rajadilipkolli/historical-mf-nav-data/releases/latest/download/funds.db.zst"
if not os.path.exists("funds.db"):
    import zstandard
    if not os.path.exists("funds.db.zst"): urllib.request.urlretrieve(URL,"funds.db.zst")
    with open("funds.db.zst","rb") as i,open("funds.db","wb") as o: zstandard.ZstdDecompressor().copy_stream(i,o)
c=sqlite3.connect("funds.db")
latest=c.execute("select max(date) from nav").fetchone()[0]
cut=(dt.date.fromisoformat(latest)-dt.timedelta(days=7)).isoformat()
old=(dt.date.fromisoformat(latest)-dt.timedelta(days=365*3+20)).isoformat()   # need >= 3 years of history
SKIP=re.compile(r"IDCW|Dividend|Payout|Reinvest|Bonus|Income Distribution|Unclaimed|\bIEF\b",re.I)   # Growth options only; no unclaimed-amount schemes
ETF=re.compile(r"ETF|Exchange Traded",re.I)   # exchange-traded funds are not Direct/Regular plans and carry unadjusted unit splits

def clean(days,vals):
    """The source stores NAV as digits without the decimal point, so a change in the number of decimals
    (e.g. 2 -> 4) shows up as a fake x10 / x100 jump. Re-scale every segment to the largest scale, then drop
    one-day bad prints that revert the next day. Returns cleaned (days, vals, #scale fixes, #spikes dropped)."""
    n=len(vals);c=[0]*n;off=0;fixes=0
    for i in range(1,n):
        r=vals[i]/vals[i-1]
        for k,e in ((1000,3),(100,2),(10,1)):
            if k*.8<=r<=k*1.2: off+=e;fixes+=1;break
            if 1/(k*1.2)<=r<=1/(k*.8): off-=e;fixes+=1;break
        c[i]=off
    mx=max(c);vals=[v*10**(mx-ci) for v,ci in zip(vals,c)]
    days=list(days);spikes=0;i=1
    while i<len(vals)-1:
        a,b,d=vals[i-1],vals[i],vals[i+1]
        if abs(b/a-1)>.15 and abs(d/a-1)<.05: del vals[i];del days[i];spikes+=1
        else: i+=1
    return days,vals,fixes,spikes
cut=(dt.date.fromisoformat(latest)-dt.timedelta(days=7)).isoformat()
sch={}
for code,name,amc,cat,plan,opt in c.execute("select scheme_code,scheme_name,amc,category,plan,option from schemes where plan like 'Direct%' or scheme_name like '%Direct%'"):
    if SKIP.search(opt or "") or SKIP.search(name): continue
    if "direct" not in name.lower() and not (plan or "").lower().startswith("direct"): continue
    if ETF.search(cat) and not re.search(r"fund of fund|FOF|FoF",name,re.I): continue
    cat=re.sub(r"^(Open|Close) Ended Schemes \(\s*|\s*\)$","",cat).strip()
    parts=cat.split(" - ")
    asset=re.sub(r" Scheme$","",parts[0].strip()) if len(parts)>1 else "Other"
    sch[code]=(name,re.sub(r" Mutual Fund$","",amc),parts[-1].strip(),asset)
c.execute("create temp table want(code integer primary key)")
c.executemany("insert into want values(?)",[(k,) for k in sch])
E0=dt.date(2000,1,1).toordinal();STAT=[0,0,0]
data={}
for code,d,n in c.execute("select n.scheme_code,n.date,n.nav from nav n join want w on w.code=n.scheme_code where n.nav>0"):
    data.setdefault(code,[]).append((d,n))
out=[]
for code,d in data.items():
    d.sort()
    if d[-1][0]<cut or len(d)<20: continue
    day=[dt.date.fromisoformat(x[0]).toordinal()-E0 for x in d]
    day,nv,nfix,nsp=clean(day,[float(x[1]) for x in d]);nv=[int(round(v)) for v in nv];STAT[0]+=nfix;STAT[1]+=nsp;STAT[2]+=(nfix>0)
    nm,amc,cat,asset=sch[code]
    out.append([code,nm,amc,cat,day[0],[day[i]-day[i-1] for i in range(1,len(day))],[nv[0]]+[nv[i]-nv[i-1] for i in range(1,len(nv))],asset])
meta={"asof":latest,"source":"rajadilipkolli/historical-mf-nav-data","funds":out}
with gzip.open("funds_data.json.gz","wb",9) as f: f.write(json.dumps(meta,separators=(",",":")).encode())
print("scale breaks fixed:",STAT[0],"in",STAT[2],"funds; bad one-day prints dropped:",STAT[1]);print(len(out),"funds,",os.path.getsize("funds_data.json.gz")//1024,"KB gz, as of",latest)

# Inject the snapshot into the page template -> fund-check.html (self-contained)
import base64
if os.path.exists("fund-check.template.html"):
    t=open("fund-check.template.html",encoding="utf8").read()
    b=base64.b64encode(open("funds_data.json.gz","rb").read()).decode()
    open("fund-check.html","w",encoding="utf8").write(t.replace("__BLOB__",b))
    print("wrote fund-check.html")
