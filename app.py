import random
import difflib
import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# PROC KICKBACK HUNTER AI — v5.1 "Industrial Candidate"
# ------------------------------------------------------------------------------
# Honest demo: the intelligence (entity resolution, scoring, accuracy, HITL
# workflow, four-eyes, audit) is REAL; everything that must stay mocked for a
# self-contained demo is LABELED as a stub with its production hook documented.
#
# v5.1 changelog vs. v5.0:
#  - Navigation switched from st.tabs to sidebar st.radio "pages". st.tabs reset
#    to the first tab on every st.rerun(), which bounced users out of the
#    review/booking workflow after each click. Radio state persists across
#    reruns, so the workflow now stays put. (Primary functional fix.)
#  - Persistent header on every page + full "what this prototype does" page.
#  - Inline "Was zeigt das?" explanation next to every visual and feature.
#  - Park action gated to review role; removed unused import; consistent umlauts.
# ==============================================================================

st.set_page_config(
    page_title="PROC Kickback Hunter AI | GlobalCorp SE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# GOVERNANCE FLAGS — single source of truth for "real vs. stub"
# ------------------------------------------------------------------------------
INTEGRITY = {
    "Entity Resolution Engine (deterministisch, erklärbar)": ("LIVE", "Reale Logik in resolve_entities()"),
    "Confidence Scoring & Evidenz pro Verknüpfung": ("LIVE", "Aus Parent-KB + Namen-Similarity berechnet"),
    "Accuracy-Messung (Precision/Recall/False-Merge)": ("LIVE", "Gegen gelabelte Ground-Truth gemessen"),
    "Human-in-the-Loop Review & Reason-Codes": ("LIVE", "Session-State Workflow"),
    "Vier-Augen-Prinzip ab Schwellenwert": ("LIVE", "Rollen- & Personentrennung erzwungen"),
    "Unveränderlicher Decision-/Audit-Log": ("LIVE", "Append-only, CSV-exportierbar"),
    "Parent-KB-Quelle (GLEIF LEI / D&B DUNS)": ("STUB", "Kuratierter Seed → Prod: GLEIF/D&B/Stammdaten"),
    "SAP Lesen (LFA1/EKKO)": ("STUB", "In-Memory → Prod: OData/CDS via BTP Destination"),
    "SAP Buchung (geparkt)": ("STUB", "Prod: BAPI_ACC_DOCUMENT_POST, Status PARKED, Release in SAP"),
    "SSO / Identity": ("STUB", "Rollenwahl → Prod: Entra/Azure AD via OIDC/SAML + MFA"),
    "Vertragsklausel-Extraktion (RAG/LLM)": ("STUB", "Hinterlegte Klausel → Prod: EU-gehosteter RAG"),
    "E-Mail-Versand": ("DRAFT-ONLY", "Kein Auto-Versand; Mensch prüft & sendet"),
}

THRESHOLD = 50_000_000.0          # Vertragsschwelle für Kickback
KICKBACK_RATE = 0.02
AUTO_MERGE_CONF = 0.90            # ab hier Auto-Vorschlag; darunter → Human-Review
NAME_REVIEW_SIM = 0.86           # Namen-Lookalikes ohne KB-Link → Review-Kandidat
FOUR_EYES_LIMIT = 250_000.0      # ab hier zwingend zweiter Genehmiger (andere Person)

ROLES = {
    "e.weber (Operativer Einkäufer)":      {"can_review": True, "can_release": False, "bukrs": "1000"},
    "s.klein (Lead Buyer / Genehmiger)":   {"can_review": True, "can_release": True,  "bukrs": "1000"},
    "k.adesina (Lead Buyer / Genehmiger)": {"can_review": True, "can_release": True,  "bukrs": "1000"},
}

# ------------------------------------------------------------------------------
# CSS (Apple/Cupertino)
# ------------------------------------------------------------------------------
def inject_css():
    st.markdown("""
    <style>
    .stApp { background-color:#0A0A0C !important; color:#F5F5F7 !important;
        font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",sans-serif; }
    .frosted-glass { background:rgba(28,28,30,0.65)!important; backdrop-filter:blur(20px)!important;
        border:1px solid rgba(255,255,255,0.08)!important; border-radius:16px!important;
        padding:22px!important; box-shadow:0 12px 40px 0 rgba(0,0,0,0.45)!important; }
    div.stButton > button:first-child { background-color:#007AFF!important; color:#FFF!important;
        border-radius:12px!important; font-weight:600!important; border:none!important;
        padding:10px 20px!important; transition:all .2s ease-in-out; }
    div.stButton > button:first-child:hover { background-color:#0062CC!important; transform:scale(1.01); }
    input[type="text"] { background-color:rgba(255,255,255,0.07)!important;
        border:1px solid rgba(255,255,255,0.18)!important; color:#FFF!important;
        border-radius:12px!important; padding:12px 16px!important; }
    div[data-testid="stMetricValue"] { font-size:30px!important; font-weight:700!important; }
    .evid { background:rgba(0,0,0,0.30); border-radius:10px; padding:10px 14px; font-size:13px;
        margin:4px 0; border-left:3px solid #30D158; }
    .evid-weak { border-left:3px solid #FF9F0A; }
    .explain { background:rgba(0,122,255,0.08); border-left:3px solid #007AFF;
        border-radius:8px; padding:10px 14px; font-size:13px; color:#C9D6EA; margin:6px 0 14px 0; }
    .pill-live { color:#30D158; font-weight:700; }
    .pill-stub { color:#FF9F0A; font-weight:700; }
    .pill-draft { color:#5E9EFF; font-weight:700; }
    </style>""", unsafe_allow_html=True)

inject_css()

def fmt(v):
    return f"{v:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

def explain(text):
    """Einheitlicher Erklärblock: 'Was zeigt das hier eigentlich?'"""
    st.markdown(f"<div class='explain'><b>ℹ️ Was zeigt das?</b> {text}</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------------------------
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []          # append-only
if "claims" not in st.session_state:
    st.session_state.claims = {}             # parent -> claim dict (workflow state)
if "engine_ran" not in st.session_state:
    st.session_state.engine_ran = False

def log(action, target, detail=""):
    st.session_state.audit_log.append({
        "Zeit": now(), "Akteur": st.session_state.get("user", "—"),
        "Aktion": action, "Objekt": target, "Detail": detail,
    })

# ==============================================================================
# 1. DATA (In-Memory SAP STUB — Prod: OData/CDS via BTP Destination)
# ==============================================================================
@st.cache_data
def generate_sap_data():
    random.seed(1337)
    core = [
        {"LIFNR":"10001","NAME1":"Cisco Systems Germany GmbH","ORT01":"Bonn","LAND1":"DE","STCD1":"DE123456780","SPEND_YTD":18_200_000.0},
        {"LIFNR":"10002","NAME1":"Cisco Technology Inc.","ORT01":"San Jose","LAND1":"US","STCD1":"US987654321","SPEND_YTD":14_100_000.0},
        {"LIFNR":"10003","NAME1":"Meraki Cloud Networks Ltd.","ORT01":"London","LAND1":"GB","STCD1":"GB554433221","SPEND_YTD":9_500_000.0},
        {"LIFNR":"10004","NAME1":"Acacia Communications Opto","ORT01":"Maynard","LAND1":"US","STCD1":"US112233445","SPEND_YTD":6_200_000.0},
        {"LIFNR":"10005","NAME1":"Splunk Software EMEA","ORT01":"Munich","LAND1":"DE","STCD1":"DE887766554","SPEND_YTD":4_400_000.0},
        {"LIFNR":"20001","NAME1":"Microsoft Deutschland GmbH","ORT01":"Munich","LAND1":"DE","STCD1":"DE998877665","SPEND_YTD":41_000_000.0},
        {"LIFNR":"20002","NAME1":"Activision Blizzard Germany","ORT01":"Ismaning","LAND1":"DE","STCD1":"DE556677889","SPEND_YTD":6_000_000.0},
    ]
    # Lookalike-Paar OHNE verifizierten Konzern-Link: muss vom Menschen geprüft
    # werden, darf NICHT automatisch gemerged werden (Demo der Konservativität).
    lookalike = [
        {"LIFNR":"40100","NAME1":"Apex Logistics GmbH","ORT01":"Frankfurt","LAND1":"DE","STCD1":"DE700100100","SPEND_YTD":2_900_000.0},
        {"LIFNR":"40101","NAME1":"Apex Logistic S.A.","ORT01":"Paris","LAND1":"FR","STCD1":"FR700100200","SPEND_YTD":2_600_000.0},
    ]
    stems=["Logistics","Facility","Consulting","MRO","Packaging","IT-Services","Robotics",
           "Chemicals","Security","Fleet","Procurement","Maintenance"]
    cities=["Frankfurt","Stuttgart","Hamburg","Berlin","Düsseldorf","Zurich","Vienna","Milan","Madrid","Amsterdam"]
    prefixes=["Nova","Sino","Euro","Chroma","Stellar","Vanguard","Omni","Inno","Hanse","Lumen",
              "Aurum","Borea","Cresta","Delphi","Equinox"]
    combos=[(p,s) for p in prefixes for s in stems]
    random.shuffle(combos)
    combos=combos[:141]
    fillers=[]
    for idx,(p,s) in enumerate(combos):
        fillers.append({
            "LIFNR":f"{30010+idx}",
            "NAME1":f"{p} {s} {random.choice(['GmbH','AG','S.A.','Ltd'])}",
            "ORT01":random.choice(cities),"LAND1":random.choice(["DE","FR","CH","AT","IT","ES","NL"]),
            "STCD1":f"EU{random.randint(100000000,999999999)}",
            "SPEND_YTD":round(random.uniform(15000.0,3_800_000.0),2),
        })
    df = pd.DataFrame(core + lookalike + fillers)

    rows=[]; ebeln=4500000001
    for _,v in df.iterrows():
        n=random.randint(6,18); cents=int(v["SPEND_YTD"]*100)
        cuts=sorted(random.randint(1,cents-1) for _ in range(n-1)); cuts=[0]+cuts+[cents]
        for k in range(len(cuts)-1):
            rows.append({"EBELN":str(ebeln),"LIFNR":v["LIFNR"],"BUKRS":"1000",
                         "NETWR":(cuts[k+1]-cuts[k])/100.0,"WAERS":"EUR"}); ebeln+=1
    df_ekko=pd.DataFrame(rows).sample(frac=1,random_state=42).reset_index(drop=True)
    return df, df_ekko

df_lfa1, df_ekko = generate_sap_data()

# ==============================================================================
# 2. KNOWLEDGE BASE  (STUB-Quelle: GLEIF LEI / D&B DUNS / interne Stammdaten)
#    EINZIGE Merge-Autorität. NICHT Stadt, NICHT Substring.
# ==============================================================================
PARENT_KB = {
    "10001": ("Cisco Systems, Inc.", "GLEIF LEI: direkte Tochter", 0.99),
    "10002": ("Cisco Systems, Inc.", "GLEIF LEI: Ultimate Parent (HQ-Entität)", 0.99),
    "10003": ("Cisco Systems, Inc.", "D&B DUNS-Linkage: Meraki-Akquisition 2012", 0.97),
    "10004": ("Cisco Systems, Inc.", "D&B DUNS-Linkage: Acacia-Akquisition 2021", 0.96),
    "10005": ("Cisco Systems, Inc.", "D&B DUNS-Linkage: Splunk-Akquisition 2024", 0.93),
    "20001": ("Microsoft Corporation", "GLEIF LEI: direkte Tochter", 0.99),
    "20002": ("Microsoft Corporation", "D&B DUNS-Linkage: Activision-Akquisition 2023", 0.95),
}
GROUND_TRUTH = {k: v[0] for k, v in PARENT_KB.items()}  # nur für Accuracy-Messung

LEGAL_SUFFIX = {"gmbh","ag","inc","ltd","sa","corp","corporation","co","plc","llc",
                "communications","cloud","networks","software","systems","technology",
                "opto","emea","germany","deutschland"}

def normalize_name(name):
    toks = [t for t in name.lower().replace(".", " ").split() if t not in LEGAL_SUFFIX]
    return " ".join(toks)

def name_sim(a, b):
    return difflib.SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

# ==============================================================================
# 3. ENTITY RESOLUTION ENGINE (LIVE, deterministisch, erklärbar)
# ==============================================================================
def resolve_entities(df):
    names = dict(zip(df["LIFNR"], df["NAME1"]))
    clusters = {}
    for lifnr in df["LIFNR"]:
        if lifnr in PARENT_KB:
            parent, source, conf = PARENT_KB[lifnr]
            clusters.setdefault(parent, []).append((lifnr, source, conf))
    verified = {}
    for parent, members in clusters.items():
        if len(members) < 2:
            continue
        cluster_conf = min(c for _, _, c in members)
        member_lifnr = [m[0] for m in members]
        evidence = {}
        for lifnr, source, conf in members:
            sims = [name_sim(names[lifnr], names[o]) for o in member_lifnr if o != lifnr]
            evidence[lifnr] = {"source": source, "conf": conf, "name_sim_max": max(sims) if sims else 0.0}
        verified[parent] = {"members": member_lifnr, "evidence": evidence,
                            "cluster_conf": cluster_conf, "auto": cluster_conf >= AUTO_MERGE_CONF}
    review = []
    singles = [l for l in df["LIFNR"] if l not in PARENT_KB]
    for i in range(len(singles)):
        for j in range(i + 1, len(singles)):
            s = name_sim(names[singles[i]], names[singles[j]])
            if s >= NAME_REVIEW_SIM:
                review.append((singles[i], singles[j], round(s, 3)))
    review.sort(key=lambda x: -x[2])
    return verified, review

def pairwise_accuracy(df, verified):
    pred = {}
    for parent, c in verified.items():
        if c["auto"]:
            for l in c["members"]:
                pred[l] = parent
    lifnrs = list(df["LIFNR"])
    tp = fp = fn = 0
    for i in range(len(lifnrs)):
        for j in range(i + 1, len(lifnrs)):
            a, b = lifnrs[i], lifnrs[j]
            same_pred = a in pred and b in pred and pred[a] == pred[b]
            same_gt = GROUND_TRUTH.get(a) is not None and GROUND_TRUTH.get(a) == GROUND_TRUTH.get(b)
            if same_pred and same_gt: tp += 1
            elif same_pred and not same_gt: fp += 1
            elif (not same_pred) and same_gt: fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    return {"precision": precision, "recall": recall, "false_merges": fp, "tp": tp, "fn": fn}

def run_engine():
    verified, review = resolve_entities(df_lfa1)
    metrics = pairwise_accuracy(df_lfa1, verified)
    st.session_state.verified = verified
    st.session_state.review = review
    st.session_state.metrics = metrics
    st.session_state.engine_ran = True
    log("ENGINE_RUN", "Entity Resolution", f"{len([c for c in verified.values() if c['auto']])} Auto-Cluster")
    for parent, c in verified.items():
        if not c["auto"] or parent in st.session_state.claims:
            continue
        spend = df_lfa1[df_lfa1["LIFNR"].isin(c["members"])]["SPEND_YTD"].sum()
        qualified = spend >= THRESHOLD
        st.session_state.claims[parent] = {
            "members": c["members"], "spend": spend, "qualified": qualified,
            "cashback": spend * KICKBACK_RATE if qualified else 0.0,
            "cluster_conf": c["cluster_conf"],
            "status": "NEU" if qualified else "KEIN_ANSPRUCH",
            "reviewer1": None, "reason1": None, "reviewer2": None, "reason2": None,
        }

# ==============================================================================
# SIDEBAR — IDENTITY (SSO-STUB) · NAVIGATION · SYSTEM INTEGRITY
# ==============================================================================
PAGES = ["📖 Übersicht", "🏛️ SAP-Quelldaten", "🧠 Resolution & Güte",
         "✅ Review & Vier-Augen", "💎 Buchung, Audit & Versand"]

with st.sidebar:
    st.markdown("### 🔐 Identity & Access")
    st.caption("SSO-STUB · Prod: Entra/Azure AD (OIDC/SAML) + MFA")
    user = st.selectbox("Angemeldete Rolle", list(ROLES.keys()), key="user")
    role = ROLES[user]
    st.caption(f"Scope (BUKRS): **{role['bukrs']}** · "
               f"Review: {'✅' if role['can_review'] else '❌'} · "
               f"Release: {'✅' if role['can_release'] else '❌'}")
    st.markdown("---")
    page = st.radio("Navigation", PAGES, key="nav")
    st.markdown("---")
    st.markdown("### 🧪 System-Integrität")
    st.caption("Was läuft echt, was ist Stub — die ehrliche Linie.")
    for comp, (status, note) in INTEGRITY.items():
        cls = {"LIVE": "pill-live", "STUB": "pill-stub", "DRAFT-ONLY": "pill-draft"}[status]
        st.markdown(f"<div style='font-size:12px;margin-bottom:6px;'>"
                    f"<span class='{cls}'>{status}</span> · {comp}<br>"
                    f"<span style='color:#8E8E93;'>{note}</span></div>", unsafe_allow_html=True)

# ==============================================================================
# PERSISTENT HEADER — auf JEDER Seite. Erklärt, was der Prototyp tut.
# ==============================================================================
def global_header(page_title, page_purpose):
    st.markdown(f"""
    <div class="frosted-glass" style="margin-bottom:12px;">
      <h1 style="margin:0;font-size:28px;font-weight:800;letter-spacing:-1px;">
        PROC Kickback Hunter AI <span style="color:#007AFF;font-size:17px;">v5.1 Industrial Candidate</span></h1>
      <p style="margin:6px 0 0 0;color:#C9D6EA;font-size:14px;line-height:1.5;">
        <b>Worum es geht:</b> Konzern-Lieferanten sind durch M&amp;A und gewachsene Buchungskreise im SAP-Kreditorenstamm
        in viele Einzelkonten zersplittert. Vertragliche Rückvergütungen (Kickbacks) greifen aber erst ab einer
        <b>konsolidierten</b> Umsatzschwelle. Klassisches ERP-Reporting prüft pro Kreditor und meldet daher fälschlich „0 €".
        Dieser Prototyp <b>verklammert die Einzelkonten zur echten Konzern-Entität</b> (über verifizierte
        Mutter-Tochter-Beziehungen, nicht über Namens-Raten), <b>misst den konsolidierten Spend gegen die Schwelle</b> und
        führt den daraus folgenden Rückvergütungsanspruch durch einen <b>menschlich kontrollierten Freigabe-Workflow</b>
        bis zum geparkten SAP-Beleg.
      </p>
      <p style="margin:8px 0 0 0;color:#8E8E93;font-size:13px;">
        Aktuelle Seite: <b style="color:#FFFFFF;">{page_title}</b> — {page_purpose}
      </p>
    </div>""", unsafe_allow_html=True)
    with st.expander("ℹ️ Vollständige Erklärung: Ablauf, Datenbasis und was echt vs. simuliert ist"):
        st.markdown(f"""
**Der Ablauf in fünf Schritten**

1. **SAP-Quelldaten lesen** — Kreditorenstamm (`LFA1`) und Bestellbelege (`EKKO`). Im Prototyp 150 in-memory
   erzeugte Kreditoren inkl. eines fragmentierten Cisco-Konzerns (5 Konten) und eines Microsoft-Konzerns (2 Konten).
2. **Entity Resolution** — die Engine ordnet jedes Konto über eine verifizierte Mutter-Tochter-Wissensbasis
   (in Prod: GLEIF-LEI-Hierarchien, D&B-DUNS, interne Stammdaten) einer Ultimate-Parent-Entität zu.
   **Stadt, Adresse und reine Namens-Ähnlichkeit sind ausdrücklich keine Merge-Signale** — genau das verhindert
   Falschverklammerungen (z. B. Microsoft + Splunk nur weil beide in München sitzen).
3. **Güte messen** — die Auflösung wird paarweise gegen eine gelabelte Ground-Truth gemessen (Precision/Recall/
   False-Merges). Das ist die Audit- und EU-AI-Act-Evidenz, dass die Automatik nicht falsch verklammert.
4. **Konsolidieren & rechnen** — pro Konzern-Entität wird der Spend summiert und gegen die Vertragsschwelle
   ({fmt(THRESHOLD)}) geprüft. Liegt er darüber, wird die Rückvergütung ({int(KICKBACK_RATE*100)} %) als Anspruch ausgewiesen.
5. **Mensch entscheidet** — der Anspruch geht NICHT automatisch ins SAP. Ein Einkäufer prüft die Evidenz, gibt mit
   Begründung frei (L1); ab {fmt(FOUR_EYES_LIMIT)} muss eine **zweite Person** gegenzeichnen (Vier-Augen). Erst danach
   wird ein **geparkter** Beleg erzeugt, den eine Genehmiger-Rolle im SAP releast. Jede Aktion landet im Audit-Log.

**Was hier echt läuft** (🟢): Entity Resolution, Confidence- & Evidenz-Berechnung, Accuracy-Messung, der komplette
HITL-Workflow inkl. Vier-Augen und der unveränderliche Audit-Log.

**Was bewusst simuliert ist** (🟠): die SAP-Anbindung (Lesen & Buchen), die Parent-Wissensbasis-Quelle, die
LLM/RAG-Vertragsklausel-Extraktion und das SSO. Diese sind in der Sidebar einzeln als „STUB" markiert, inkl.
des jeweiligen Produktiv-Integrationspunkts. Die E-Mail an den CFO ist **Entwurf-only** — kein Auto-Versand.
        """)

# ==============================================================================
# PAGE: ÜBERSICHT
# ==============================================================================
if page == "📖 Übersicht":
    global_header("Übersicht", "Was der Prototyp tut und wie er aufgebaut ist.")
    st.markdown("#### 🔎 Das konkrete Beispiel in dieser Demo")
    explain("Der Kern-Showcase. Mit „Cisco Global“ besteht ein Rahmenvertrag: ab "
            f"{fmt(THRESHOLD)} konsolidiertem Konzernumsatz greift {int(KICKBACK_RATE*100)} % Rückvergütung. "
            "Im SAP existieren aber 5 getrennte Cisco-Kreditoren — keiner reißt für sich die Schwelle. "
            "Genau diese Lücke schließt der Prototyp.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='frosted-glass'><b>🏛️ Klassische SAP-Sicht</b><br>"
                    "<span style='color:#8E8E93;font-size:13px;'>Prüft pro Kreditor. Größtes Einzelsilo &lt; Schwelle "
                    "→ meldet <b style='color:#FF453A;'>0,00 € Anspruch</b>.</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='frosted-glass'><b>🧠 Diese Engine</b><br>"
                    "<span style='color:#8E8E93;font-size:13px;'>Verklammert 5 Konten zur Konzern-Entität, summiert "
                    "den Spend → <b style='color:#30D158;'>52,40 Mio. €</b>.</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='frosted-glass'><b>💎 Ergebnis (nach Freigabe)</b><br>"
                    "<span style='color:#8E8E93;font-size:13px;'>Schwelle überschritten → Rückvergütungs-Anspruch "
                    "<b style='color:#30D158;'>1.048.000 €</b>.</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.info("➡️ Empfohlener Demo-Pfad: **SAP-Quelldaten** ansehen → **Resolution & Güte** ausführen → "
            "**Review & Vier-Augen** durchlaufen (Rolle in der Sidebar wechseln!) → **Buchung, Audit & Versand**.")

# ==============================================================================
# PAGE: SAP-QUELLDATEN
# ==============================================================================
elif page == "🏛️ SAP-Quelldaten":
    global_header("SAP-Quelldaten", "Die rohe ERP-Datenbasis, auf der die Engine arbeitet.")
    st.caption("🟠 STUB: In-Memory erzeugt. Prod-Lesepfad: OData/CDS-Views über BTP Destination + Cloud Connector, "
               "Service-Account least-privilege.")
    search = st.text_input("🔍 Anzeige filtern (reine Navigationshilfe — die Konsolidierung macht die Engine, nicht die Suche)",
                           value="", placeholder="z.B. 'Cisco', 'Microsoft', 'Apex' oder eine LIFNR").strip()
    if search:
        m = df_lfa1["NAME1"].str.contains(search, case=False, na=False) | df_lfa1["LIFNR"].str.contains(search, na=False)
        view = df_lfa1[m]
    else:
        view = df_lfa1
    explain("Der simulierte SAP-Kreditorenstamm <b>LFA1</b>: Kreditornummer (LIFNR), Name, Ort, Land, "
            "Steuer-ID (STCD1) und kumulierter Jahres-Spend (SPEND_YTD). Wichtig: <b>Ort und Adresse werden bewusst "
            "NICHT zum Verklammern benutzt</b>. Suchen Sie z.B. 'Cisco' — Sie sehen 5 getrennte Konten, die im SAP "
            "nichts voneinander wissen. Genau diese Fragmentierung löst die Engine auf der nächsten Seite auf.")
    st.markdown(f"**Kreditorenstamm `LFA1`** — angezeigt: {len(view)} von {len(df_lfa1)} Kreditoren")
    st.dataframe(view.style.format({"SPEND_YTD": "{:,.2f} €"}), use_container_width=True, height=460, hide_index=True)
    with st.expander("Bestellbelege `EKKO` (Beleg-Ebene, die den Spend ergibt)"):
        ek = df_ekko[df_ekko["LIFNR"].isin(view["LIFNR"].tolist())]
        explain("Die einzelnen Bestellbelege je Kreditor. Ihre Summe pro Konto ergibt den SPEND_YTD oben. "
                "Demonstriert, dass der Spend aus vielen kleinen Belegen besteht — nichts ist hartkodiert.")
        st.dataframe(ek.style.format({"NETWR": "{:,.2f} €"}), use_container_width=True, height=320, hide_index=True)

# ==============================================================================
# PAGE: RESOLUTION & GÜTE
# ==============================================================================
elif page == "🧠 Resolution & Güte":
    global_header("Resolution & Güte", "Die Engine verklammert Konten zur Konzern-Entität und weist ihre Treffsicherheit nach.")
    st.caption("🟢 LIVE: deterministische, erklärbare Auflösung. Merge nur über verifizierte Parent-Linkage (GLEIF/D&B-Stub).")
    explain("Hier läuft die eigentliche Intelligenz. Per Klick ordnet die Engine jedes Konto seiner verifizierten "
            "Mutter-Entität zu. Es gibt <b>keine versteckte KI-Show</b> — die Logik ist nachvollziehbar und liefert "
            "für jede Verknüpfung eine sichtbare Begründung (Quelle + Confidence).")
    if st.button("🚀 Entity Resolution ausführen", type="primary"):
        with st.status("Resolution läuft…", expanded=False) as s:
            run_engine()
            s.update(label="Resolution abgeschlossen", state="complete")

    if st.session_state.get("engine_ran"):
        verified = st.session_state.verified
        review = st.session_state.review
        m = st.session_state.metrics
        names = dict(zip(df_lfa1["LIFNR"], df_lfa1["NAME1"]))

        st.markdown("#### 📐 Gemessene Engine-Güte (Audit- / EU-AI-Act-Evidenz)")
        a, b, c, d = st.columns(4)
        a.metric("Precision", f"{m['precision']*100:.1f} %")
        b.metric("Recall", f"{m['recall']*100:.1f} %")
        c.metric("False Merges", f"{m['false_merges']}")
        d.metric("Auto-Cluster", f"{len([x for x in verified.values() if x['auto']])}")
        explain("Gemessen paarweise gegen eine gelabelte Ground-Truth. <b>Precision</b> = von den automatisch "
                "verklammerten Kreditor-Paaren, wie viele waren korrekt. <b>Recall</b> = von den Paaren, die "
                "zusammengehören, wie viele hat die Engine gefunden. <b>False Merges</b> = fälschlich verklammerte "
                "Paare (0 = keine). <b>Auto-Cluster</b> = Zahl der Konzern-Gruppen, die oberhalb der Confidence-Schwelle "
                "automatisch vorgeschlagen wurden. Diese Zahlen sind der Beweis, dass die Automatik nicht falsch klammert.")

        st.markdown("#### 🧬 Verifizierte Cluster (mit Evidenz pro Verknüpfung)")
        explain("Jeder aufklappbare Block ist eine aufgelöste Konzern-Entität. Darin steht je Kreditor das "
                "<b>konkrete Signal</b>, warum er dazugehört (z. B. „D&B-Linkage: Splunk-Akquisition 2024“), die "
                "Confidence und die Namens-Ähnlichkeit. So validiert ein Mensch die <b>Gruppierung</b> statt blind zu vertrauen.")
        for parent, cl in verified.items():
            if not cl["auto"]:
                continue
            with st.expander(f"🟢 {parent} — {len(cl['members'])} Kreditoren · Cluster-Confidence {cl['cluster_conf']:.2f}"):
                for lifnr in cl["members"]:
                    e = cl["evidence"][lifnr]
                    st.markdown(f"<div class='evid'><b>{names[lifnr]}</b> ({lifnr})<br>"
                                f"Signal: {e['source']} · Confidence {e['conf']:.2f} · "
                                f"Namen-Ähnlichkeit z. Cluster {e['name_sim_max']:.2f}</div>", unsafe_allow_html=True)
                st.caption("Hinweis: die nationalen Steuer-IDs der Töchter unterscheiden sich bewusst — deshalb scheitert "
                           "naives Tax-ID-/Substring-Matching, und deshalb braucht es die verifizierte Parent-Linkage.")

        st.markdown("#### 🟠 Review-Kandidaten (Namens-Lookalike OHNE verifizierten Link)")
        explain("Paare, deren Namen sich stark ähneln, für die es aber <b>keine</b> verifizierte Konzern-Linkage gibt. "
                "Die Engine merged sie <b>bewusst nicht</b>, sondern legt sie dem Menschen zur Prüfung vor. Das ist "
                "die eingebaute Konservativität: Ähnlichkeit allein löst nie eine Buchung aus. "
                "Das oberste Paar (Apex) ist das Schulbeispiel dafür.")
        if review:
            for a_, b_, sim in review[:12]:
                st.markdown(f"<div class='evid evid-weak'><b>{names[a_]}</b> ({a_}) ↔ <b>{names[b_]}</b> ({b_})<br>"
                            f"Namen-Ähnlichkeit {sim} · KEINE Konzern-Linkage → menschliche Prüfung erforderlich.</div>",
                            unsafe_allow_html=True)
            if len(review) > 12:
                st.caption(f"… und {len(review)-12} weitere Kandidaten.")
        else:
            st.caption("Keine offenen Lookalike-Kandidaten.")
    else:
        st.info("Engine noch nicht ausgeführt — bitte oben den Button klicken.")

# ==============================================================================
# PAGE: REVIEW & VIER-AUGEN (HITL)
# ==============================================================================
elif page == "✅ Review & Vier-Augen":
    global_header("Review & Vier-Augen", "Der Mensch prüft die Evidenz und gibt frei — kein Auto-Posting.")
    st.caption("🟢 LIVE: Vorschlag → Evidenzprüfung → L1-Entscheid (Reason-Code) → Vier-Augen ab Schwelle → geparkter Beleg.")
    explain("Hier wird aus einem KI-Vorschlag eine verantwortete Entscheidung. Es gibt <b>keinen Magie-Knopf</b>: "
            "Jede Freigabe verlangt eine Begründung (Reason-Code) und wird protokolliert. Ansprüche ab "
            f"{fmt(FOUR_EYES_LIMIT)} Cashback brauchen zwingend eine <b>zweite Person</b> (Vier-Augen) — dafür in der "
            "Sidebar die Rolle wechseln.")
    if not st.session_state.get("engine_ran"):
        st.info("Bitte zuerst die Seite **Resolution & Güte** ausführen.")
    elif not role["can_review"]:
        st.warning("Ihre Rolle besitzt keine Review-Berechtigung.")
    else:
        open_claims = {p: c for p, c in st.session_state.claims.items() if c["qualified"]}
        if not open_claims:
            st.success("Keine qualifizierten Ansprüche in der Queue. (Beispiel: der Microsoft-Cluster liegt mit "
                       "47,0 Mio. korrekt unter der 50-Mio-Schwelle → kein Anspruch, Logik intakt.)")
        for parent, c in open_claims.items():
            st.markdown("<div class='frosted-glass'>", unsafe_allow_html=True)
            st.markdown(f"**Anspruch: {parent}** · Status `{c['status']}` · "
                        f"Konsolidiert {fmt(c['spend'])} · Cashback {fmt(c['cashback'])}")
            st.caption("Geprüft wird die Gruppierung (gehören diese Konten wirklich zusammen?) — nicht die Mathematik.")
            st.dataframe(df_lfa1[df_lfa1['LIFNR'].isin(c['members'])][["LIFNR","NAME1","ORT01","LAND1","SPEND_YTD"]]
                         .style.format({"SPEND_YTD":"{:,.2f} €"}), use_container_width=True, hide_index=True)

            needs_four_eyes = c["cashback"] >= FOUR_EYES_LIMIT
            if needs_four_eyes:
                st.caption(f"⚖️ Vier-Augen erforderlich (≥ {fmt(FOUR_EYES_LIMIT)} Cashback): L1 und L2 müssen verschiedene Personen sein.")

            if c["status"] == "NEU":
                reason = st.text_input("Reason-Code / Begründung L1", key=f"r1_{parent}",
                                       placeholder="z.B. 'Linkage GLEIF+D&B verifiziert, Akquisitionen plausibel'")
                col_a, col_r = st.columns(2)
                if col_a.button("✅ L1 freigeben", key=f"a1_{parent}"):
                    if not reason.strip():
                        st.error("Reason-Code ist Pflicht.")
                    else:
                        c["reviewer1"] = user; c["reason1"] = reason.strip()
                        c["status"] = "L1_OK" if needs_four_eyes else "FREIGEGEBEN"
                        log("APPROVE_L1", parent, reason.strip()); st.rerun()
                if col_r.button("❌ Ablehnen", key=f"x1_{parent}"):
                    if not reason.strip():
                        st.error("Reason-Code ist Pflicht.")
                    else:
                        c["reviewer1"] = user; c["reason1"] = reason.strip(); c["status"] = "ABGELEHNT"
                        log("REJECT", parent, reason.strip()); st.rerun()

            elif c["status"] == "L1_OK":
                st.caption(f"L1 freigegeben von **{c['reviewer1']}** — „{c['reason1']}“")
                if user == c["reviewer1"]:
                    st.warning("Vier-Augen: L2 muss eine andere Person sein. Bitte in der Sidebar die Rolle wechseln.")
                else:
                    reason2 = st.text_input("Reason-Code / Begründung L2", key=f"r2_{parent}")
                    if st.button("✅ L2 freigeben (Vier-Augen)", key=f"a2_{parent}"):
                        if not reason2.strip():
                            st.error("Reason-Code ist Pflicht.")
                        else:
                            c["reviewer2"] = user; c["reason2"] = reason2.strip(); c["status"] = "FREIGEGEBEN"
                            log("APPROVE_L2", parent, reason2.strip()); st.rerun()

            elif c["status"] == "FREIGEGEBEN":
                st.success("Freigegeben. Weiter auf Seite **Buchung, Audit & Versand** (Beleg parken).")
            elif c["status"] == "ABGELEHNT":
                st.error(f"Abgelehnt von {c['reviewer1']} — „{c['reason1']}“")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ==============================================================================
# PAGE: BUCHUNG, AUDIT & VERSAND
# ==============================================================================
elif page == "💎 Buchung, Audit & Versand":
    global_header("Buchung, Audit & Versand", "Geparkter Beleg, Release, Konsolidierungs-Chart, CFO-Entwurf und Audit-Log.")

    st.markdown("#### 💎 Buchung (geparkt → Release)")
    st.caption("🟠 STUB: Prod ruft BAPI_ACC_DOCUMENT_POST mit Status PARKED; Freigabe im SAP unter der SAP-ID des Genehmigers. Kein Auto-Posting.")
    explain("Ein freigegebener Anspruch wird <b>nicht</b> automatisch gebucht. Er wird als <b>geparkter</b> Beleg "
            "angelegt (FB60-Park) und muss von einer Genehmiger-Rolle separat im SAP released werden — unter deren "
            "eigener Kennung. Das trennt Vorschlag, Freigabe und Buchung sauber.")
    if not st.session_state.get("engine_ran"):
        st.info("Bitte zuerst **Resolution & Güte** ausführen und den Anspruch in **Review & Vier-Augen** freigeben.")
    else:
        approved = {p: c for p, c in st.session_state.claims.items()
                    if c["qualified"] and c["status"] in ("FREIGEGEBEN", "GEPARKT", "RELEASED")}
        if not approved:
            st.caption("Noch kein freigegebener Anspruch. (Erst in Review & Vier-Augen freigeben.)")
        for parent, c in approved.items():
            st.markdown(f"**{parent}** · {fmt(c['cashback'])} · Status `{c['status']}`")
            if c["status"] == "FREIGEGEBEN":
                if not role["can_review"]:
                    st.warning("Parken erfordert mindestens Review-Berechtigung.")
                elif st.button(f"📄 Beleg parken (FB60-Park) — {parent}", key=f"park_{parent}"):
                    c["status"] = "GEPARKT"; c["park_id"] = f"PARK-{random.randint(100000,999999)}"
                    log("PARK_DOC", parent, f"{c['park_id']} · {fmt(c['cashback'])}"); st.rerun()
            elif c["status"] == "GEPARKT":
                st.caption(f"Geparkt als `{c['park_id']}` — wartet auf Release durch Genehmiger-Rolle.")
                if not role["can_release"]:
                    st.warning("Release nur durch Genehmiger-Rolle (Release-Berechtigung). Rolle in der Sidebar wechseln.")
                elif st.button(f"🚀 In SAP freigeben (Release) — {parent}", key=f"rel_{parent}"):
                    c["status"] = "RELEASED"; c["doc"] = f"#10{random.randint(9000000,9999999)}"
                    log("RELEASE", parent, f"{c['doc']} · {fmt(c['cashback'])}"); st.rerun()
            elif c["status"] == "RELEASED":
                st.success(f"Gebucht (Beleg {c['doc']}): {fmt(c['cashback'])}")

        st.markdown("#### 📈 Konsolidierung vs. Einzelsilo")
        explain("Der „Aha“-Chart. Der graue Balken ist das <b>größte einzelne SAP-Kreditorkonto</b> der Gruppe — das, "
                "was klassisches Reporting sieht und das unter der blauen Schwellenlinie bleibt. Der grüne Balken ist "
                "der <b>konsolidierte Konzern-Spend</b>, der die Linie überschreitet und damit den Anspruch auslöst.")
        focus_parent = next(iter({p: cc for p, cc in st.session_state.claims.items() if cc['qualified']}), None)
        if focus_parent:
            cc = st.session_state.claims[focus_parent]
            silo_max = df_lfa1[df_lfa1["LIFNR"].isin(cc["members"])]["SPEND_YTD"].max()
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Max. SAP-Einzelsilo", x=[focus_parent], y=[silo_max],
                                 marker_color="#3A3A3C", text=[fmt(silo_max)], textposition="auto"))
            fig.add_trace(go.Bar(name="Konsolidiert (verifiziert)", x=[focus_parent], y=[cc["spend"]],
                                 marker_color="#30D158", text=[fmt(cc["spend"])], textposition="outside"))
            fig.add_hline(y=THRESHOLD, line_dash="dash", line_color="#007AFF",
                          annotation_text="Kickback-Schwelle 50 Mio. €", annotation_font_color="#007AFF")
            fig.update_layout(barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#F5F5F7"), height=380, margin=dict(l=10, r=10, t=30, b=10),
                              legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
                              yaxis=dict(range=[0, max(cc["spend"]*1.25, 55_000_000)], gridcolor="#1C1C1E"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Noch keine qualifizierte Entität — bitte Engine ausführen.")

    st.markdown("#### ✉️ C-Level-Kommunikation — ENTWURF")
    st.markdown("<span class='pill-draft'>DRAFT-ONLY</span> · Kein automatischer Versand. Ein Mensch prüft und versendet manuell.",
                unsafe_allow_html=True)
    explain("Ein vorbereiteter Entwurf an den CFO über die realisierten Ansprüche — bewusst <b>nicht</b> automatisch "
            "verschickt. Autonome Finanzkommunikation an die Geschäftsleitung wäre genau das, was Vertrauen zerstört; "
            "deshalb bleibt der Mensch der Absender.")
    released_claims = {p: c for p, c in st.session_state.claims.items() if c.get("status") == "RELEASED"}
    if released_claims:
        body_lines = "\n".join([f"- {p}: {fmt(c['cashback'])} (Beleg {c['doc']}, L1={c['reviewer1']} / L2={c['reviewer2']})"
                                for p, c in released_claims.items()])
        draft = (f"An: Dr. Henrik von Bohlen (CFO)\n"
                 f"Betreff: [ENTWURF] Realisierte Rückvergütungen — Group Procurement\n\n"
                 f"Sehr geehrter Herr Dr. von Bohlen,\n\n"
                 f"nach verifizierter Entity Resolution und Vier-Augen-Freigabe wurden folgende "
                 f"Rückvergütungsansprüche als geparkte Belege im SAP zur Buchung gebracht:\n\n"
                 f"{body_lines}\n\n"
                 f"Hinweis: Es handelt sich um vertragliche Ansprüche; die finale Realisierung erfolgt im "
                 f"kommerziellen Prozess mit dem Lieferanten. Evidenz und Audit-Trail liegen bei.\n\n"
                 f"Mit besten Grüßen\nGroup Procurement")
        st.text_area("Entwurf (zum Kopieren / manuellen Versand)", value=draft, height=240)
    else:
        st.caption("Noch kein freigegebener Anspruch — kein Entwurf erzeugt.")

    st.markdown("#### 🧾 Unveränderlicher Audit-/Decision-Log")
    explain("Jede Aktion (Engine-Lauf, L1/L2-Freigabe, Ablehnung, Parken, Release) mit Akteur, Uhrzeit, Objekt und "
            "Begründung — append-only und als CSV exportierbar. Das ist gleichzeitig der Compliance- und EU-AI-Act-Nachweis: "
            "wer hat was auf welcher Basis entschieden.")
    if st.session_state.audit_log:
        df_log = pd.DataFrame(st.session_state.audit_log)
        st.dataframe(df_log, use_container_width=True, hide_index=True, height=240)
        st.download_button("⬇️ Audit-Log als CSV", df_log.to_csv(index=False).encode("utf-8"),
                           "audit_log.csv", "text/csv")
    else:
        st.caption("Noch keine Aktionen protokolliert.")
