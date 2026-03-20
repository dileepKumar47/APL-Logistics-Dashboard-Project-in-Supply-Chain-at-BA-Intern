import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="APL Logistics", page_icon="🚢", layout="wide")

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#f0f4f8;}
[data-testid="stSidebar"]{background:#0b1f3a;}
[data-testid="stSidebar"] *{color:#e8f0fe !important;}
[data-testid="stSidebar"] label{color:#e8f0fe !important;font-weight:600;}
[data-testid="stSidebar"] [data-baseweb="tag"]{background:#1e88e5 !important;color:#fff !important;}
[data-testid="stSidebar"] input[type="text"]{background:#1a3560 !important;color:#fff !important;border:1px solid #3d5a99 !important;border-radius:6px !important;}
/* fix records counter text */
[data-testid="stSidebar"] .stMarkdown p{color:#c8d8f0 !important;font-size:0.82rem;}
/* fix widget inner text (input/select boxes inside sidebar) */
[data-testid="stSidebar"] [data-baseweb="select"] *{color:#0b1f3a !important;}
[data-testid="stSidebar"] [data-baseweb="input"] input{color:#fff !important;}
/* discount tab filter labels — force visible on dark & light */
.stSlider label,.stSelectbox label,.stMultiSelect label{color:#0b1f3a !important;font-weight:600 !important;}
.kpi{background:#fff;border-radius:12px;padding:1rem 1.2rem;border-left:5px solid #1a73e8;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:.4rem;}
.kpi.g{border-left-color:#34a853;}.kpi.r{border-left-color:#e53935;}.kpi.o{border-left-color:#fb8c00;}.kpi.p{border-left-color:#8e24aa;}
.kpi .v{font-size:1.65rem;font-weight:700;color:#0b1f3a;line-height:1.2;}
.kpi .l{font-size:.7rem;font-weight:600;color:#5a6a85;text-transform:uppercase;letter-spacing:.8px;margin-top:3px;}
.sh{font-size:.92rem;font-weight:700;color:#0b1f3a;border-left:4px solid #1a73e8;padding-left:.5rem;margin:1rem 0 .5rem;}
button[data-baseweb="tab"] p{color:#0b1f3a !important;font-weight:600;}
button[data-baseweb="tab"][aria-selected="true"] p{color:#1a73e8 !important;}
</style>""", unsafe_allow_html=True)

LOGO_PATH = "Logo.png"

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("APL_Logistics.csv", encoding="latin1")
    df["Customer Name"] = df["Customer Fname"].str.strip() + " " + df["Customer Lname"].str.strip()
    df["Margin %"] = df["Order Profit Per Order"] / df["Sales"].replace(0, np.nan) * 100
    return df

try: df_raw = load()
except FileNotFoundError:
    st.error("❌ APL_Logistics.csv not found."); st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
try:
    st.sidebar.image(LOGO_PATH, use_container_width=True)
except Exception:
    st.sidebar.markdown("### 🚢 APL Logistics")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Filters")
mkt = st.sidebar.multiselect("Market",      sorted(df_raw["Market"].dropna().unique()),            default=sorted(df_raw["Market"].dropna().unique()))
seg = st.sidebar.multiselect("Segment",     sorted(df_raw["Customer Segment"].dropna().unique()),  default=sorted(df_raw["Customer Segment"].dropna().unique()))
shp = st.sidebar.multiselect("Ship Mode",   sorted(df_raw["Shipping Mode"].dropna().unique()),     default=sorted(df_raw["Shipping Mode"].dropna().unique()))
st.sidebar.markdown("---")
smin,smax = float(df_raw["Sales"].min()), float(df_raw["Sales"].max())
srng = st.sidebar.slider("Sales Range ($)", smin, smax, (smin, smax), step=10.0)

df = df_raw[df_raw["Market"].isin(mkt) & df_raw["Customer Segment"].isin(seg) &
            df_raw["Shipping Mode"].isin(shp) & df_raw["Sales"].between(*srng)].copy()

st.sidebar.markdown(f'<p style="color:#a0bde8;font-size:.82rem;margin-top:4px;">📊 Records: <b style="color:#e8f0fe;">{len(df):,}</b> / {len(df_raw):,}</p>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([1, 6])
with hc1:
    try:
        st.image(LOGO_PATH, width=110)
    except Exception:
        st.markdown("🚢")
with hc2:
    st.markdown(
        f'''<div style="padding-top:8px;">
          <div style="font-size:1.5rem;font-weight:700;color:#0b1f3a;">Supply Chain Analytics Dashboard</div>
          <div style="font-size:.85rem;color:#5a6a85;">{len(df):,} records &nbsp;·&nbsp; {df["Market"].nunique()} Markets &nbsp;·&nbsp; {df["Customer Segment"].nunique()} Segments</div>
        </div>''', unsafe_allow_html=True)

# ── Plot Helpers ──────────────────────────────────────────────────────────────
D = "#0b1f3a"; B = "#1a202c"; G = "#e2e8f0"
PLT  = dict(plot_bgcolor="#fff", paper_bgcolor="#fff", margin=dict(t=35,b=20,l=10,r=10),
            font=dict(color=B, family="Inter,sans-serif", size=12))
TF   = dict(color=D, size=11, family="Inter,sans-serif")
SEG  = {"Consumer":"#1a73e8","Corporate":"#34a853","Home Office":"#fb8c00"}
LH   = dict(orientation="h", y=1.12, font=dict(color=B,size=11), bgcolor="rgba(255,255,255,.85)", bordercolor=G, borderwidth=1)
LV   = dict(font=dict(color=B,size=11), bgcolor="rgba(255,255,255,.85)", bordercolor=G, borderwidth=1)
DEL  = {"Late delivery":"#e53935","Shipping on time":"#43a047","Advance shipping":"#1e88e5","Shipping canceled":"#fb8c00"}

def ax(title="", angle=0, rev=False):
    d = dict(title=title, title_font=dict(color=D,size=13), tickfont=dict(color=B,size=11),
             tickangle=angle, gridcolor=G, linecolor=G)
    if rev: d["autorange"]="reversed"
    return d

def cbar(t): return dict(title=dict(text=t,font=dict(color=D,size=12)),tickfont=dict(color=B,size=10))
def K(v,l,c=""): return f'<div class="kpi {c}"><div class="v">{v}</div><div class="l">{l}</div></div>'
def sh(t): st.markdown(f'<div class="sh">{t}</div>', unsafe_allow_html=True)
def bar_h(df_, x, y, **kw): return px.bar(df_, x=x, y=y, orientation="h", **kw)

# ── Tabs ──────────────────────────────────────────────────────────────────────
t1,t2,t3,t4 = st.tabs(["💰 Revenue & Profit","👥 Customer Value","📦 Product & Category","🎯 Discount Impact"])

# ══ TAB 1 ═════════════════════════════════════════════════════════════════════
with t1:
    cols = st.columns(5)
    for col,v,l,c in zip(cols,[f"${df['Sales'].sum()/1e6:.2f}M",f"${df['Order Profit Per Order'].sum()/1e6:.2f}M",
        f"{df['Margin %'].mean():.1f}%",f"${df['Sales'].mean():.0f}",f"{(df['Order Profit Per Order']<0).mean()*100:.1f}%"],
        ["Total Sales","Total Profit","Avg Margin","Avg Order","Loss Orders %"],["","g","p","o","r"]):
        col.markdown(K(v,l,c), unsafe_allow_html=True)
    st.markdown("")

    c1,c2 = st.columns(2)
    with c1:
        sh("Sales & Profit by Market")
        m = df.groupby("Market").agg(Sales=("Sales","sum"),Profit=("Order Profit Per Order","sum")).reset_index().sort_values("Sales",ascending=False)
        fig = go.Figure()
        for nm,col_,col2 in [("Sales","Sales","#1a73e8"),("Profit","Profit","#34a853")]:
            fig.add_bar(x=m["Market"],y=m[col_],name=nm,marker_color=col2,
                        text=m[col_].apply(lambda v:f"${v/1e3:.0f}K"),textposition="outside",textfont=TF)
        fig.update_layout(**PLT,barmode="group",xaxis=ax(""),yaxis=ax("Amount ($)"),legend=LH)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sh("Profit Margin % by Segment")
        s = df.groupby("Customer Segment").agg(S=("Sales","sum"),P=("Order Profit Per Order","sum")).reset_index()
        s["Mg"] = (s["P"]/s["S"]*100).round(1)
        fig2 = px.bar(s,x="Customer Segment",y="Mg",color="Customer Segment",color_discrete_map=SEG,
                      text=s["Mg"].apply(lambda v:f"{v:.1f}%"))
        fig2.update_traces(textposition="outside",textfont=TF)
        fig2.update_layout(**PLT,showlegend=False,xaxis=ax(""),yaxis=ax("Margin %"))
        st.plotly_chart(fig2,use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        sh("Department Sales & Profit")
        d = df.groupby("Department Name").agg(Sales=("Sales","sum"),Profit=("Order Profit Per Order","sum")).reset_index().sort_values("Sales")
        fig3 = go.Figure()
        for nm,col_,col2 in [("Sales","Sales","#1a73e8"),("Profit","Profit","#34a853")]:
            fig3.add_bar(y=d["Department Name"],x=d[col_],name=nm,marker_color=col2,orientation="h",
                         text=d[col_].apply(lambda v:f"${v/1e3:.0f}K"),textposition="outside",textfont=TF)
        fig3.update_layout(**PLT,barmode="group",height=460,xaxis=ax("Amount ($)"),yaxis=ax(""),legend=LH)
        st.plotly_chart(fig3,use_container_width=True)
    with c4:
        sh("Department Margin %")
        dm = df.groupby("Department Name").agg(S=("Sales","sum"),P=("Order Profit Per Order","sum")).reset_index()
        dm["Mg"] = (dm["P"]/dm["S"]*100).round(1)
        dm = dm.sort_values("Mg")
        fig4 = bar_h(dm,"Mg","Department Name",color="Mg",color_continuous_scale="RdYlGn",text=dm["Mg"].apply(lambda v:f"{v:.1f}%"))
        fig4.update_traces(textposition="outside",textfont=TF)
        fig4.update_layout(**PLT,height=460,coloraxis_showscale=False,xaxis=ax("Margin %"),yaxis=ax(""))
        st.plotly_chart(fig4,use_container_width=True)

# ══ TAB 2 ═════════════════════════════════════════════════════════════════════
with t2:
    cu = df.groupby(["Customer Id","Customer Name","Customer Segment"]).agg(
        Sales=("Sales","sum"),Profit=("Order Profit Per Order","sum"),Orders=("Sales","count")).reset_index()
    cu["Mg"] = (cu["Profit"]/cu["Sales"]*100).round(1)
    cols = st.columns(4)
    for col,v,l,c in zip(cols,[f"{cu['Customer Id'].nunique():,}",f"${cu.nlargest(10,'Sales')['Sales'].sum()/1e3:.0f}K",
        f"${cu['Profit'].mean():.0f}",f"{(cu['Profit']<0).mean()*100:.1f}%"],
        ["Total Customers","Top 10 Sales","Avg Profit/Customer","Unprofitable %"],["","g","p","r"]):
        col.markdown(K(v,l,c), unsafe_allow_html=True)
    st.markdown("")

    c1,c2 = st.columns(2)
    with c1:
        sh("Top 15 Customers by Profit")
        tc = cu.nlargest(15,"Profit")
        fig = bar_h(tc,"Profit","Customer Name",color="Customer Segment",color_discrete_map=SEG,text=tc["Profit"].apply(lambda v:f"${v:.0f}"))
        fig.update_traces(textposition="outside",textfont=TF)
        fig.update_layout(**PLT,yaxis=dict(**ax("",rev=True)),xaxis=ax("Profit ($)"),legend=LH)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sh("Bottom 15 Customers (Loss-Makers)")
        bc = cu.nsmallest(15,"Profit")
        fig2 = bar_h(bc,"Profit","Customer Name",color="Profit",color_continuous_scale="Reds_r",text=bc["Profit"].apply(lambda v:f"${v:.0f}"))
        fig2.update_traces(textposition="outside",textfont=TF)
        fig2.update_layout(**PLT,coloraxis_showscale=False,yaxis=dict(**ax("",rev=True)),xaxis=ax("Profit ($)"))
        st.plotly_chart(fig2,use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        sh("Segment Sales & Profit")
        sc = df.groupby("Customer Segment").agg(Sales=("Sales","sum"),Profit=("Order Profit Per Order","sum")).reset_index()
        fig3 = go.Figure()
        for nm,col_,col2 in [("Sales","Sales","#1a73e8"),("Profit","Profit","#34a853")]:
            fig3.add_bar(x=sc["Customer Segment"],y=sc[col_],name=nm,marker_color=col2,
                         text=sc[col_].apply(lambda v:f"${v/1e6:.2f}M" if nm=="Sales" else f"${v/1e3:.0f}K"),
                         textposition="outside",textfont=TF)
        fig3.update_layout(**PLT,barmode="group",xaxis=ax(""),yaxis=ax("Amount ($)"),legend=LH)
        st.plotly_chart(fig3,use_container_width=True)
    with c4:
        sh("Customer Profit vs Sales")
        sp = cu.sample(min(500,len(cu)),random_state=42)
        fig4 = px.scatter(sp,x="Sales",y="Profit",size="Orders",color="Customer Segment",
                          color_discrete_map=SEG,opacity=.7,size_max=30,hover_data=["Customer Name","Mg"])
        fig4.add_hline(y=0,line_dash="dash",line_color="#e53935",line_width=1.5,
                       annotation_text="Break-even",annotation_font=dict(color="#e53935",size=11))
        fig4.update_layout(**PLT,xaxis=ax("Sales ($)"),yaxis=ax("Profit ($)"),legend=LV)
        st.plotly_chart(fig4,use_container_width=True)

# ══ TAB 3 ═════════════════════════════════════════════════════════════════════
with t3:
    pr = df.groupby(["Product Name","Category Name","Department Name"]).agg(
        Sales=("Sales","sum"),Profit=("Order Profit Per Order","sum")).reset_index()
    pr["Mg"] = (pr["Profit"]/pr["Sales"]*100).round(1)
    ca = df.groupby("Category Name").agg(Sales=("Sales","sum"),Profit=("Order Profit Per Order","sum")).reset_index()
    ca["Mg"] = (ca["Profit"]/ca["Sales"]*100).round(1)
    cols = st.columns(4)
    best,worst = ca.loc[ca["Profit"].idxmax(),"Category Name"], ca.loc[ca["Profit"].idxmin(),"Category Name"]
    for col,v,l,c in zip(cols,[f"{pr['Product Name'].nunique():,}",f"{ca['Category Name'].nunique():,}",best[:18],worst[:18]],
        ["Total Products","Total Categories","Best Category","Worst Category"],["","o","g","r"]):
        col.markdown(K(v,l,c), unsafe_allow_html=True)
    st.markdown("")

    c1,c2 = st.columns(2)
    with c1:
        sh("Top 15 Products by Profit")
        tp = pr.nlargest(15,"Profit").copy(); tp["Short"]=tp["Product Name"].str[:30]
        fig = bar_h(tp,"Profit","Short",color="Mg",color_continuous_scale="Teal",text=tp["Profit"].apply(lambda v:f"${v/1e3:.1f}K"))
        fig.update_traces(textposition="outside",textfont=TF)
        fig.update_layout(**PLT,coloraxis_colorbar=cbar("Margin %"),yaxis=dict(**ax("",rev=True)),xaxis=ax("Profit ($)"))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sh("Bottom 15 Products by Margin")
        bp = pr.nsmallest(15,"Mg").copy(); bp["Short"]=bp["Product Name"].str[:30]
        fig2 = bar_h(bp,"Mg","Short",color="Mg",color_continuous_scale="Reds_r",text=bp["Mg"].apply(lambda v:f"{v:.1f}%"))
        fig2.update_traces(textposition="outside",textfont=TF)
        fig2.update_layout(**PLT,coloraxis_showscale=False,yaxis=dict(**ax("",rev=True)),xaxis=ax("Margin %"))
        st.plotly_chart(fig2,use_container_width=True)

    sh("Category × Department Profitability Heatmap")
    hp = df.groupby(["Department Name","Category Name"])["Order Profit Per Order"].sum().reset_index()
    hpv = hp.pivot(index="Department Name",columns="Category Name",values="Order Profit Per Order").fillna(0)
    fig3 = px.imshow(hpv,color_continuous_scale="RdYlGn",aspect="auto",text_auto=".2s",
                     labels=dict(x="Category",y="Department",color="Profit ($)"))
    fig3.update_traces(textfont=dict(color=D,size=9))
    fig3.update_layout(**PLT,height=400,xaxis=dict(tickfont=dict(color=B,size=9),tickangle=-35,title=""),
                       yaxis=dict(tickfont=dict(color=B,size=10),title=""),coloraxis_colorbar=cbar("Profit ($)"))
    st.plotly_chart(fig3,use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        sh("Category Sales vs Margin")
        cs = ca.sort_values("Sales",ascending=False).head(15)
        fig4 = go.Figure()
        fig4.add_bar(x=cs["Category Name"],y=cs["Sales"],name="Sales",marker_color="#1a73e8",yaxis="y1",
                     text=cs["Sales"].apply(lambda v:f"${v/1e3:.0f}K"),textposition="outside",textfont=TF)
        fig4.add_scatter(x=cs["Category Name"],y=cs["Mg"],name="Margin %",mode="lines+markers",
                         line=dict(color="#e53935",width=2.5),marker=dict(size=8,color="#e53935"),yaxis="y2")
        fig4.update_layout(**PLT,yaxis=dict(**ax("Sales ($)"),side="left"),
                           yaxis2=dict(**ax("Margin %"),side="right",overlaying="y",showgrid=False),
                           xaxis=ax("",angle=-35),legend=LH)
        st.plotly_chart(fig4,use_container_width=True)
    with c4:
        sh("Product Margin Distribution")
        fig5 = px.histogram(pr,x="Mg",nbins=40,color_discrete_sequence=["#1a73e8"])
        fig5.add_vline(x=0,line_dash="dash",line_color="#e53935",line_width=2,
                       annotation_text="Break-even",annotation_font=dict(color="#e53935",size=11))
        fig5.add_vline(x=pr["Mg"].mean(),line_dash="dot",line_color="#34a853",line_width=2,
                       annotation_text=f"Avg {pr['Mg'].mean():.1f}%",annotation_font=dict(color="#34a853",size=11))
        fig5.update_layout(**PLT,xaxis=ax("Profit Margin %"),yaxis=ax("# Products"),bargap=.05)
        st.plotly_chart(fig5,use_container_width=True)

# ══ TAB 4 ═════════════════════════════════════════════════════════════════════
with t4:
    avg_d = df["Order Item Discount Rate"].mean()*100
    no_d  = df[df["Order Item Discount Rate"]==0]["Order Profit Per Order"].mean()
    hi_d  = df[df["Order Item Discount Rate"]>0.2]["Order Profit Per Order"].mean()
    cols  = st.columns(4)
    for col,v,l,c in zip(cols,[f"{avg_d:.1f}%",f"${no_d:.0f}",f"${hi_d:.0f}",f"${df['Order Item Discount'].sum()/1e6:.2f}M"],
        ["Avg Discount Rate","Avg Profit (No Disc)","Avg Profit (>20%)","Total Discount Given"],["o","g","r","p"]):
        col.markdown(K(v,l,c), unsafe_allow_html=True)
    st.markdown("")

    c1,c2 = st.columns(2)
    with c1:
        sh("Avg Profit by Discount Band")
        db = df.copy()
        db["Band"] = pd.cut(db["Order Item Discount Rate"],bins=[-0.01,.05,.10,.15,.20,.25,.30,1.01],
                            labels=["0-5%","6-10%","11-15%","16-20%","21-25%","26-30%",">30%"])
        ba = db.groupby("Band",observed=True)["Order Profit Per Order"].mean().reset_index()
        ba.columns=["Band","Avg Profit"]
        fig = go.Figure()
        fig.add_bar(x=ba["Band"],y=ba["Avg Profit"],
                    marker=dict(color=ba["Avg Profit"],colorscale="RdYlGn",showscale=False),
                    text=ba["Avg Profit"].apply(lambda v:f"${v:.0f}"),textposition="outside",textfont=TF)
        fig.add_hline(y=0,line_dash="dash",line_color="#e53935",line_width=2,
                      annotation_text="Break-even",annotation_font=dict(color="#e53935",size=11))
        fig.update_layout(**PLT,xaxis=ax("Discount Band"),yaxis=ax("Avg Profit ($)"))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sh("Avg Discount by Market & Segment")
        dsm = df.groupby(["Market","Customer Segment"])["Order Item Discount Rate"].mean().mul(100).reset_index()
        dsm.columns=["Market","Segment","Avg Disc %"]
        fig2 = px.bar(dsm,x="Market",y="Avg Disc %",color="Segment",barmode="group",
                      color_discrete_map=SEG,text=dsm["Avg Disc %"].apply(lambda v:f"{v:.1f}%"))
        fig2.update_traces(textposition="outside",textfont=TF)
        fig2.update_layout(**PLT,xaxis=ax(""),yaxis=ax("Avg Discount %"),legend=LH)
        st.plotly_chart(fig2,use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        sh("Category Margin % by Discount Level")
        cd = df.groupby("Category Name").agg(Avg_Disc=("Order Item Discount Rate","mean"),
             Avg_Mg=("Margin %","mean"),Sales=("Sales","sum")).reset_index()
        cd["Level"] = pd.cut(cd["Avg_Disc"],bins=[-0.01,.05,.15,1.0],labels=["Low (0-5%)","Mid (6-15%)","High (>15%)"])
        cd = cd.sort_values("Avg_Mg")
        fig3 = bar_h(cd,"Avg_Mg","Category Name",color="Level",
                     color_discrete_map={"Low (0-5%)":"#34a853","Mid (6-15%)":"#fbbc04","High (>15%)":"#e53935"},
                     text=cd["Avg_Mg"].apply(lambda v:f"{v:.1f}%"))
        fig3.update_traces(textposition="outside",textfont=TF)
        fig3.update_layout(**PLT,height=550,xaxis=ax("Avg Margin %"),yaxis=ax(""),
                           legend=dict(title=dict(text="Disc Level",font=dict(color=D,size=12)),
                                       font=dict(color=B,size=11),bgcolor="rgba(255,255,255,.85)",bordercolor=G,borderwidth=1))
        st.plotly_chart(fig3,use_container_width=True)

    with c4:
        sh("🎯 What-If Discount Simulator")
        st.markdown('<p style="color:#0b1f3a;font-weight:600;font-size:.85rem;margin-bottom:4px;">Configure Scenario</p>', unsafe_allow_html=True)
        disc_pct  = st.slider("Discount Rate (%)", 0, 50, 10, step=1, key="disc")
        s_cat     = st.selectbox("Category", ["All"]+sorted(df["Category Name"].dropna().unique().tolist()), key="scat")
        s_seg     = st.selectbox("Segment",  ["All"]+sorted(df["Customer Segment"].dropna().unique().tolist()), key="sseg")
        s_mkt     = st.selectbox("Market",   ["All"]+sorted(df["Market"].dropna().unique().tolist()), key="smkt")
        sim = df.copy()
        if s_cat!="All": sim=sim[sim["Category Name"]==s_cat]
        if s_seg!="All": sim=sim[sim["Customer Segment"]==s_seg]
        if s_mkt!="All": sim=sim[sim["Market"]==s_mkt]
        ss=sim["Sales"].sum(); fr=disc_pct/100
        ns=ss*(1-fr); bp=sim["Order Profit Per Order"].sum()
        sp2=bp-(sim["Sales"]*fr).sum()
        bm=(bp/ss*100) if ss else 0; nm=(sp2/ns*100) if ns else 0; pd_=(sp2-bp)
        arrow="🟢 ▲" if pd_>=0 else "🔴 ▼"
        st.markdown(f"""
<style>
.metric-tbl{{width:100%;border-collapse:collapse;font-family:Inter,sans-serif;font-size:.88rem;}}
.metric-tbl th{{background:#0b1f3a;color:#7ec8e3;font-weight:700;padding:8px 12px;text-align:left;border-bottom:2px solid #1e88e5;}}
.metric-tbl td{{padding:7px 12px;border-bottom:1px solid #dce8f5;color:#4a90c4;font-weight:500;}}
.metric-tbl tr:last-child td{{border-bottom:none;}}
.metric-tbl tr:hover td{{background:#eaf3fb;}}
</style>
<table class="metric-tbl">
  <tr><th>Metric</th><th>Baseline</th><th>After {disc_pct}%</th></tr>
  <tr><td>Sales</td><td>${ss:,.0f}</td><td>${ns:,.0f}</td></tr>
  <tr><td>Profit</td><td>${bp:,.0f}</td><td>${sp2:,.0f}</td></tr>
  <tr><td>Margin %</td><td>{bm:.1f}%</td><td>{nm:.1f}%</td></tr>
  <tr><td>Δ Profit</td><td>—</td><td><b>{arrow} ${pd_:+,.0f}</b></td></tr>
</table>""", unsafe_allow_html=True)

    comp = pd.DataFrame({"Scenario":["Baseline",f"{disc_pct}% Disc"],"Sales":[ss,ns],"Profit":[bp,sp2]})
    fs = go.Figure()
    for nm_,col_,col2 in [("Sales","Sales","#1a73e8"),("Profit","Profit","#34a853" if sp2>=0 else "#e53935")]:
        fs.add_bar(x=comp["Scenario"],y=comp[col_],name=nm_,marker_color=col2,
                   text=comp[col_].apply(lambda v:f"${v/1e3:.1f}K"),textposition="outside",textfont=TF)
    fs.update_layout(**PLT,barmode="group",height=280,xaxis=ax(""),yaxis=ax("Amount ($)"),legend=LH)
    st.plotly_chart(fs,use_container_width=True)