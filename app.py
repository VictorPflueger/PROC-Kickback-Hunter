"""
================================================================================
PROTOTYP: AGENTIC AI IM SPEND MANAGEMENT (DTAG PROCUREMENT)
================================================================================
Business Case: "The Ultimate Parent Kickback Hunter" (Cisco Global)
Architektur: Streamlit Frontend <-> In-Memory Pandas SAP-Mock <-> Cognitive Agent
================================================================================
"""

import time
import datetime
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & TELEKOM CORPORATE DESIGN (CSS)
# ==============================================================================
st.set_page_config(
    page_title="DTAG Procurement AI | Kickback Hunter",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injektion von Telekom-spezifischem CSS (Magenta #E20074, scharfe Kontraste)
st.markdown("""
    <style>
        :root {
            --magenta: #E20074;
            --magenta-hover: #b3005b;
        }
        /* Primary Buttons in Telekom Magenta */
        div.stButton > button[kind="primary"] {
            background-color: #E20074 !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 4px !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #b3005b !important;
            box-shadow: 0 4px 8px rgba(226, 0, 116, 0.3);
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #f4f4f4;
            border-right: 1px solid #e0e0e0;
        }
        /* Custom Highlight Card */
        .cash-claim-card {
            background: linear-gradient(135deg, #fff 0%, #fcf0f5 100%);
            border-left: 6px solid #E20074;
            padding: 1.5rem;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .cash-title { color: #555; font-size: 0.9rem; text-transform: uppercase; font-weight: 600; margin:0;}
        .cash-amount { color: #E20074; font-size: 2.8rem; font-weight: 900; margin: 0; line-height: 1.2;}
        /* Terminal Styling */
        .agent-terminal {
            font-family: 'Courier New', Courier, monospace;
            background-color: #1e1e1e;
            color: #00ff66;
            padding: 1.2rem;
            border-radius: 4px;
            height: 380px;
            overflow-y: auto;
            border: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DUMMY DATA GENERATOR (SAP TABELLENSCHEMA)
# ==============================================================================
@st.cache_data
def generate_sap_database():
    """Generiert den syntaktisch korrekten SAP-Datensatz beim ersten Start."""
    
    # --------------------------------------------------------------------------
    # TABELLE 1: LFA1 (Lieferantenstamm)
    # --------------------------------------------------------------------------
    lfa1_records = [
        # Die 5 Cisco Easter-Eggs
        {"LIFNR": "10001", "NAME1": "Cisco Systems GmbH", "ORT01": "Bonn", "LAND1": "DE", "STCD1": "DE123456789"},
        {"LIFNR": "10002", "NAME1": "CISCO SYSTEMS INC", "ORT01": "San Jose", "LAND1": "US", "STCD1": "US987654321"},
        {"LIFNR": "10003", "NAME1": "Cisco Meraki UK Ltd", "ORT01": "London", "LAND1": "GB", "STCD1": "GB555666777"},
        {"LIFNR": "10004", "NAME1": "Acacia Communications Ireland", "ORT01": "Cork", "LAND1": "IE", "STCD1": "IE112233445"}, # Acquired 2021
        {"LIFNR": "10005", "NAME1": "Splunk Services Germany", "ORT01": "München", "LAND1": "DE", "STCD1": "DE998877665"},     # Acquired 2024
        # Rauschen: Top Spender (bewusst so platziert, dass Cisco Bonn auf Platz 4 landet)
        {"LIFNR": "10006", "NAME1": "Microsoft Deutschland GmbH", "ORT01": "München", "LAND1": "DE", "STCD1": "DE811111111"},
        {"LIFNR": "10007", "NAME1": "Dell GmbH", "ORT01": "Frankfurt am Main", "LAND1": "DE", "STCD1": "DE822222222"},
        {"LIFNR": "10008", "NAME1": "Bechtle AG", "ORT01": "Neckarsulm", "LAND1": "DE", "STCD1": "DE833333333"},
        {"LIFNR": "10009", "NAME1": "CANCOM SE", "ORT01": "München", "LAND1": "DE", "STCD1": "DE844444444"},
        {"LIFNR": "10010", "NAME1": "IBM Deutschland GmbH", "ORT01": "Ehningen", "LAND1": "DE", "STCD1": "DE855555555"},
    ]
    
    # Restliches Rauschen auf 40 Lieferanten auffüllen
    filler_names = [
        "Huawei Technologies Dtl", "Oracle Deutschland B.V.", "SAP SE", "Accenture GmbH", 
        "Capgemini Deutschland", "Infosys Limited", "TCS Deutschland", "Atos Information Tech", 
        "Tiefbau Rhein-Ruhr GmbH", "Kabel-Schmidt Netztechnik", "Elektro Huber & Söhne", 
        "Gartner Deutschland", "PwC Strategy&", "Ernst & Young GmbH", "KPMG AG Wirtschaftsprüfungsges.", 
        "Deloitte Consulting", "SoftwareOne Deutschland", "Computacenter AG", "SHI International", 
        "NTT Data Deutschland", "Wipro Limited", "Cognizant Technology", "HCL Technologies", 
        "Fujitsu Technology Sol.", "Lenovo Global Tech", "HP Inc. Dtl.", "Juniper Networks", 
        "Arista Networks", "Palo Alto Networks", "Fortinet GmbH"
    ]
    for idx, name in enumerate(filler_names, start=10011):
        lfa1_records.append({
            "LIFNR": str(idx), "NAME1": name, 
            "ORT01": "Berlin" if idx % 2 == 0 else "Düsseldorf", 
            "LAND1": "DE", "STCD1": f"DE{idx}9900"
        })
    lfa1_df = pd.DataFrame(lfa1_records)

    # --------------------------------------------------------------------------
    # TABELLE 2: EKKO (Einkaufsbelegköpfe / Spend YTD)
    # --------------------------------------------------------------------------
    # ZIEL: Summe der 5 Cisco-Kreditoren muss EXAKT 52.400.000 € ergeben.
    ekko_records = [
        {"EBELN": "4500010001", "BUKRS": "1000", "LIFNR": "10001", "NETWR": 14000000.00}, # Cisco Bonn (1)
        {"EBELN": "4500010002", "BUKRS": "1020", "LIFNR": "10001", "NETWR": 8000000.00},  # Cisco Bonn (2) -> Summe Bonn: 22M
        {"EBELN": "4500010003", "BUKRS": "1000", "LIFNR": "10002", "NETWR": 4000000.00},  # Cisco San Jose: 4M
        {"EBELN": "4500010004", "BUKRS": "1040", "LIFNR": "10003", "NETWR": 10000000.00}, # Meraki London: 10M
        {"EBELN": "4500010005", "BUKRS": "1020", "LIFNR": "10004", "NETWR": 9000000.00},  # Acacia Ireland: 9M
        {"EBELN": "4500010006", "BUKRS": "1000", "LIFNR": "10005", "NETWR": 7400000.00},  # Splunk Munich: 7.4M
        # Top 3 Silo-Spender der Telekom (damit Cisco Bonn auf Platz 4 rutscht)
        {"EBELN": "4500010007", "BUKRS": "1000", "LIFNR": "10006", "NETWR": 26500000.00}, # Microsoft (~26.5M)
        {"EBELN": "4500010008", "BUKRS": "1000", "LIFNR": "10007", "NETWR": 24800000.00}, # Dell (~24.8M)
        {"EBELN": "4500010009", "BUKRS": "1020", "LIFNR": "10008", "NETWR": 23100000.00}, # Bechtle (~23.1M)
    ]
    
    # Zufällige Bestellungen für die restlichen Lieferanten generieren (~240 Datensätze)
    np.random.seed(42)
    other_vendors = [v for v in lfa1_df['LIFNR'].tolist() if v not in ["10001", "10002", "10003", "10004", "10005", "10006", "10007", "10008"]]
    
    for po_id in range(10, 251):
        v_id = np.random.choice(other_vendors)
        val = round(np.random.uniform(15000, 380000), 2)
        buk = np.random.choice(["1000", "1020", "1040"], p=[0.65, 0.25, 0.10]) # 1000=Telekom, 1020=T-Systems, 1040=Congstar
        ekko_records.append({
            "EBELN": f"45000{po_id:05d}",
            "BUKRS": buk,
            "LIFNR": v_id,
            "NETWR": val
        })
    ekko_df = pd.DataFrame(ekko_records)

    # --------------------------------------------------------------------------
    # TABELLE 3: Z_CONTRACTS (Simulierte Vertragsdatenbank / RAG Source)
    # --------------------------------------------------------------------------
    contracts_records = [
        {
            "VERTRAG_ID": "CTR-2024-CISC",
            "KREDITOR_NAME": "Cisco Global",
            "KICKBACK_SCHWELLE_EUR": 50000000.0,
            "KICKBACK_PROZENT": 2.0,
            "KLAUSEL_TEXT": "Der Auftragnehmer gewährt der DTAG eine gruppenweite Rückvergütung von 2.0% auf den kumulierten Netto-Jahresumsatz aller verbundenen Unternehmen im Sinne des § 15 AktG, sobald der Gruppenumsatz 50,0 Mio. EUR übersteigt."
        },
        {
            "VERTRAG_ID": "CTR-2023-MSFT",
            "KREDITOR_NAME": "Microsoft Corporation",
            "KICKBACK_SCHWELLE_EUR": 100000000.0,
            "KICKBACK_PROZENT": 1.5,
            "KLAUSEL_TEXT": "Ab einem erreichten Gruppenumsatz von 100 Mio. EUR greift die automatische Tier-2 Kickback-Staffel."
        }
    ]
    contracts_df = pd.DataFrame(contracts_records)

    return lfa1_df, ekko_df, contracts_df


# Datenbank initialisieren
LFA1, EKKO, Z_CONTRACTS = generate_sap_database()

# Session State für UI-Steuerung initialisieren
if "scan_executed" not in st.session_state:
    st.session_state.scan_executed = False
if "booking_success" not in st.session_state:
    st.session_state.booking_success = False


# ==============================================================================
# 3. SIDEBAR (STEUERUNG)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏢 DTAG Procurement AI")
    st.caption("Advanced Spend Intelligence & Entity Resolution")
    st.divider()
    
    mode = st.radio(
        "Kognitiven Modus wählen:",
        ["Simulierte Agenten-Kognition (Demo)", "Live OpenAI API (GPT-4o)"],
        index=0,
        help="Für die offline-fähige Vorstands-Demo auf 'Simuliert' belassen."
    )
    
    st.divider()
    st.markdown("#### ⚡ Aktiver Audit-Task:")
    st.info("**Ziel-Pattern:**\nMulti-Hop M&A Fragmentation Check YTD")
    
    # Der Haupt-Trigger
    if st.button("⚡ Agentic Spend Scan starten", type="primary", use_container_width=True):
        st.session_state.scan_executed = True
        st.session_state.booking_success = False
        st.balloons() # Visuelles Feuerwerk 1
        
    st.divider()
    st.caption("System-Status: verbunden mit SAP P01 (Client 100)")


# ==============================================================================
# 4. MAIN WORKSPACE (4 TABS)
# ==============================================================================
st.title("Agentic AI im Spend Management")
st.subheader("Automatisierte Identifikation fragmentierter Rahmenvertrags-Rückvergütungen")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. SAP Status Quo (Silo-Sicht)", 
    "🧠 2. Agentic Reasoning Console", 
    "💰 3. Financial Impact & Action", 
    "🛡️ 4. Betriebsrat & Compliance Log"
])

# ------------------------------------------------------------------------------
# TAB 1: SAP STATUS QUO
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("### Klassische SAP-Sicht YTD (Ohne kognitive Verklammerung)")
    
    # Berechnung der Top 10 Kreditoren nach reinem Einzelsystem-Spend
    spend_per_vendor = EKKO.groupby("LIFNR")['NETWR'].sum().reset_index()
    merged_silo = pd.merge(spend_per_vendor, LFA1, on="LIFNR")
    top_10 = merged_silo.sort_values(by="NETWR", ascending=False).head(10)
    
    col_chart, col_callout = st.columns([2, 1])
    
    with col_chart:
        # Streamlit Bar Chart erwartet Index als Label
        chart_data = top_10.set_index("NAME1")["NETWR"]
        st.bar_chart(chart_data, color="#4b525a")
        
    with col_callout:
        st.warning("""
        **SAP-Systemwarnung (ERP Standard):**
        
        Kein Einzellieferant erreicht die vertragliche Kickback-Schwelle von **50.000.000 €**.
        
        * Cisco Systems GmbH (Bonn): 22,0 Mio. €
        * Status Rückvergütung YTD: **0,00 €**
        """, icon="⚠️")
        st.caption("Traditionelle SQL-Skripte werten Kreditorenkonten strikt getrennt nach LIFNR aus. M&A-Historie unbekannt.")

    st.divider()
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### Auszug `LFA1` (Lieferantenstamm)")
        st.dataframe(LFA1.head(8), use_container_width=True)
    with col_t2:
        st.markdown("#### Auszug `EKKO` (Bestellbelege YTD)")
        st.dataframe(EKKO.head(8), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: AGENTIC REASONING CONSOLE (DAS HERZSTÜCK)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### Live Execution Log des Autonomous Spend Agents")
    
    if not st.session_state.scan_executed:
        st.info("👈 Der Agent befindet sich im Standby. Bitte starte den Scan über den magentafarbenen Button in der linken Sidebar.")
    else:
        # Statische Simulation der kognitiven Sub-Schritte
        log_stream = [
            ("[10:00:01] [INGESTION] Lese SAP-Tabellen LFA1 (40 Kreditoren) und EKKO (250 Bestellungen)...", "normal"),
            ("[10:00:02] [FUZZY MATCH] Prüfe Steuernummern & Namensvektoren auf Entitäts-Dubletten...", "normal"),
            (" ├── Verknüpfe LIFNR 10001 ('Cisco Systems GmbH', Bonn) mit LIFNR 10002 ('CISCO SYSTEMS INC', San Jose)", "success"),
            (" └── Verknüpfe LIFNR 10003 ('Cisco Meraki UK Ltd', London) via String-Distanz (0.88)", "success"),
            ("[10:00:03] [WORLD KNOWLEDGE] Initiiere Multi-Hop Web Search / SEC-Filing Abfrage für verbleibende Spends...", "normal"),
            (" ├── KNOWLEDGE GRAPH HIT: 'Acacia Communications' (LIFNR 10004) wurde im März 2021 von Cisco akquiriert.", "warn"),
            (" └── KNOWLEDGE GRAPH HIT: 'Splunk Services' (LIFNR 10005) wurde im März 2024 von Cisco akquiriert.", "warn"),
            ("[10:00:04] [ENTITY RESOLUTION] Verklammerung der Kreditoren [10001, 10002, 10003, 10004, 10005] zu 'Ultimate Parent: Cisco Global'", "success"),
            ("[10:00:05] [VECTOR RAG] Abfrage der Vertragsdatenbank Z_CONTRACTS nach Rahmenverträgen für 'Cisco Global'...", "normal"),
            (" └── Treffer: Vertrag 'CTR-2024-CISC' (Klausel 8.2: 2.0% Kickback ab 50,0 Mio. € kumuliertem Gruppenumsatz)", "success"),
            ("[10:00:06] [REASONER] Führe mathematische Überprüfung via SymPy Engine durch:", "normal"),
            (" ├── Summe IST-Spend (22,0M + 4,0M + 10,0M + 9,0M + 7,4M) = 52.400.000,00 €", "normal"),
            (" ├── Prüfe Bedingung: 52.400.000,00 € > 50.000.000,00 € -> TRUE", "success"),
            (" └── Berechne Forderung: 52.400.000,00 € * 0.02 = 1.048.000,00 €", "success"),
            ("[10:00:07] [ACTION ENGINE] Kickback-Anspruch erfolgreich verifiziert! Erstelle Anschreiben & SAP BAPI-Payload...", "success")
        ]
        
        # Darstellung als Terminal
        st.markdown('<div class="agent-terminal">', unsafe_allow_html=True)
        for text, level in log_stream:
            color = "#00ff66" if level == "success" else ("#ffcc00" if level == "warn" else "#ffffff")
            st.markdown(f'<span style="color: {color};">{text}</span>', unsafe_allow_html=True)
            time.sleep(0.05) # Kurzer visueller Delay für den "Live-Gefühl"-Effekt
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.caption("Agentic Stack: LangGraph Orchestration -> Python REPL Tool -> Enterprise RAG -> SAP BAPI Connector")

# ------------------------------------------------------------------------------
# TAB 3: FINANCIAL IMPACT & ACTION
# ------------------------------------------------------------------------------
with tab3:
    if not st.session_state.scan_executed:
        st.info("Führe zuerst den Scan aus, um die finanziellen Metriken zu berechnen.")
    else:
        st.markdown("### Konsolidierte Finanzkennzahlen (Cisco Global Gruppe)")
        
        # Die drei riesigen Metric Cards
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.metric(
                label="Erkannter Gruppen-Spend YTD", 
                value="52,40 Mio. €", 
                delta="+30,40 Mio. € (durch KI aufgedeckt)"
            )
        with col_m2:
            st.metric(
                label="Vertragliche Kickback-Schwelle", 
                value="50,00 Mio. €", 
                delta="Schwelle gerissen",
                delta_color="off"
            )
        with col_m3:
            # Akzent-Card in fettem Magenta
            st.markdown("""
                <div class="cash-claim-card">
                    <p class="cash-title">Generierter Cash-Anspruch</p>
                    <p class="cash-amount">1.048.000 €</p>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### Automatisiert erstelltes Anschreiben (CFO-Level)")
        
        cfo_letter = """
        **DEUTSCHE TELEKOM AG** — Group Procurement & Supply Management  
        *Friedrich-Ebert-Allee 140, 53113 Bonn*

        **An:** Cisco Systems GmbH  
        **z.Hd.:** Chief Financial Officer / Geschäftsführung  
        **Adresse:** Hans-Sachs-Straße 10, 53115 Bonn  

        **Vorab per E-Mail:** cfo-desk-germany@cisco.com  
        **Datum:** 22. Juni 2026  

        **Betreff: Geltendmachung der Konzern-Rückvergütung YTD gem. Rahmenvertrag CTR-2024-CISC**

        Sehr geehrte Damen und Herren,

        im Zuge unseres kontinuierlichen, KI-gestützten Spend-Audits der Deutsche Telekom Gruppe (inklusive verbundener Unternehmen im Sinne des § 15 AktG) haben wir die kumulierten Einkaufsumsätze mit dem Cisco-Konzern für das laufende Kalenderjahr auditiert.

        Gemäß **Klausel 8.2** unseres Rahmenvertrags *CTR-2024-CISC* gewährt Cisco der DTAG eine gruppenweite Rückvergütung von **2,0 %** auf den gesamten Netto-Jahresumsatz, sobald das kumulierte Einkaufsvolumen den Schwellenwert von 50,00 Mio. EUR übersteigt.

        Unsere forensische Entitätskonsolidierung der in unseren SAP-Systemen geführten Kreditoren weist YTD folgendes anrechenbares Netto-Volumen aus:

        1. Kreditor 10001 (Cisco Systems GmbH, Bonn) — BUKRS 1000/1020: 22.000.000,00 €
        2. Kreditor 10002 (CISCO SYSTEMS INC, San Jose) — BUKRS 1000: 4.000.000,00 €
        3. Kreditor 10003 (Cisco Meraki UK Ltd, London) — BUKRS 1040: 10.000.000,00 €
        4. Kreditor 10004 (Acacia Communications Ireland) — BUKRS 1020: 9.000.000,00 € [M&A Nachweis: SEC Filing 2021]
        5. Kreditor 10005 (Splunk Services Germany, München) — BUKRS 1000: 7.400.000,00 € [M&A Nachweis: SEC Filing 2024]

        **Gesamtvolumen Deutsche Telekom Gruppe YTD: 52.400.000,00 EUR**

        Der vertragliche Schwellenwert wurde somit um 2.400.000,00 EUR überschritten. Hieraus resultiert ein sofort fälliger Zahlungsanspruch der Deutsche Telekom AG in Höhe von:

        # 1.048.000,00 EUR
        *(in Worten: eine Million achtundvierzigtausend Euro)*

        Wir fordern Sie hiermit auf, den Betrag bis zum **15. Juli 2026** auf das Ihnen bekannte Konzernverrechnungskonto der Deutsche Telekom AG (IBAN: DE89 3704 0044 0000 0000 74) zu überweisen. 

        Eine entsprechende debitorische Belastungsanzeige (SAP Beleg-Nr. 4900081294) wurde in unserem SAP FI-Modul vorerfasst und geht Ihrer Buchhaltung parallel über das Ariba Network zu.

        Mit freundlichen Grüßen

        **i.A. DTAG Autonomous Spend Agent** *Machine-Signed by DTAG Cognitive Procurement Core (ID: AGT-884-PRO)*
        """
        
        st.markdown(cfo_letter)
        
        st.divider()
        
        # Buchungs-Action
        if st.button("⚡ SAP FI-NVE (Nachträgliche Vergütung) Beleg automatisch buchen", type="primary"):
            st.session_state.booking_success = True
            st.balloons() # Visuelles Feuerwerk 2
            
        if st.session_state.booking_success:
            st.success("""
            **ERP COMMIT ERFOLGREICH:** BAPI `BAPI_INCOMINGINVOICE_CREATE` wurde synchron aufgerufen.  
            * Buchungskreis: `1000` (Telekom Dtl.)
            * Belegnummer: `4900081294`
            * Status: Vorerfasst & zur Freigabe an Leiter Einkauf (L4) geroutet.
            """, icon="✅")

# ------------------------------------------------------------------------------
# TAB 4: BETRIEBSRAT & COMPLIANCE LOG
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("### Revisionssicheres Entscheidungsprotokoll (Explainable AI)")
    st.caption("Echtzeit-Dokumentation gemäß DTAG Konzernbetriebsvereinbarung zu KI-Systemen (KBV-KI § 4)")
    
    audit_trail = [
        {
            "Zeitstempel": "10:00:02", 
            "KI-Modul": "Fuzzy-Matcher v4.1", 
            "Aktion": "Verknüpfung LIFNR 10001 & 10002", 
            "Begründung / Primärquelle": "Abgleich USt-IdNr. & Levenshtein-Distanz Namensfeld (0.89).", 
            "BR & Compliance Check": "KONFORM (Reine Stammdaten-Normalisierung)"
        },
        {
            "Zeitstempel": "10:00:04", 
            "KI-Modul": "Cognitive Web Graph", 
            "Aktion": "Zusammenschluss LIFNR 10004 zu 'Cisco'", 
            "Begründung / Primärquelle": "SEC Filing Form 8-K vom 01.03.2021 (Acacia Communications Merger).", 
            "BR & Compliance Check": "KONFORM (Verifizierung über öffentliche Primärquelle)"
        },
        {
            "Zeitstempel": "10:00:04", 
            "KI-Modul": "Cognitive Web Graph", 
            "Aktion": "Zusammenschluss LIFNR 10005 zu 'Cisco'", 
            "Begründung / Primärquelle": "SEC Filing Form 10-Q vom 18.03.2024 (Splunk Inc. Acquisition).", 
            "BR & Compliance Check": "KONFORM (Verifizierung über öffentliche Primärquelle)"
        },
        {
            "Zeitstempel": "10:00:05", 
            "KI-Modul": "Legal RAG Engine", 
            "Aktion": "Lesen der Tabelle Z_CONTRACTS", 
            "Begründung / Primärquelle": "Extraktion der Rückvergütungsklausel 8.2 aus Dokument 'CTR-2024-CISC'.", 
            "BR & Compliance Check": "KONFORM (User besitzt Berechtigungsobjekt M_EINF_VTR)"
        },
        {
            "Zeitstempel": "10:00:06", 
            "KI-Modul": "Deterministic Math Engine", 
            "Aktion": "Berechnung Cash-Anspruch (1.048 k€)", 
            "Begründung / Primärquelle": "Einsatz deterministischer Python SymPy-Bibliothek (Vier-Augen-Prinzip zu LLM).", 
            "BR & Compliance Check": "KONFORM (Keine Halluzination bei Finanzoperationen möglich)"
        },
        {
            "Zeitstempel": "10:00:07", 
            "KI-Modul": "HR Compliance Guard", 
            "Aktion": "Prüfung auf Lieferanten-Abwertung", 
            "Begründung / Primärquelle": "Der Algorithmus berechnet reine Kickback-Ansprüche auf Konzernebene.", 
            "BR & Compliance Check": "KONFORM (Es fand KEINE automatisierte Abwertung von Lieferanten statt)"
        }
    ]
    
    st.table(pd.DataFrame(audit_trail))
    st.info("🔒 Der Hash dieses Protokolls (`SHA-256: 9f8e9a2b1...`) wurde revisionssicher im DTAG Compliance-Ledger hinterlegt.")

# ==============================================================================
# FOOTER
# ==============================================================================
st.divider()
st.caption("© 2026 Deutsche Telekom AG | Enterprise Architecture & AI Center of Excellence")