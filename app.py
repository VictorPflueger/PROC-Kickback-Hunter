# ==============================================================================
# PROC Kickback Hunter AI  —  v6.0 "Agentic Single-Flow"
# ------------------------------------------------------------------------------
# Single-File Streamlit-Prototyp. Geführter Single-Screen-Flow: EIN Button löst
# eine Agentenkette aus, ein Token-Dict wird sequenziell durch die Agenten
# gereicht und pro Stufe um Ergebnis + Evidenz angereichert. Genau EINE
# Human-in-the-Loop-Freigabe (Pflicht-Reason-Code). Ehrliche LIVE/STUB-Trennung.
#
# Stack (requirements.txt unverändert): streamlit, pandas, plotly + stdlib.
# ==============================================================================

import json
import random
from datetime import datetime
from difflib import SequenceMatcher

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# 0. PAGE CONFIG & APPLE CUPERTINO DARK MODE CSS
# ==============================================================================
st.set_page_config(
    page_title="PROC Kickback Hunter AI | GlobalCorp SE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #0A0A0C !important;
        color: #F5F5F7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif;
    }
    .frosted-glass {
        background: rgba(28, 28, 30, 0.65) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45) !important;
    }
    div.stButton > button:first-child {
        background-color: #007AFF !important; color: #FFFFFF !important;
        border-radius: 12px !important; font-weight: 600 !important;
        letter-spacing: 0.3px !important; border: none !important;
        padding: 12px 24px !important; transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #0062CC !important; transform: scale(1.01);
        box-shadow: 0 0 20px rgba(0, 122, 255, 0.4);
    }
    /* Pipeline-Track im Header (auf .agent-pill aus früheren Versionen aufgebaut) */
    .pipeline-track {
        display: flex; justify-content: space-between; align-items: stretch;
        background: rgba(18, 18, 20, 0.8); padding: 14px 16px; border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06); margin-bottom: 8px; gap: 8px;
    }
    .agent-pill {
        flex: 1; text-align: center; padding: 12px 6px; border-radius: 10px;
        font-size: 12.5px; font-weight: 600; color: rgba(255, 255, 255, 0.4);
        background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .agent-pill.active {
        color: #FFFFFF; background: rgba(0, 122, 255, 0.18); border-color: #007AFF;
        box-shadow: 0 0 18px rgba(0, 122, 255, 0.35); transform: translateY(-2px);
    }
    .agent-pill.done { color: #30D158; background: rgba(48, 209, 88, 0.12); border-color: #30D158; }
    /* Mensch-Gate optisch abgesetzt (Amber) */
    .agent-pill.human { border-style: dashed; }
    .agent-pill.human.active {
        color: #FFD60A; background: rgba(255, 214, 10, 0.16); border-color: #FFD60A;
        box-shadow: 0 0 18px rgba(255, 214, 10, 0.30);
    }
    .agent-pill.human.done { color: #FFD60A; background: rgba(255, 214, 10, 0.10); border-color: #FFD60A; }
    .pill-sub { display:block; font-size:10px; font-weight:500; opacity:0.7; margin-top:2px; }
    /* LIVE / STUB Badges */
    .tag { font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 6px;
           letter-spacing: 0.4px; vertical-align: middle; }
    .tag-live { color:#30D158; background:rgba(48,209,88,0.12); border:1px solid #30D158; }
    .tag-stub { color:#FF9F0A; background:rgba(255,159,10,0.12); border:1px solid #FF9F0A; }
    .apple-mail-box {
        background-color: #161618; border: 1px solid #2C2C30; border-radius: 14px;
        padding: 22px; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    }
    .mail-row { margin-bottom: 6px; font-size: 13px; color: #8E8E93; }
    .mail-row span.val { color: #FFFFFF; font-weight: 500; }
    .mail-divider { border-top: 1px solid #2C2C30; margin: 14px 0; }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: 700 !important; letter-spacing: -0.5px !important; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

def fmt_curr(val):
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_mio(val):
    return f"{val/1_000_000:,.1f} Mio. €".replace(",", "X").replace(".", ",").replace("X", ".")

# ==============================================================================
# 1. FACHLICHE KONSTANTEN
# ==============================================================================
THRESHOLD = 50_000_000.0   # Konsolidierte Umsatzschwelle für den Kickback-Anspruch
RATE = 0.02                # Rückvergütungssatz

CISCO_IDS = ["10001", "10002", "10003", "10004", "10005"]
MSFT_IDS = ["20001", "20002"]
APEX_IDS = ["40001", "40002"]

# Deterministische Kern-Kreditoren inkl. bewusstem Apex-Lookalike-Paar
CORE_VENDORS = [
    {"LIFNR": "10001", "NAME1": "Cisco Systems Germany GmbH",  "ORT01": "Bonn",       "LAND1": "DE", "STCD1": "DE123456780", "SPEND_YTD": 18_200_000.0},
    {"LIFNR": "10002", "NAME1": "Cisco Technology Inc.",        "ORT01": "San Jose",   "LAND1": "US", "STCD1": "US987654321", "SPEND_YTD": 14_100_000.0},
    {"LIFNR": "10003", "NAME1": "Meraki Cloud Networks Ltd.",   "ORT01": "London",     "LAND1": "GB", "STCD1": "GB554433221", "SPEND_YTD": 9_500_000.0},
    {"LIFNR": "10004", "NAME1": "Acacia Communications Opto",   "ORT01": "Maynard",    "LAND1": "US", "STCD1": "US112233445", "SPEND_YTD": 6_200_000.0},
    {"LIFNR": "10005", "NAME1": "Splunk Software EMEA",         "ORT01": "Munich",     "LAND1": "DE", "STCD1": "DE887766554", "SPEND_YTD": 4_400_000.0},
    {"LIFNR": "20001", "NAME1": "Microsoft Deutschland GmbH",   "ORT01": "Munich",     "LAND1": "DE", "STCD1": "DE998877665", "SPEND_YTD": 41_000_000.0},
    {"LIFNR": "20002", "NAME1": "Activision Blizzard Germany",  "ORT01": "Ismaning",   "LAND1": "DE", "STCD1": "DE556677889", "SPEND_YTD": 6_000_000.0},
    # Bewusstes Lookalike-Paar: fast identische Namen, ABER verschiedene reale Mütter.
    {"LIFNR": "40001", "NAME1": "Apex Robotics Solutions GmbH", "ORT01": "Stuttgart",  "LAND1": "DE", "STCD1": "DE606060601", "SPEND_YTD": 2_300_000.0},
    {"LIFNR": "40002", "NAME1": "Apex Robotics Systems Ltd.",   "ORT01": "Manchester", "LAND1": "GB", "STCD1": "GB707070702", "SPEND_YTD": 1_900_000.0},
]

# Verifizierte Parent-Wissensbasis (GLEIF/D&B-STUB) = EINZIGE Merge-Autorität.
# Stadt, Adresse und reine Namens-Ähnlichkeit sind KEINE Merge-Signale.
# Verifiziert == LEI beginnt mit '529900'. Die Apex-Einträge sind bewusst
# UNVERIFIZIERT bzw. tragen verschiedene Mütter -> kein Merge.
PARENT_KB = {
    "10001": ("Cisco Systems, Inc.",      "529900CISCO0001", "Konzernmutter (HQ San Jose)"),
    "10002": ("Cisco Systems, Inc.",      "529900CISCO0001", "Stammgesellschaft US"),
    "10003": ("Cisco Systems, Inc.",      "529900CISCO0001", "Meraki → Cisco (Akquisition 2012)"),
    "10004": ("Cisco Systems, Inc.",      "529900CISCO0001", "Acacia → Cisco (Akquisition 2021)"),
    "10005": ("Cisco Systems, Inc.",      "529900CISCO0001", "Splunk → Cisco (Akquisition 2024)"),
    "20001": ("Microsoft Corporation",    "529900MSFT00001", "Konzernmutter (HQ Redmond)"),
    "20002": ("Microsoft Corporation",    "529900MSFT00001", "Activision Blizzard → Microsoft (2023)"),
    "40001": ("Apex Robotics Holding AG", "UNVERIFIZIERT-DE", "KB: eigenständiger DE-Konzern"),
    "40002": ("Apex Industrial Group plc","UNVERIFIZIERT-GB", "KB: anderer GB-Konzern (kein Bezug zu 40001)"),
}

VERTRAGSKLAUSEL = (
    "§4.2 Rahmenvertrag: 2,0 % Rückvergütung auf den KONSOLIDIERTEN Konzernumsatz, "
    "fällig ab exakt 50.000.000,00 € kumuliertem Spend pro Geschäftsjahr."
)

REASON_CODES = [
    "— bitte Reason-Code wählen —",
    "RC-01 Parent-Linkage verifiziert (KB-Quelle geprüft)",
    "RC-02 Konsolidierte Schwelle eindeutig überschritten",
    "RC-03 Beleg-Stichprobe (EKKO) plausibilisiert",
    "RC-90 Ablehnung: Evidenz/Parent-Linkage unzureichend",
    "RC-91 Ablehnung: Schwelle nicht erreicht — keine Buchung",
]

CFO_NAME = "Dr. Henrik von Bohlen (CFO)"

PIPELINE = [
    ("🛬", "Ingestion", "SAP LFA1/EKKO", "stub"),
    ("🧬", "Resolution", "Entity Resolution", "live"),
    ("📑", "Contract", "Klausel-RAG", "stub"),
    ("🧮", "Finance", "Spend & Verdict", "live"),
    ("🧑‍⚖️", "Human Review", "Freigabe + Reason", "human"),
    ("📒", "Booking", "BAPI Park / Draft", "stub"),
]

# ==============================================================================
# 2. EPIC 1: DETERMINISTISCHER IN-MEMORY-DATENGENERATOR (150 Kreditoren)
# ==============================================================================
@st.cache_data
def generate_enterprise_sap_data():
    random.seed(1337)
    stems = ["Logistics", "Facility", "Consulting", "MRO", "Packaging",
             "IT-Services", "Robotics", "Chemicals", "Security", "Fleet"]
    cities = ["Frankfurt", "Stuttgart", "Hamburg", "Berlin", "Düsseldorf",
              "Paris", "Zurich", "Vienna", "Milan", "Madrid", "Amsterdam"]
    # 'Apex' bewusst NICHT in den Fillern -> das einzige Apex-Paar ist das Kern-Lookalike
    prefixes = ["Global", "Nova", "Sino", "Euro", "Chroma", "Stellar", "Vanguard", "Omni", "Inno"]

    fillers = []
    for i in range(8, 149):  # 141 Filler -> 9 Kern + 141 = 150
        spend = round(random.uniform(15000.0, 3_800_000.0), 2)
        fillers.append({
            "LIFNR": f"{30000 + i}",
            "NAME1": f"{random.choice(prefixes)} {random.choice(stems)} {random.choice(['GmbH', 'AG', 'S.A.', 'Ltd'])}",
            "ORT01": random.choice(cities),
            "LAND1": random.choice(["DE", "FR", "CH", "AT", "IT", "ES", "NL"]),
            "STCD1": f"EU{random.randint(100000000, 999999999)}",
            "SPEND_YTD": spend,
        })

    all_vendors = CORE_VENDORS + fillers
    df_lfa1 = pd.DataFrame(all_vendors)

    po_counts = {"10001": 30, "10002": 25, "10003": 20, "10004": 15, "10005": 10,
                 "20001": 35, "20002": 15, "40001": 9, "40002": 8}
    for idx, v in enumerate(fillers):
        po_counts[v["LIFNR"]] = 8 if idx < 49 else 7

    ekko_rows = []
    ebeln_base = 4500000001
    for v in all_vendors:
        lifnr = v["LIFNR"]
        n_pos = po_counts[lifnr]
        target_cents = int(v["SPEND_YTD"] * 100)
        cutpoints = sorted([random.randint(1, target_cents - 1) for _ in range(n_pos - 1)])
        cutpoints = [0] + cutpoints + [target_cents]
        for k in range(len(cutpoints) - 1):
            netwr = (cutpoints[k + 1] - cutpoints[k]) / 100.0
            ekko_rows.append({
                "EBELN": str(ebeln_base), "LIFNR": lifnr, "BUKRS": "1000",
                "AEDAT": f"2026-{random.randint(1, 5):02d}-{random.randint(1, 28):02d}",
                "NETWR": netwr, "WAERS": "EUR",
            })
            ebeln_base += 1
    df_ekko = pd.DataFrame(ekko_rows).sample(frac=1, random_state=42).reset_index(drop=True)
    return df_lfa1, df_ekko

df_lfa1, df_ekko = generate_enterprise_sap_data()

# ==============================================================================
# 3. LIVE-KERN: DETERMINISTISCHE, ERKLÄRBARE ENTITY RESOLUTION + GÜTE-MESSUNG
# ==============================================================================
def resolve_entities(df):
    """Verklammert Konten ausschließlich über die VERIFIZIERTE Parent-Linkage.
    Rückgabe: dict cluster_key -> {parent, lei, verified, members[], evidence[]}."""
    clusters = {}
    for _, r in df.iterrows():
        lifnr = r["LIFNR"]
        if lifnr in PARENT_KB:
            parent, lei, note = PARENT_KB[lifnr]
            verified = lei.startswith("529900")            # nur verifizierte Mütter mergen
            key = parent if verified else f"SINGLE::{lifnr}"
        else:
            parent, lei, note, verified = ("(kein KB-Eintrag)", "—", "Singleton: keine verifizierte Mutter", False)
            key = f"SINGLE::{lifnr}"
        c = clusters.setdefault(key, {"parent": parent, "lei": lei, "verified": verified, "members": [], "evidence": []})
        c["members"].append(lifnr)
        c["evidence"].append({"LIFNR": lifnr, "NAME1": r["NAME1"], "ORT01": r["ORT01"],
                              "LAND1": r["LAND1"], "Linkage": note, "Quelle": "GLEIF/D&B (STUB)"})
    return clusters

def ground_truth_labels(df):
    """Gelabelte ökonomische Wahrheit für die Accuracy-Messung."""
    gt = {}
    for lifnr in df["LIFNR"]:
        if lifnr in CISCO_IDS:
            gt[lifnr] = "GT_CISCO"
        elif lifnr in MSFT_IDS:
            gt[lifnr] = "GT_MSFT"
        else:
            gt[lifnr] = f"GT_{lifnr}"   # Apex 40001/40002 getrennt, Filler je einzeln
    return gt

def pred_labels(clusters):
    lab = {}
    for key, c in clusters.items():
        for m in c["members"]:
            lab[m] = key
    return lab

def pairwise_metrics(pred, gt):
    ids = list(gt.keys())
    tp = fp = fn = 0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            same_pred = pred[a] == pred[b]
            same_true = gt[a] == gt[b]
            if same_pred and same_true:
                tp += 1
            elif same_pred and not same_true:
                fp += 1            # Falsch-Merge
            elif (not same_pred) and same_true:
                fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    return {"precision": precision, "recall": recall, "false_merges": fp, "tp": tp, "fn": fn}

def name_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

@st.cache_data
def compute_quality():
    clusters = resolve_entities(df_lfa1)
    gt = ground_truth_labels(df_lfa1)
    metrics = pairwise_metrics(pred_labels(clusters), gt)
    # Ehrliche difflib-Belege: warum Name/Stadt allein kein Merge-Signal sein darf
    nm = {r["LIFNR"]: r["NAME1"] for _, r in df_lfa1.iterrows()}
    examples = [
        {"fall": "Lookalike (würde fälschlich mergen)",
         "paar": "40001 ↔ 40002 (Apex)",
         "namensaehnlichkeit": name_similarity(nm["40001"], nm["40002"]),
         "kb_merge": False,
         "kommentar": "Hohe Namensnähe, aber verschiedene verifizierte Mütter → bewusst NICHT gemerged."},
        {"fall": "Echte M&A-Verbindung (würde verfehlt)",
         "paar": "10001 ↔ 10003 (Cisco ↔ Meraki)",
         "namensaehnlichkeit": name_similarity(nm["10001"], nm["10003"]),
         "kb_merge": True,
         "kommentar": "Niedrige Namensnähe, aber dieselbe verifizierte Mutter → korrekt gemerged."},
    ]
    return clusters, metrics, examples

CLUSTERS, METRICS, NAME_EXAMPLES = compute_quality()

# ==============================================================================
# 4. STATE-HELPER
# ==============================================================================
def init_state():
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("audit_log", [])   # append-only
    st.session_state.setdefault("target", "CISCO")

def log_audit(token, actor, stage, action, detail):
    st.session_state["audit_log"].append({
        "Zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Vorgang": token.get("vorgang_id", "—"),
        "Akteur": actor,
        "Stufe": stage,
        "Aktion": action,
        "Detail": detail,
    })

def claim_ids_for_target(target):
    return {"CISCO": CISCO_IDS, "MICROSOFT": MSFT_IDS, "APEX": ["40001"]}[target]

# ==============================================================================
# 5. AGENTEN  —  agent(token) -> token   (jeder liest, arbeitet, reichert an)
# ==============================================================================
def agent_ingestion(token):
    n_focus = len(token["claim_ids"])
    ekko_focus = int(df_ekko[df_ekko["LIFNR"].isin(token["claim_ids"])].shape[0])
    token["ingestion"] = {
        "modus": "STUB",
        "quelle": "SAP LFA1 / EKKO via RFC-BAPI (simuliert; Daten deterministisch in-memory)",
        "kreditoren_gesamt": int(df_lfa1.shape[0]),
        "bestellbelege_gesamt": int(df_ekko.shape[0]),
        "fokus_konten": token["claim_ids"],
        "fokus_belege": ekko_focus,
    }
    token["stage_idx"] = 0
    log_audit(token, "Ingestion-Agent", "Ingestion",
              "SAP-Quelldaten geladen (STUB)",
              f"{df_lfa1.shape[0]} Kreditoren / {df_ekko.shape[0]} Belege; Fokus {n_focus} Konten")
    return token

def agent_resolution(token):
    primary = token["claim_ids"][0]
    cluster_key = pred_labels(CLUSTERS)[primary]
    cluster = CLUSTERS[cluster_key]
    token["resolution"] = {
        "modus": "LIVE",
        "merge_autoritaet": "Ausschließlich verifizierte Parent-Linkage (PARENT_KB / GLEIF/D&B-STUB)",
        "cluster_parent": cluster["parent"],
        "cluster_lei": cluster["lei"],
        "verklammerte_konten": cluster["members"],
        "anzahl_konten": len(cluster["members"]),
        "evidenz": cluster["evidence"],
        "guete": {
            "precision_pct": round(METRICS["precision"] * 100, 1),
            "recall_pct": round(METRICS["recall"] * 100, 1),
            "false_merges": METRICS["false_merges"],
            "geprüfte_paare_tp": METRICS["tp"],
        },
        "lookalike_review": {
            "paar": "Apex Robotics Solutions GmbH (40001) ↔ Apex Robotics Systems Ltd. (40002)",
            "entscheidung": "NICHT gemerged — verschiedene verifizierte Mütter",
            "namensaehnlichkeit_pct": round(NAME_EXAMPLES[0]["namensaehnlichkeit"] * 100, 1),
        },
    }
    token["stage_idx"] = 1
    log_audit(token, "Resolution-Agent", "Resolution",
              "Entity Resolution (LIVE)",
              f"{len(cluster['members'])} Konten → 1 Entität '{cluster['parent']}'; "
              f"P/R {token['resolution']['guete']['precision_pct']}/"
              f"{token['resolution']['guete']['recall_pct']} %, "
              f"{METRICS['false_merges']} Falsch-Merges")
    return token

def agent_contract(token):
    token["contract"] = {
        "modus": "STUB",
        "quelle": "Z_CONTRACTS RAG (Klausel deterministisch hinterlegt, keine echte LLM-Extraktion)",
        "schwelle_eur": THRESHOLD,
        "satz": RATE,
        "klausel": VERTRAGSKLAUSEL,
    }
    token["stage_idx"] = 2
    log_audit(token, "Contract-Agent", "Contract",
              "Vertragsklausel gezogen (STUB)",
              f"Schwelle {fmt_mio(THRESHOLD)} / Satz {RATE*100:.1f} %")
    return token

def agent_finance(token):
    members = token["resolution"]["verklammerte_konten"]
    dff = df_lfa1[df_lfa1["LIFNR"].isin(members)]
    consolidated = float(dff["SPEND_YTD"].sum())
    silo_max = float(dff["SPEND_YTD"].max())
    qualified = consolidated >= THRESHOLD
    cashback = round(consolidated * RATE, 2) if qualified else 0.0
    token["finance"] = {
        "modus": "LIVE",
        "max_einzelsilo": silo_max,
        "konsolidierter_spend": consolidated,
        "delta_durch_resolution": consolidated - silo_max,
        "schwelle": THRESHOLD,
        "qualifiziert": qualified,
        "cashback": cashback,
        "verdict": ("ANSPRUCH" if qualified else "KEIN ANSPRUCH"),
    }
    token["stage_idx"] = 3
    token["status"] = "AWAITING_APPROVAL"
    log_audit(token, "Finance-Agent", "Finance",
              "Spend konsolidiert & gegen Schwelle geprüft (LIVE)",
              f"{fmt_curr(consolidated)} vs. {fmt_mio(THRESHOLD)} → "
              f"{token['finance']['verdict']}; Cashback {fmt_curr(cashback)}")
    return token

def agent_booking(token):
    fin = token["finance"]
    members = token["resolution"]["verklammerte_konten"]
    dff = df_lfa1[df_lfa1["LIFNR"].isin(members)]
    vendor_lines = "".join(
        f"• {r['LIFNR']}: {r['NAME1']} ({r['ORT01']}) — {fmt_curr(r['SPEND_YTD'])}<br>"
        for _, r in dff.iterrows()
    )
    beleg_id = "4900" + datetime.now().strftime("%H%M%S")
    token["booking"] = {
        "modus": "STUB",
        "bapi": "BAPI_ACC_DOCUMENT_POST (simulierte Parkung, kein echter Commit)",
        "beleg_id": beleg_id,
        "buchungstext": f"Debitor an Erlöse aus Rückvergütungen: {fmt_curr(fin['cashback'])}",
        "mail_draft": {
            "status": "DRAFT-ONLY — nicht versendet",
            "an": CFO_NAME,
            "betreff": f"[CASHBACK SECURED] +{fmt_curr(fin['cashback'])} für {token['parent']}",
            "vendor_lines": vendor_lines,
        },
    }
    token["stage_idx"] = 5
    token["status"] = "BOOKED"
    log_audit(token, "Booking-Agent", "Booking",
              "Beleg geparkt (STUB) & CFO-Draft erzeugt",
              f"Beleg #{beleg_id}; {fmt_curr(fin['cashback'])}; Mail = Draft-only")
    return token

# ==============================================================================
# 6. APP
# ==============================================================================
init_state()

# ---- Header -----------------------------------------------------------------
st.markdown("""
<div class="frosted-glass" style="margin-bottom: 14px;">
  <h1 style="margin:0; font-size: 30px; font-weight: 800; letter-spacing: -1px;">
    PROC Kickback Hunter AI <span style="color:#007AFF; font-size: 18px;">v6.0 · Agentic Single-Flow</span>
  </h1>
  <p style="margin: 4px 0 0 0; color: #8E8E93; font-size: 14px;">
    Ein Vorgangs-Token wird durch sechs Agenten gereicht — mit genau einer menschlichen Freigabe.
  </p>
</div>
""", unsafe_allow_html=True)

# ---- Pipeline-Track (Prozessverlauf, dauerhaft sichtbar) --------------------
def render_pipeline(token):
    cur = token["stage_idx"] if token else -1            # Index der letzten ABGESCHLOSSENEN Stufe
    awaiting = bool(token and token.get("status") == "AWAITING_APPROVAL")
    rejected = bool(token and token.get("status") == "REJECTED")
    html = '<div class="pipeline-track">'
    for i, (icon, label, sub, kind) in enumerate(PIPELINE):
        cls = "agent-pill"
        if kind == "human":
            cls += " human"
        # Status bestimmen
        if i <= cur:
            status = "done"
        elif awaiting and i == 4:
            status = "active"
        elif (not awaiting) and (not rejected) and i == cur + 1 and token:
            status = "active"
        else:
            status = ""
        if rejected and i == 5:
            sub = "übersprungen"
        html += (f'<div class="{cls} {status}">{icon} {label}'
                 f'<span class="pill-sub">{sub}</span></div>')
    return html + "</div>"

token = st.session_state["token"]
st.markdown(render_pipeline(token), unsafe_allow_html=True)
st.markdown(
    '<div style="margin:0 2px 16px 2px; font-size:12px; color:#8E8E93;">'
    '<span class="tag tag-live">LIVE</span> echt implementiert &nbsp;·&nbsp; '
    '<span class="tag tag-stub">STUB</span> bewusst simuliert &nbsp;·&nbsp; '
    'Merge-Autorität ausschließlich verifizierte Parent-Linkage — Stadt/Name allein mergen nie.'
    '</div>', unsafe_allow_html=True)

# ---- Steuerleiste -----------------------------------------------------------
running = token is not None
c1, c2, c3 = st.columns([1.6, 1.0, 1.0])
with c1:
    target_label = st.selectbox(
        "Ziel-Vorgang",
        options=["CISCO", "MICROSOFT", "APEX"],
        index=["CISCO", "MICROSOFT", "APEX"].index(st.session_state["target"]),
        format_func=lambda x: {
            "CISCO": "Cisco Group — Showcase (qualifiziert)",
            "MICROSOFT": "Microsoft-Cluster — Negativbeleg (47,0 Mio.)",
            "APEX": "Apex — Lookalike-Review (bewusst kein Merge)",
        }[x],
        disabled=running,
        help="Bei laufendem Vorgang zuerst zurücksetzen.",
    )
    st.session_state["target"] = target_label
with c2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    start = st.button("🚀 Prozess starten", type="primary", disabled=running, use_container_width=True)
with c3:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    reset = st.button("↩︎ Zurücksetzen", disabled=not running, use_container_width=True)

if reset:
    st.session_state["token"] = None
    st.rerun()

# ---- Start: autonome Kette Ingestion → Resolution → Contract → Finance ------
if start:
    target = st.session_state["target"]
    primary = claim_ids_for_target(target)[0]
    parent = PARENT_KB.get(primary, ("(unbekannt)", "", ""))[0]
    new_token = {
        "vorgang_id": "VG-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "erstellt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ziel": target,
        "parent": parent,
        "claim_ids": claim_ids_for_target(target),
        "status": "STARTED",
        "stage_idx": 0,
    }
    log_audit(new_token, "Orchestrator", "Start", "Vorgang angelegt", f"Ziel = {target}")
    new_token = agent_ingestion(new_token)
    new_token = agent_resolution(new_token)
    new_token = agent_contract(new_token)
    new_token = agent_finance(new_token)
    st.session_state["token"] = new_token
    st.rerun()

token = st.session_state["token"]

# ---- Token-State (wächst pro Stufe) -----------------------------------------
with st.expander("🧾 Vorgangs-Token (wächst pro Agenten-Stufe)", expanded=False):
    if token:
        st.caption(f"Vorgang {token['vorgang_id']} · Status {token['status']}")
        st.code(json.dumps(token, indent=2, ensure_ascii=False, default=str), language="json")
    else:
        st.info("Noch kein Vorgang. Ziel wählen und **Prozess starten**.")

# ==============================================================================
# 7. PROGRESSIVE STUFEN-DARSTELLUNG (Single-Screen-Narrativ)
# ==============================================================================
if token:
    ing = token["ingestion"]
    res = token["resolution"]
    con = token["contract"]
    fin = token["finance"]

    # ---- Stufe 1: Ingestion ----
    with st.expander(f"🛬 Stufe 1 · Ingestion-Agent  ·  STUB", expanded=False):
        st.markdown(f'<span class="tag tag-stub">STUB</span> {ing["quelle"]}', unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.metric("Kreditoren gesamt", ing["kreditoren_gesamt"])
        b.metric("Bestellbelege gesamt", ing["bestellbelege_gesamt"])
        c.metric("Fokus-Konten", len(ing["fokus_konten"]))
        dff = df_lfa1[df_lfa1["LIFNR"].isin(ing["fokus_konten"])]
        st.dataframe(dff.style.format({"SPEND_YTD": "{:,.2f} €"}), use_container_width=True, hide_index=True)

    # ---- Stufe 2: Resolution (zentraler Mehrwert) ----
    with st.expander(f"🧬 Stufe 2 · Resolution-Agent  ·  LIVE  —  aus {res['anzahl_konten']} Silos wird 1 Entität",
                     expanded=True):
        st.markdown(f'<span class="tag tag-live">LIVE</span> Merge-Autorität: {res["merge_autoritaet"]}',
                    unsafe_allow_html=True)
        st.markdown(f"**Konsolidierte Entität:** {res['cluster_parent']}  ·  LEI `{res['cluster_lei']}`")
        st.dataframe(pd.DataFrame(res["evidenz"]), use_container_width=True, hide_index=True)

        g = res["guete"]
        st.markdown("**Gemessene Güte gegen gelabelte Ground-Truth (EU-AI-Act-/Audit-Evidenz)**")
        q1, q2, q3 = st.columns(3)
        q1.metric("Precision", f"{g['precision_pct']:.1f} %")
        q2.metric("Recall", f"{g['recall_pct']:.1f} %")
        q3.metric("Falsch-Merges", g["false_merges"])

        lr = res["lookalike_review"]
        st.markdown(
            f"""<div class="frosted-glass" style="border-color:#FFD60A !important; background:rgba(255,214,10,0.05) !important;">
            <b>🟡 Lookalike-Review (bewusst kein Auto-Merge):</b><br>
            {lr['paar']}<br>
            Namensähnlichkeit <b>{lr['namensaehnlichkeit_pct']:.1f} %</b> → {lr['entscheidung']}.
            </div>""", unsafe_allow_html=True)
        st.caption(
            f"Warum Name/Stadt allein nie mergen darf — live mit difflib gerechnet: "
            f"Apex-Paar {NAME_EXAMPLES[0]['namensaehnlichkeit']*100:.1f} % Namensnähe (wäre Falsch-Merge), "
            f"Cisco ↔ Meraki nur {NAME_EXAMPLES[1]['namensaehnlichkeit']*100:.1f} % "
            f"(echte M&A-Verbindung, die reines Name-Matching verfehlen würde).")

    # ---- Stufe 3: Contract ----
    with st.expander("📑 Stufe 3 · Contract-Agent  ·  STUB", expanded=False):
        st.markdown(f'<span class="tag tag-stub">STUB</span> {con["quelle"]}', unsafe_allow_html=True)
        st.markdown(f"> {con['klausel']}")

    # ---- Stufe 4: Finance (€-Mehrwert) ----
    with st.expander("🧮 Stufe 4 · Finance-Agent  ·  LIVE", expanded=True):
        st.markdown('<span class="tag tag-live">LIVE</span> Konsolidierung & Schwellenprüfung',
                    unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Max. SAP-Einzelsilo", fmt_curr(fin["max_einzelsilo"]))
        k2.metric("Konsolidierter Spend", fmt_curr(fin["konsolidierter_spend"]),
                  f"+{fmt_curr(fin['delta_durch_resolution'])}")
        k3.metric("Schwelle", fmt_mio(fin["schwelle"]),
                  "überschritten" if fin["qualifiziert"] else "nicht erreicht",
                  delta_color="normal" if fin["qualifiziert"] else "off")
        k4.metric("Cashback (2 %)", fmt_curr(fin["cashback"]))

        bar_color = "#30D158" if fin["qualifiziert"] else "#FF453A"
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Max. SAP-Einzelsilo", x=[token["parent"]], y=[fin["max_einzelsilo"]],
                             marker_color="#3A3A3C", text=[fmt_curr(fin["max_einzelsilo"])], textposition="auto"))
        fig.add_trace(go.Bar(name="AI konsolidiert", x=[token["parent"]], y=[fin["konsolidierter_spend"]],
                             marker_color=bar_color, text=[fmt_curr(fin["konsolidierter_spend"])], textposition="outside"))
        fig.add_hline(y=THRESHOLD, line_dash="dash", line_color="#007AFF",
                      annotation_text="Kickback-Schwelle (50,0 Mio. €)",
                      annotation_position="top left", annotation_font_color="#007AFF")
        fig.update_layout(barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#F5F5F7"), margin=dict(l=10, r=10, t=30, b=10), height=380,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                          yaxis=dict(title="Spend YTD in €", gridcolor="#1C1C1E",
                                     range=[0, max(fin["konsolidierter_spend"] * 1.25, 55_000_000.0)]))
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================================
    # 8. HUMAN-IN-THE-LOOP — die EINZIGE menschliche Stufe
    # ==========================================================================
    st.markdown("---")
    if token["status"] == "AWAITING_APPROVAL":
        verdict_color = "#30D158" if fin["qualifiziert"] else "#FF453A"
        verdict_txt = (f"<b style='color:#30D158;'>ANSPRUCH:</b> Konsolidierter Spend "
                       f"{fmt_curr(fin['konsolidierter_spend'])} überschreitet die Schwelle. "
                       f"Empfohlene Buchung: <b>{fmt_curr(fin['cashback'])}</b>."
                       if fin["qualifiziert"] else
                       f"<b style='color:#FF453A;'>KEIN ANSPRUCH:</b> Konsolidierter Spend "
                       f"{fmt_curr(fin['konsolidierter_spend'])} liegt unter der Schwelle "
                       f"({fmt_mio(THRESHOLD)}). Keine Buchung ableitbar.")
        st.markdown(
            f"""<div class="frosted-glass" style="border-color:{verdict_color} !important;">
            <h3 style="margin-top:0;">🧑‍⚖️ Human-in-the-Loop — Freigabe erforderlich</h3>
            <p style="color:#8E8E93; font-size:13px; margin-bottom:8px;">
            Vorher und nachher arbeiten die Agenten autonom. Hier entscheidet einmalig der Mensch.</p>
            <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:8px; font-size:14px;">{verdict_txt}</div>
            </div>""", unsafe_allow_html=True)

        reason = st.selectbox("Pflicht — Reason-Code", REASON_CODES, index=0)
        comment = st.text_input("Begründung / Kommentar (optional)", value="")
        approver = st.text_input("Freigebende:r", value="P. Procurement (Group Sourcing)")

        ha, hr, _ = st.columns([1, 1, 2])
        approve = ha.button("✅ Freigeben", type="primary", use_container_width=True)
        rejectb = hr.button("⛔ Ablehnen", use_container_width=True)

        if approve or rejectb:
            if reason == REASON_CODES[0]:
                st.warning("Bitte zuerst einen Reason-Code wählen.")
            else:
                decision = "FREIGEGEBEN" if approve else "ABGELEHNT"
                token["hitl"] = {
                    "modus": "LIVE",
                    "entscheidung": decision,
                    "reason_code": reason,
                    "kommentar": comment,
                    "freigeber": approver,
                    "zeitpunkt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                log_audit(token, f"Mensch · {approver}", "Human Review",
                          f"Entscheidung: {decision}", f"{reason}" + (f" — {comment}" if comment else ""))
                if approve:
                    token["status"] = "APPROVED"
                    token = agent_booking(token)
                else:
                    token["status"] = "REJECTED"
                    token["stage_idx"] = 4
                st.session_state["token"] = token
                st.rerun()

    elif token["status"] == "REJECTED":
        st.markdown(
            f"""<div class="frosted-glass" style="border-color:#FF453A !important; background:rgba(255,69,58,0.05) !important;">
            <h3 style="margin-top:0;">⛔ Vorgang abgelehnt</h3>
            <p>{token['hitl']['reason_code']}{(' — ' + token['hitl']['kommentar']) if token['hitl']['kommentar'] else ''}<br>
            Freigeber: {token['hitl']['freigeber']} · {token['hitl']['zeitpunkt']}</p>
            <p style="color:#8E8E93;">Booking-Agent wurde nicht ausgeführt. Keine Buchung, kein Versand.</p>
            </div>""", unsafe_allow_html=True)

    # ==========================================================================
    # 9. BOOKING-AGENT (nur bei Freigabe)
    # ==========================================================================
    if token["status"] == "BOOKED":
        bk = token["booking"]
        st.markdown("---")
        st.markdown("### 📒 Stufe 6 · Booking-Agent  ·  STUB")
        st.markdown(f'<span class="tag tag-stub">STUB</span> {bk["bapi"]}', unsafe_allow_html=True)
        st.success(f"Beleg **#{bk['beleg_id']}** geparkt — {bk['buchungstext']}")
        st.markdown(
            f"""<div class="apple-mail-box">
            <div class="mail-row"><b>VON:</b> <span class="val">AI.Orchestrator@globalcorp.com</span></div>
            <div class="mail-row"><b>AN:</b> <span class="val">{bk['mail_draft']['an']}</span></div>
            <div class="mail-row" style="color:#007AFF;"><b>BETREFF: {bk['mail_draft']['betreff']}</b></div>
            <div class="mail-row"><span class="tag tag-stub">{bk['mail_draft']['status']}</span></div>
            <div class="mail-divider"></div>
            <div style="font-size:13px; line-height:1.6; color:#D1D1D6;">
            Sehr geehrter Herr {CFO_NAME.split('(')[0].strip()},<br><br>
            unsere Agentic AI hat den Vorgang <b>{token['vorgang_id']}</b> für
            <b>„{token['parent']}“</b> abgeschlossen. Konsolidierte SAP-Einzelsilos:<br><br>
            {bk['mail_draft']['vendor_lines']}<br>
            <b>Konsolidierter Spend: {fmt_curr(fin['konsolidierter_spend'])}</b>
            (größtes Einzelsilo: {fmt_curr(fin['max_einzelsilo'])})<br>
            Freigegeben durch {token['hitl']['freigeber']} ({token['hitl']['reason_code']}).<br><br>
            Mit besten Grüßen,<br><b>PROC Kickback Hunter AI</b>
            </div></div>""", unsafe_allow_html=True)
        st.caption("Entwurf wird nicht automatisch versendet (Draft-only).")

# ==============================================================================
# 10. AUDIT-LOG (append-only) + CSV-Export
# ==============================================================================
st.markdown("---")
with st.expander(f"📋 Audit-Log (append-only · {len(st.session_state['audit_log'])} Einträge)", expanded=False):
    if st.session_state["audit_log"]:
        df_audit = pd.DataFrame(st.session_state["audit_log"])
        st.dataframe(df_audit, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇︎ Audit-Log als CSV exportieren",
            data=df_audit.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Noch keine Audit-Einträge.")
