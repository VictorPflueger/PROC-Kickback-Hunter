import time
import random
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
            background-color: rgba(255, 255, 255, 0.07) !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
        }
        input[type="text"]:focus {
            border-color: #007AFF !important;
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.3) !important;
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

        /* Apple Mail Mockup Box */
        .apple-mail-box {
            background-color: #161618;
            border: 1px solid #2C2C30;
            border-radius: 14px;
            padding: 24px;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        }
        .mail-row { margin-bottom: 6px; font-size: 13px; color: #8E8E93; }
        .mail-row span.val { color: #FFFFFF; font-weight: 500; }
        .mail-divider { border-top: 1px solid #2C2C30; margin: 16px 0; }

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
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


# ==============================================================================
# 1. EPIC 1: MASSIVE DATA SCALING ENGINE (In-Memory Deterministic Generator)
# ==============================================================================
@st.cache_data
def generate_enterprise_sap_data():
    random.seed(1337)
    
    core_vendors = [
        {"LIFNR": "10001", "NAME1": "Cisco Systems Germany GmbH", "ORT01": "Bonn", "LAND1": "DE", "STCD1": "DE123456780", "SPEND_YTD": 18200000.0},
        {"LIFNR": "10002", "NAME1": "Cisco Technology Inc.", "ORT01": "San Jose", "LAND1": "US", "STCD1": "US987654321", "SPEND_YTD": 14100000.0},
        {"LIFNR": "10003", "NAME1": "Meraki Cloud Networks Ltd.", "ORT01": "London", "LAND1": "GB", "STCD1": "GB554433221", "SPEND_YTD": 9500000.0},
        {"LIFNR": "10004", "NAME1": "Acacia Communications Opto", "ORT01": "Maynard", "LAND1": "US", "STCD1": "US112233445", "SPEND_YTD": 6200000.0},
        {"LIFNR": "10005", "NAME1": "Splunk Software EMEA", "ORT01": "Munich", "LAND1": "DE", "STCD1": "DE887766554", "SPEND_YTD": 4400000.0},
        
        {"LIFNR": "20001", "NAME1": "Microsoft Deutschland GmbH", "ORT01": "Munich", "LAND1": "DE", "STCD1": "DE998877665", "SPEND_YTD": 41000000.0},
        {"LIFNR": "20002", "NAME1": "Activision Blizzard Germany", "ORT01": "Ismaning", "LAND1": "DE", "STCD1": "DE556677889", "SPEND_YTD": 6000000.0},
    ]

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

    po_counts = {
        "10001": 30, "10002": 25, "10003": 20, "10004": 15, "10005": 10,
        "20001": 35, "20002": 15
    }
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
                "EBELN": str(ebeln_base), "LIFNR": lifnr, "BUKRS": "1000",
                "AEDAT": aedat, "NETWR": netwr, "WAERS": "EUR"
            })
            ebeln_base += 1

    df_ekko = pd.DataFrame(ekko_rows).sample(frac=1, random_state=42).reset_index(drop=True)
    return df_lfa1, df_ekko

df_lfa1, df_ekko = generate_enterprise_sap_data()


# ==============================================================================
# HEADER & MASTER SEARCH BAR (The Single Source of Truth for all 4 Tabs)
# ==============================================================================
st.markdown("""
<div class="frosted-glass" style="margin-bottom: 16px;">
    <h1 style="margin:0; font-size: 32px; font-weight: 800; letter-spacing: -1px;">
        PROC Kickback Hunter AI <span style="color:#007AFF; font-size: 20px;">v4.5 Enterprise Engine</span>
    </h1>
    <p style="margin: 4px 0 0 0; color: #8E8E93; font-size: 15px;">
        Fully Reactive Entity Resolution across all Views — No hardcoded limits
    </p>
</div>
""", unsafe_allow_html=True)

raw_search = st.text_input(
    "🔍 GLOBALE KREDITOR- & ENTITÄTSSUCHE (Steuert in Echtzeit Tab 1, Tab 2, Tab 3 und Tab 4)...", 
    value="", 
    placeholder="Tippe z.B. 'Cisco', 'Microsoft', 'Nova', 'Munich' oder eine LIFNR..."
).strip()


# --- THE REACTIVE CORE: RESOLVING "df_focus" ---
if raw_search:
    q_lower = raw_search.lower()
    mask = (
        df_lfa1["NAME1"].str.lower().str.contains(q_lower, na=False) |
        df_lfa1["ORT01"].str.lower().str.contains(q_lower, na=False) |
        df_lfa1["LIFNR"].str.lower().str.contains(q_lower, na=False)
    )
    df_focus = df_lfa1[mask]
    focus_title = f"Suchergebnis: „{raw_search}“"
else:
    # Default Showcase Mode, wenn die Suchleiste leer ist
    df_focus = df_lfa1[df_lfa1["LIFNR"].isin(["10001", "10002", "10003", "10004", "10005"])]
    focus_title = "Cisco Systems Group (Default Showcase Cluster)"

# Mathematische Live-Auswertung des aktuellen df_focus
focus_true_spend = df_focus["SPEND_YTD"].sum() if len(df_focus) > 0 else 0.0
focus_silo_max = df_focus["SPEND_YTD"].max() if len(df_focus) > 0 else 0.0
focus_delta = focus_true_spend - focus_silo_max

THRESHOLD = 50000000.0
is_qualified = focus_true_spend >= THRESHOLD
focus_cashback = focus_true_spend * 0.02 if is_qualified else 0.0

# Hilfslisten für dynamische Strings
focus_names_list = df_focus["NAME1"].tolist()
first_vendor_name = focus_names_list[0] if len(focus_names_list) > 0 else "Unbekannte Entität"


# NAVIGATION TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ 1. SAP ERP Dump", 
    "🧠 2. LangGraph Deep-Thought", 
    "💎 3. Financial Impact",
    "📈 4. Management Summary & E-Mail"
])


# ==============================================================================
# TAB 1: SOURCE DUMP (Reagiert live)
# ==============================================================================
with tab1:
    # In Tab 1 zeigen wir bei leerer Suche ALLE 150 an, bei aktiver Suche nur die Treffer
    display_lfa1 = df_focus if raw_search else df_lfa1
    display_ekko = df_ekko[df_ekko["LIFNR"].isin(display_lfa1["LIFNR"].tolist())]
    
    st.markdown(f"<h3 style='margin-bottom:16px;'>In-Memory Subsystem (Angezeigt: {len(display_lfa1)} Kreditoren)</h3>", unsafe_allow_html=True)
    col_lfa1, col_ekko = st.columns(2)
    
    with col_lfa1:
        st.markdown("**Kreditorenstamm (`SAP.LFA1`)**")
        st.dataframe(display_lfa1.style.format({"SPEND_YTD": "{:,.2f} €"}), use_container_width=True, height=450, hide_index=True)

    with col_ekko:
        st.markdown("**Bestellbelege YTD (`SAP.EKKO`)**")
        st.dataframe(display_ekko.style.format({"NETWR": "{:,.2f} €"}), use_container_width=True, height=450, hide_index=True)


# ==============================================================================
# TAB 2: LANGGRAPH DEEP-THOUGHT ORCHESTRATOR (Reagiert dynamisch auf Namen!)
# ==============================================================================
def render_pipeline_badges(active_step):
    steps = [("🕵️‍♂️", "1. ERP Ingest"), ("🧬", "2. Fuzzy Match"), ("🌐", "3. Web Graph"), ("⚖️", "4. Legal RAG"), ("🧮", "5. Math Core")]
    html = '<div class="pipeline-track">'
    for idx, (icon, label) in enumerate(steps, 1):
        status = "active" if active_step == idx else ("done" if active_step > idx else "")
        html += f'<div class="agent-pill {status}">{icon} {label}</div>'
    return html + '</div>'

with tab2:
    st.markdown(f"<h3>Agentic Scan Target: <span style='color:#007AFF;'>{focus_title}</span> (30.0s Choreografie)</h3>", unsafe_allow_html=True)
    
    badge_container = st.empty()
    terminal_container = st.empty()
    
    badge_container.markdown(render_pipeline_badges(0), unsafe_allow_html=True)
    terminal_container.markdown(f'<div class="apple-terminal"><span class="terminal-time">[00:00.0]</span> <span class="terminal-source">[SYSTEM]</span> Bereit für Deep-Scan von {len(df_focus)} Entitäten...</div>', unsafe_allow_html=True)

    if st.button("🚀 EXECUTE DYNAMIC VENDOR DEEP-SCAN", type="primary"):
        log_text = ""
        def push_term(t_str, src="LANGGRAPH", time_code="00:00"):
            global log_text
            log_text += f'<span class="terminal-time">[{time_code}]</span> <span class="terminal-source">[{src}]</span> {t_str}<br>'
            terminal_container.markdown(f'<div class="apple-terminal">{log_text}</div>', unsafe_allow_html=True)

        # Phase 1
        badge_container.markdown(render_pipeline_badges(1), unsafe_allow_html=True)
        push_term(f"Lese {len(df_focus)} verknüpfte Kreditorenkonten per RFC-BAPI in In-Memory Vektorraum...", "ERP-INGEST", "00:01")
        time.sleep(3.0)
        push_term(f"Fokussiere Graphen-Traversierung auf Entität: '<b>{first_vendor_name}</b>' und zugehörige Schlüssel.", "ERP-INGEST", "00:04")
        time.sleep(2.0)

        # Phase 2
        badge_container.markdown(render_pipeline_badges(2), unsafe_allow_html=True)
        push_term("Fuzzy-Space: Transformiere Adress- & Namensfelder in Levenshtein-Matrizen...", "FUZZY-CORE", "00:07")
        time.sleep(3.0)
        if len(focus_names_list) > 1:
            push_term(f"Semantische Nähe entdeckt zwischen '{first_vendor_name}' und '{focus_names_list[1]}'.", "FUZZY-CORE", "00:10")
        else:
            push_term(f"Einzel-Entität '{first_vendor_name}' verifiziert. Prüfe auf versteckte Tochtergesellschaften...", "FUZZY-CORE", "00:10")
        time.sleep(1.0)

        # Phase 3
        badge_container.markdown(render_pipeline_badges(3), unsafe_allow_html=True)
        push_term("Frage globale Handelsregister & SEC-Filings (Form 10-K) via OSINT-Agent ab...", "WEB-GRAPH", "00:12")
        time.sleep(3.0)
        push_term(f"Graph-Synthese: Bestätige wirtschaftliche Zugehörigkeit von {len(df_focus)} Datensätzen zum Cluster '{focus_title}'.", "WEB-GRAPH", "00:15")
        time.sleep(3.0)

        # Phase 4
        badge_container.markdown(render_pipeline_badges(4), unsafe_allow_html=True)
        push_term("Vektorisiere hinterlegte PDF-Rahmenverträge der Einkaufsorganisation...", "LEGAL-RAG", "00:19")
        time.sleep(3.0)
        push_term("<i style='color:#fff;'>Extrahierte Klausel: '2.0% Kickback auf den konsolidierten Gesamtumsatz ab exakt 50.000.000,00 € Spend.'</i>", "LEGAL-RAG", "00:23")
        time.sleep(1.0)

        # Phase 5
        badge_container.markdown(render_pipeline_badges(5), unsafe_allow_html=True)
        push_term(f"Übergebe Spend-Vektor an SymPy... Berechne True Spend: {fmt_curr(focus_true_spend)}", "MATH-ENGINE", "00:25")
        time.sleep(2.0)
        
        hit_label = "<b>TRUE</b> (Anspruch verifiziert!)" if is_qualified else "<b style='color:#FF453A;'>FALSE</b> (Schwelle nicht erreicht)"
        push_term(f"Prüfe Bedingung ({fmt_curr(focus_true_spend)} >= 50.0M €) ➔ {hit_label}", "MATH-ENGINE", "00:27")
        time.sleep(2.0)
        
        if is_qualified:
            push_term(f"Erzeuge BAPI-Payload für Debitorenbuchung über {fmt_curr(focus_cashback)}... Done.", "SYSTEM", "00:30")
        else:
            push_term("Audit beendet. Keine Rückvergütung ableitbar. Keine Buchung ausgelöst.", "SYSTEM", "00:30")
        
        badge_container.markdown(render_pipeline_badges(6), unsafe_allow_html=True)
        st.balloons() if is_qualified else None
        st.success(f"✅ **SCAN ABGESCHLOSSEN.** Ergebnis für {focus_title} gesichert.")


# ==============================================================================
# TAB 3: FINANCIAL IMPACT (100% Live berechnet aus df_focus!)
# ==============================================================================
with tab3:
    st.markdown("<h3>Executive Financial Impact & Entity Card</h3>", unsafe_allow_html=True)
    
    # 100% Dynamische KPIs! Nichts ist mehr fest einprogrammiert!
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Max. SAP-Einzelsilo", fmt_curr(focus_silo_max), "Größter Kreditor im Silo")
    with k2: st.metric("AI Konsolidierter Spend", fmt_curr(focus_true_spend), f"+{fmt_curr(focus_delta)} durch AI")
    
    stat_lbl = "QUALIFIZIERT (2%)" if is_qualified else "NICHT ERREICHT"
    stat_col = "normal" if is_qualified else "off"
    with k3: st.metric("Vertrags-Kickback Status", stat_lbl, "Schwelle: 50.0M €", delta_color=stat_col)
    with k4: st.metric("EBITDA Cashback", fmt_curr(focus_cashback), "Sofort wirksam")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 24px 0;'>", unsafe_allow_html=True)

    # Die eine, perfekt angepasste Audit-Karte
    card_border = "#30D158" if is_qualified else "#FF453A"
    card_bg = "rgba(48, 209, 88, 0.05)" if is_qualified else "rgba(255, 69, 58, 0.05)"
    badge_icon = "🟢" if is_qualified else "🔴"
    verdict_text = f"<b style='color:#30D158;'>Erfolg:</b> Spend übersteigt 50M-Schwelle. Anspruch auf <b>{fmt_curr(focus_cashback)}</b> verifiziert." if is_qualified else f"<b style='color:#FF453A;'>Abgelehnt:</b> Der konsolidierte Umsatz von {fmt_curr(focus_true_spend)} verfehlt die vertragliche 50M-Schwelle."

    st.markdown(f"""
    <div class="frosted-glass" style="border-color: {card_border} !important; background: {card_bg} !important;">
        <h4 style="margin-top:0; color: #FFFFFF;">{badge_icon} AUDIT REPORT: {focus_title}</h4>
        <p style="color:#8E8E93; font-size: 14px;">Die KI hat die untenstehenden {len(df_focus)} SAP-Kreditorenkonten als wirtschaftliche Entität zusammengefasst.</p>
        <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 14px;">
            {verdict_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    st.dataframe(df_focus[["LIFNR", "NAME1", "ORT01", "LAND1", "SPEND_YTD"]].style.format({"SPEND_YTD": "{:,.2f} €"}), use_container_width=True, hide_index=True)

    if is_qualified:
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button(f"⚡ BAPI: Debitoren-Sollstellung über {fmt_curr(focus_cashback)} im SAP buchen (FB01)", type="primary"):
            st.toast("BAPI_ACC_DOCUMENT_POST erfolgreich abgesetzt!", icon="🚀")
            st.success(f"Buchungsbeleg **#109482001** (Debitor an Erlöse aus Rückvergütungen: {fmt_curr(focus_cashback)}) im SAP S/4HANA erzeugt.")


# ==============================================================================
# TAB 4: MANAGEMENT SUMMARY CHART & AUTOMATED EMAIL DISPATCHER
# ==============================================================================
with tab4:
    st.markdown("<h3>Executive Board Visualizer & Automated Dispatch</h3>", unsafe_allow_html=True)
    
    col_graph, col_mail = st.columns([1.1, 0.9])

    with col_graph:
        st.markdown(f"**Spend-Konsolidierung: {focus_title}**")
        
        fig = go.Figure()

        # Balken 1: Das alte SAP Silo
        fig.add_trace(go.Bar(
            name="Max. SAP Einzelsilo", x=[focus_title], y=[focus_silo_max],
            marker_color="#3A3A3C", text=[fmt_curr(focus_silo_max)], textposition="auto"
        ))
        
        # Balken 2: Die Wahrheit durch die KI
        bar_color = "#30D158" if is_qualified else "#FF453A"
        fig.add_trace(go.Bar(
            name="AI Konsolidiert (True Spend)", x=[focus_title], y=[focus_true_spend],
            marker_color=bar_color, text=[fmt_curr(focus_true_spend)], textposition="outside"
        ))

        fig.add_hline(
            y=THRESHOLD, line_dash="dash", line_color="#007AFF",
            annotation_text="Kickback-Schwelle (50.0 Mio. €)", 
            annotation_position="top left", annotation_font_color="#007AFF"
        )

        y_max_scale = max(focus_true_spend * 1.25, 55000000.0)

        fig.update_layout(
            barmode='group', plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F5F5F7"), margin=dict(l=10, r=10, t=30, b=10), height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Spend YTD in €", gridcolor="#1C1C1E", zerolinecolor="#1C1C1E", range=[0, y_max_scale])
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_mail:
        st.markdown("**Automatisierter C-Level Dispatch (E-Mail)**")
        
        # Kreditorenliste formatiert für die Mail
        mail_vendors = "".join([f"• {row['LIFNR']}: {row['NAME1']} ({row['ORT01']}) — {fmt_curr(row['SPEND_YTD'])}<br>" for _, row in df_focus.iterrows()])
        
        if is_qualified:
            m_subj = f"[CASHBACK SECURED] +{fmt_curr(focus_cashback)} für {focus_title}"
            m_body_stat = f"<span style='color:#30D158;'><b>ANSPRUCH BESTÄTIGT:</b> Der konsolidierte True-Spend von {fmt_curr(focus_true_spend)} überschreitet die 50M-Vertragsschwelle. Wir buchen {fmt_curr(focus_cashback)} als Ertrag ein.</span>"
        else:
            m_subj = f"[AUDIT REPORT] Compliance-Prüfung für {focus_title}"
            m_body_stat = f"<span style='color:#FF453A;'><b>KEIN ANSPRUCH:</b> Der konsolidierte True-Spend von {fmt_curr(focus_true_spend)} liegt unter der 50M-Vertragsschwelle. Logik-Integrität intakt.</span>"

        mail_html = f"""
        <div class="apple-mail-box">
            <div class="mail-row"><b>VON:</b> <span class="val">AI.Orchestrator@globalcorp.com</span></div>
            <div class="mail-row"><b>AN:</b> <span class="val">Dr. Henrik von Bohlen (CFO)</span></div>
            <div class="mail-row" style="margin-top: 8px; color:#007AFF;"><b>BETREFF: {m_subj}</b></div>
            <div class="mail-divider"></div>
            <div style="font-size: 13px; line-height: 1.6; color: #D1D1D6;">
                Sehr geehrter Herr Dr. von Bohlen,<br><br>
                unsere Agentic AI hat den Scan für <b>„{focus_title}“</b> abgeschlossen. 
                Folgende SAP-Einzelsilos wurden erfolgreich konsolidiert:<br><br>
                {mail_vendors}<br>
                <b>Konsolidierter True-Spend: {fmt_curr(focus_true_spend)}</b> (Maximales Einzelsilo lag bei nur {fmt_curr(focus_silo_max)})<br><br>
                <b>FAZIT DER PRÜFUNG:</b><br>
                {m_body_stat}<br><br>
                Mit besten Grüßen,<br><b>PROC Kickback Hunter AI</b>
            </div>
        </div>
        """
        st.markdown(mail_html, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        if st.button("✉️ E-Mail sofort über internes Relay an CFO versenden", type="primary"):
            st.balloons() if is_qualified else None
            st.success("E-Mail wurde kryptografisch signiert und im Postausgang hinterlegt.")
