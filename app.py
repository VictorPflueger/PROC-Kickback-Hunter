import time
import random
import pandas as pd
import streamlit as st

# ==============================================================================
# 0. PAGE CONFIG & APPLE CUPERTINO DARK MODE CSS
# ==============================================================================
st.set_page_config(
    page_title="PROC Kickback Hunter AI | GlobalCorp SE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_apple_cupertino_css():
    st.markdown("""
    <style>
        /* Apple Space Black Background */
        .stApp {
            background-color: #0A0A0C !important;
            color: #F5F5F7 !important;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif;
        }
        
        /* Frosted Glass Containers */
        .frosted-glass {
            background: rgba(28, 28, 30, 0.65) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45) !important;
        }

        /* SF-Blue Accent Buttons */
        div.stButton > button:first-child {
            background-color: #007AFF !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px !important;
            border: none !important;
            padding: 12px 24px !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:first-child:hover {
            background-color: #0062CC !important;
            transform: scale(1.01);
            box-shadow: 0 0 20px rgba(0, 122, 255, 0.4);
        }

        /* Search Input Styling */
        input[type="text"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            font-size: 15px !important;
        }
        input[type="text"]:focus {
            border-color: #007AFF !important;
            box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.3) !important;
        }

        /* LangGraph Apple-Style Pipeline Badges */
        .pipeline-track {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(18, 18, 20, 0.8);
            padding: 14px 20px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            margin-bottom: 20px;
            gap: 10px;
        }
        .agent-pill {
            flex: 1;
            text-align: center;
            padding: 10px 8px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.4);
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .agent-pill.active {
            color: #FFFFFF;
            background: rgba(0, 122, 255, 0.18);
            border-color: #007AFF;
            box-shadow: 0 0 18px rgba(0, 122, 255, 0.35);
            transform: translateY(-2px);
        }
        .agent-pill.done {
            color: #30D158;
            background: rgba(48, 209, 88, 0.12);
            border-color: #30D158;
        }

        /* Apple Terminal Simulation */
        .apple-terminal {
            background-color: #0E0E10;
            border-radius: 14px;
            border: 1px solid #222226;
            padding: 20px;
            font-family: 'SF Mono', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            color: #30D158;
            height: 260px;
            overflow-y: auto;
            box-shadow: inset 0 0 16px rgba(0,0,0,0.8);
        }
        .terminal-time { color: #8E8E93; font-size: 11px; margin-right: 8px; }
        .terminal-source { color: #007AFF; font-weight: bold; margin-right: 8px; }

        /* Metric Overrides */
        div[data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
        }
        
        /* Custom Tabs */
        button[data-baseweb="tab"] {
            background: transparent !important;
            color: #8E8E93 !important;
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #FFFFFF !important;
            border-bottom: 2px solid #007AFF !important;
        }
    </style>
    """, unsafe_allow_html=True)

inject_apple_cupertino_css()

def fmt_curr(val):
    """Formats float to German Enterprise Currency format: 1.048.000,00 €"""
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


# ==============================================================================
# 1. EPIC 1: MASSIVE DATA SCALING ENGINE (In-Memory Deterministic Generator)
# ==============================================================================
@st.cache_data
def generate_enterprise_sap_data():
    random.seed(1337) # Absolute Reproduzierbarkeit
    
    # --- A. DEFINITION DER KERN-KREDITOREN (Exakte mathematische Zielwerte) ---
    core_vendors = [
        # Epic 1.2: Cisco Cluster (Exakt 52.400.000,00 €)
        {"LIFNR": "10001", "NAME1": "Cisco Systems Germany GmbH", "ORT01": "Bonn", "LAND1": "DE", "STCD1": "DE123456780", "SPEND_YTD": 18200000.0},
        {"LIFNR": "10002", "NAME1": "Cisco Technology Inc.", "ORT01": "San Jose", "LAND1": "US", "STCD1": "US987654321", "SPEND_YTD": 14100000.0},
        {"LIFNR": "10003", "NAME1": "Meraki Cloud Networks Ltd.", "ORT01": "London", "LAND1": "GB", "STCD1": "GB554433221", "SPEND_YTD": 9500000.0},
        {"LIFNR": "10004", "NAME1": "Acacia Communications Opto", "ORT01": "Maynard", "LAND1": "US", "STCD1": "US112233445", "SPEND_YTD": 6200000.0},
        {"LIFNR": "10005", "NAME1": "Splunk Software EMEA", "ORT01": "Munich", "LAND1": "DE", "STCD1": "DE887766554", "SPEND_YTD": 4400000.0},
        
        # Epic 1.3: Die M&A Falle - Microsoft Cluster (Exakt 47.000.000,00 € -> verfehlt 50M)
        {"LIFNR": "20001", "NAME1": "Microsoft Deutschland GmbH", "ORT01": "Munich", "LAND1": "DE", "STCD1": "DE998877665", "SPEND_YTD": 41000000.0},
        {"LIFNR": "20002", "NAME1": "Activision Blizzard Germany", "ORT01": "Ismaning", "LAND1": "DE", "STCD1": "DE556677889", "SPEND_YTD": 6000000.0},
    ]

    # --- B. GENERIERUNG DES RAUSCHENS (Kreditoren 8 bis 150) ---
    stems = ["Logistics", "Facility", "Consulting", "MRO", "Packaging", "IT-Services", "Robotics", "Chemicals", "Security", "Fleet"]
    cities = ["Frankfurt", "Stuttgart", "Hamburg", "Berlin", "Düsseldorf", "Paris", "Zurich", "Vienna", "Milan", "Madrid", "Amsterdam"]
    prefixes = ["Apex", "Global", "Nova", "Sino", "Euro", "Chroma", "Stellar", "Vanguard", "Omni", "Inno"]
    
    filler_vendors = []
    for i in range(8, 151):
        spend = round(random.uniform(15000.0, 3800000.0), 2)
        filler_vendors.append({
            "LIFNR": f"{30000 + i}",
            "NAME1": f"{random.choice(prefixes)} {random.choice(stems)} {random.choice(['GmbH', 'AG', 'S.A.', 'Ltd'])}",
            "ORT01": random.choice(cities),
            "LAND1": random.choice(["DE", "FR", "CH", "AT", "IT", "ES", "NL"]),
            "STCD1": f"EU{random.randint(100000000, 999999999)}",
            "SPEND_YTD": spend
        })
    
    all_vendors_list = core_vendors + filler_vendors
    df_lfa1 = pd.DataFrame(all_vendors_list)

    # --- C. DETERMINISTISCHE EKKO-BESTELLBELEG-ZERLEGUNG (Exakt 1.200 Belege) ---
    # Verteilung der 1.200 Belege auf die 150 Kreditoren
    po_counts = {}
    po_counts["10001"] = 30  # Cisco Bonn
    po_counts["10002"] = 25  # Cisco San Jose
    po_counts["10003"] = 20  # Meraki
    po_counts["10004"] = 15  # Acacia
    po_counts["10005"] = 10  # Splunk
    po_counts["20001"] = 35  # Microsoft
    po_counts["20002"] = 15  # Activision
    
    # Bleiben exakt 1.050 Belege für die 143 Filler-Kreditoren
    for idx, v in enumerate(filler_vendors):
        po_counts[v["LIFNR"]] = 8 if idx < 49 else 7

    ekko_rows = []
    ebeln_base = 4500000001

    for v in all_vendors_list:
        lifnr = v["LIFNR"]
        target_sum = v["SPEND_YTD"]
        n_pos = po_counts[lifnr]
        
        target_cents = int(target_sum * 100)
        cutpoints = sorted([random.randint(1, target_cents - 1) for _ in range(n_pos - 1)])
        cutpoints = [0] + cutpoints + [target_cents]
        
        for k in range(len(cutpoints) - 1):
            val_cents = cutpoints[k+1] - cutpoints[k]
            netwr = val_cents / 100.0
            
            aedat = f"2026-{random.randint(1,5):02d}-{random.randint(1,28):02d}"
            
            ekko_rows.append({
                "EBELN": str(ebeln_base),
                "LIFNR": lifnr,
                "BUKRS": "1000",
                "AEDAT": aedat,
                "NETWR": netwr,
                "WAERS": "EUR"
            })
            ebeln_base += 1

    df_ekko = pd.DataFrame(ekko_rows)
    df_ekko = df_ekko.sample(frac=1, random_state=42).reset_index(drop=True)

    return df_lfa1, df_ekko

df_lfa1, df_ekko = generate_enterprise_sap_data()


# ==============================================================================
# HEADER & NAVIGATION
# ==============================================================================
st.markdown("""
<div class="frosted-glass" style="margin-bottom: 24px;">
    <h1 style="margin:0; font-size: 32px; font-weight: 800; letter-spacing: -1px;">
        PROC Kickback Hunter AI <span style="color:#007AFF; font-size: 20px;">v4.2 Enterprise</span>
    </h1>
    <p style="margin: 4px 0 0 0; color: #8E8E93; font-size: 15px;">
        Agentic Multi-Hop Entity Resolution & Automated Spend Consolidation for SAP ECC / S/4HANA
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🏛️ 1. SAP ERP Source Dump (LFA1/EKKO)", 
    "🧠 2. LangGraph Deep-Thought Orchestrator", 
    "💎 3. Financial Impact & Audit Proof"
])


# ==============================================================================
# TAB 1: EPIC 2 - LIVE VENDOR SEARCH & DATA DUMP
# ==============================================================================
with tab1:
    st.markdown("<h3 style='margin-bottom:16px;'>In-Memory Subsystem (150 Kreditoren, 1.200 Bestellbelege YTD)</h3>", unsafe_allow_html=True)
    
    search_str = st.text_input(
        "🔍 Kreditor suchen (Name, Ort oder LIFNR)...", 
        value="", 
        placeholder="Tippe 'Cisco', '10004', 'Munich' oder 'Activision'..."
    )
    
    if search_str.strip():
        query = search_str.strip()
        mask_lfa1 = (
            df_lfa1["NAME1"].str.contains(query, case=False, na=False) |
            df_lfa1["ORT01"].str.contains(query, case=False, na=False) |
            df_lfa1["LIFNR"].str.contains(query, case=False, na=False)
        )
        filtered_lfa1 = df_lfa1[mask_lfa1]
        matching_lifnrs = filtered_lfa1["LIFNR"].tolist()
        filtered_ekko = df_ekko[df_ekko["LIFNR"].isin(matching_lifnrs)]
    else:
        filtered_lfa1 = df_lfa1
        filtered_ekko = df_ekko

    col_lfa1, col_ekko = st.columns(2)
    
    with col_lfa1:
        st.markdown(f"**Kreditorenstamm (`SAP.LFA1`)** — Zeigt {len(filtered_lfa1)} von 150")
        st.dataframe(
            filtered_lfa1.style.format({"SPEND_YTD": "{:,.2f} €"}),
            use_container_width=True, height=450, hide_index=True
        )

    with col_ekko:
        st.markdown(f"**Bestellbelege YTD (`SAP.EKKO`)** — Zeigt {len(filtered_ekko)} von 1.200")
        st.dataframe(
            filtered_ekko.style.format({"NETWR": "{:,.2f} €"}),
            use_container_width=True, height=450, hide_index=True
        )


# ==============================================================================
# TAB 2: EPIC 3 - THE 30-SECOND LANGGRAPH ORCHESTRATOR
# ==============================================================================
def render_pipeline_badges(active_step):
    steps = [
        ("🕵️‍♂️", "1. ERP Ingestion"),
        ("🧬", "2. Fuzzy Matcher"),
        ("🌐", "3. Web Graph"),
        ("⚖️", "4. Legal RAG"),
        ("🧮", "5. Math Core")
    ]
    html = '<div class="pipeline-track">'
    for idx, (icon, label) in enumerate(steps, 1):
        status_class = ""
        if active_step == idx: status_class = "active"
        elif active_step > idx: status_class = "done"
        html += f'<div class="agent-pill {status_class}">{icon} {label}</div>'
    html += '</div>'
    return html

with tab2:
    st.markdown("<h3>Agentic Execution Pipeline (Durchlaufzeit: Programmatisch 30.0s)</h3>", unsafe_allow_html=True)
    
    badge_container = st.empty()
    terminal_container = st.empty()
    
    badge_container.markdown(render_pipeline_badges(0), unsafe_allow_html=True)
    terminal_container.markdown('<div class="apple-terminal"><span class="terminal-time">[00:00.0]</span> <span class="terminal-source">[SYSTEM]</span> Awaiting C-Level execution trigger...</div>', unsafe_allow_html=True)

    if st.button("🚀 EXECUTE LANGGRAPH VENDOR DEEP-SCAN", type="primary"):
        log_text = ""
        
        def push_term(t_str, src="LANGGRAPH", time_code="00:00"):
            global log_text  # <--- PATCHED (Scope fix)
            entry = f'<span class="terminal-time">[{time_code}]</span> <span class="terminal-source">[{src}]</span> {t_str}<br>'
            log_text += entry
            terminal_container.markdown(f'<div class="apple-terminal">{log_text}</div>', unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # PHASE 1 (0 bis 5 Sek): ERP Ingestion
        # ----------------------------------------------------------------------
        badge_container.markdown(render_pipeline_badges(1), unsafe_allow_html=True)
        push_term("Lese 150 Kreditoren und 1.200 Belege per RFC-BAPI in In-Memory Vektorraum...", "ERP-INGEST", "00:01")
        time.sleep(2.5)
        push_term("Speicher alloziert. Berechne initiale Kontokorrent-Salden...", "ERP-INGEST", "00:03")
        time.sleep(2.5)

        # ----------------------------------------------------------------------
        # PHASE 2 (5 bis 11 Sek): Fuzzy Matcher
        # ----------------------------------------------------------------------
        badge_container.markdown(render_pipeline_badges(2), unsafe_allow_html=True)
        push_term("Überführe Firmennamen & Adressen in n-dimensionale Levenshtein-Vektoren...", "FUZZY-SPACE", "00:06")
        time.sleep(2.0)
        push_term("Achtung: Hohe Namensähnlichkeit entdeckt: 'Cisco Systems Germany' & 'Cisco Technology Inc.' (Sim-Score: 0.94)", "FUZZY-SPACE", "00:08")
        time.sleep(2.0)
        push_term("Bilde vorläufigen Entitäts-Cluster #C-100 (Cisco Group)", "FUZZY-SPACE", "00:10")
        time.sleep(2.0)

        # ----------------------------------------------------------------------
        # PHASE 3 (11 bis 18 Sek): Web Graph / OSINT
        # ----------------------------------------------------------------------
        badge_container.markdown(render_pipeline_badges(3), unsafe_allow_html=True)
        push_term("Lese globale SEC Filings (Form 10-K) via Perplexity/Tavily API...", "OSINT-CRAWL", "00:12")
        time.sleep(2.5)
        push_term("M&A Nachweis gefunden: Cisco Systems übernimmt 'Acacia Communications' (März 2021) für $4.5B.", "OSINT-CRAWL", "00:14")
        time.sleep(2.5)
        push_term("M&A Nachweis gefunden: Cisco Systems übernimmt 'Splunk Inc.' (März 2024) für $28B. Füge LIFNR 10004 & 10005 zu Cluster #C-100 hinzu.", "OSINT-CRAWL", "00:16")
        time.sleep(2.0)

        # ----------------------------------------------------------------------
        # PHASE 4 (18 bis 24 Sek): Legal RAG
        # ----------------------------------------------------------------------
        badge_container.markdown(render_pipeline_badges(4), unsafe_allow_html=True)
        push_term("Vektorisiere 18 hinterlegte PDF-Rahmenverträge der GlobalCorp SE Einkaufsorganisation...", "LEGAL-RAG", "00:19")
        time.sleep(2.0)
        push_term("Treffer in Dokument 'CTR-2024-CISC-GLOBAL.pdf' (Klausel 8.2):", "LEGAL-RAG", "00:21")
        push_term("<i style='color:#fff;'>'The customer is entitled to a 2.00% annual retrospective spend rebate if total consolidated group spend across all affiliated entities exceeds €50,000,000.00.'</i>", "LEGAL-RAG", "00:22")
        time.sleep(2.0)

        # ----------------------------------------------------------------------
        # PHASE 5 (24 bis 30 Sek): Math Core / SymPy Auditor
        # ----------------------------------------------------------------------
        badge_container.markdown(render_pipeline_badges(5), unsafe_allow_html=True)
        push_term("Übergebe Cluster #C-100 an deterministische SymPy-Engine zur Prüfung der Bedingung...", "MATH-CORE", "00:25")
        time.sleep(2.0)
        push_term("Prüfe Cisco Cluster: Summe = 52.400.000,00 € ➔ Schwelle (50.0M) überschritten? <b>TRUE</b>", "MATH-CORE", "00:27")
        push_term("Prüfe Microsoft Cluster: Summe = 47.000.000,00 € ➔ Schwelle (50.0M) überschritten? <b style='color:#FF453A;'>FALSE</b> (Kein Cashback)", "MATH-CORE", "00:28")
        time.sleep(2.0)
        push_term("Generiere BAPI-Buchungs-Payload für SAP FI-CA... Done.", "MATH-CORE", "00:30")
        
        # ----------------------------------------------------------------------
        # SEKUNDE 30: FINISH
        # ----------------------------------------------------------------------
        badge_container.markdown(render_pipeline_badges(6), unsafe_allow_html=True)
        st.balloons()
        st.success("✅ **DEEP-SCAN ABGESCHLOSSEN.** Mathematischer Beweis gesichert. Bitte wechseln Sie in Reiter 3 (Financial Impact).")


# ==============================================================================
# TAB 3: FINANCIAL IMPACT & THE AUDITOR PROOF (C-Level Summary)
# ==============================================================================
with tab3:
    st.markdown("<h3>Executive Financial Summary & Audit-Nachweise</h3>", unsafe_allow_html=True)
    
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)
    with kcol1:
        st.metric("Silo SQL-Skript Kickback", "0,00 €", "Standard SAP Report")
    with kcol2:
        st.metric("Konsolidierter Cisco Spend", "52.400.000,00 €", "+2.4M € über Schwelle")
    with kcol3:
        st.metric("Identifizierter Cashback", "1.048.000,00 €", "2.0% vertraglicher Kickback")
    with kcol4:
        st.metric("EBITDA Impact YTD", "+ 1.048.000 €", "Sofort wirksam", delta_color="normal")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 24px 0;'>", unsafe_allow_html=True)

    col_cisco, col_msft = st.columns(2)

    with col_cisco:
        st.markdown("""
        <div class="frosted-glass">
            <h4 style="margin-top:0; color: #007AFF;">🟢 ENTITY CLUSTER #1: Cisco Systems Group</h4>
            <p style="color:#8E8E93; font-size: 13px;">Durch Multi-Hop Reasoning konsolidierte SAP-Kreditoren</p>
        </div>
        """, unsafe_allow_html=True)
        
        cisco_df = df_lfa1[df_lfa1["LIFNR"].isin(["10001", "10002", "10003", "10004", "10005"])]
        st.dataframe(
            cisco_df[["LIFNR", "NAME1", "ORT01", "SPEND_YTD"]].style.format({"SPEND_YTD": "{:,.2f} €"}),
            use_container_width=True, hide_index=True
        )
        
        st.markdown("""
        <div style="background: rgba(48, 209, 88, 0.1); border: 1px solid #30D158; padding: 12px; border-radius: 10px; margin-top: 12px;">
            <b style="color:#30D158;">Ergebnis:</b> 52,40 Mio. € Spend > 50,00 Mio. € Schwelle ➔ <b>Anspruch auf 1.048.000,00 € Rückvergütung verifiziert.</b>
        </div>
        """, unsafe_allow_html=True)

    with col_msft:
        st.markdown("""
        <div class="frosted-glass">
            <h4 style="margin-top:0; color: #FF453A;">🛡️ AUDITOR PROOF: Die Microsoft M&A-Falle</h4>
            <p style="color:#8E8E93; font-size: 13px;">Beweis der mathematischen und logischen Integrität der KI</p>
        </div>
        """, unsafe_allow_html=True)

        msft_df = df_lfa1[df_lfa1["LIFNR"].isin(["20001", "20002"])]
        st.dataframe(
            msft_df[["LIFNR", "NAME1", "ORT01", "SPEND_YTD"]].style.format({"SPEND_YTD": "{:,.2f} €"}),
            use_container_width=True, hide_index=True
        )

        st.markdown("""
        <div style="background: rgba(255, 69, 58, 0.1); border: 1px solid #FF453A; padding: 12px; border-radius: 10px; margin-top: 12px; font-size: 14px;">
            <b style="color:#FF453A;">Audit-Logik intakt:</b> Die Agentic AI hat die Akquisition von Activision Blizzard durch Microsoft korrekt erkannt (Konsolidierter Spend: <b>47,00 Mio. €</b>). Da die vertragliche Kickback-Schwelle von 50,00 Mio. € jedoch um exakt 3,00 Mio. € verfehlt wurde, hat die KI <b>keinen falschen Anspruch</b> ausgelöst.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    if st.button("⚡ BAPI: Debitoren-Sollstellung im SAP erzeugen (Transaktion FB01 / BAPI_ACC_DOCUMENT_POST)", type="primary"):
        st.toast("BAPI_ACC_DOCUMENT_POST erfolgreich an SAP S/4HANA (Instanz P01) abgesetzt!", icon="🚀")
        st.success("Buchungsbeleg **#109482001** (Debitor Cisco Systems an Erlöse aus Rückvergütungen: 1.048.000,00 €) im SAP erzeugt.")