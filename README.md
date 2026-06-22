# 🏢 Enterprise Procurement AI: "The Ultimate Parent Kickback Hunter"

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![SAP ERP](https://img.shields.io/badge/SAP-Standard_Schema-0FAAFF?logo=sap&logoColor=white)
![AI Wording](https://img.shields.io/badge/Agentic_AI-LangGraph_Pattern-8A2BE2)
![Status](https://img.shields.io/badge/Status-C--Level_Ready-brightgreen)

> **Ein interaktiver Software-Prototyp zur Demonstration von "Agentic AI im Spend Management" für den globalen Konzerneinkauf (Group Procurement).**

---

## 💡 The Business Case: Das 1-Million-Euro-Silo

Internationale Großkonzerne verlieren jährlich Millionen an vertraglichen Rahmenvertrags-Rückvergütungen (Kickbacks). Der Grund ist eine **historische Datenfragmentierung im SAP-Kreditorenstamm (`LFA1`)**, ausgelöst durch weltweite M&A-Aktivitäten der Lieferanten oder dezentrale, historisch gewachsene Buchungskreise.

### Das reale Beispiel in dieser Demo:
* Ein DAX-40-Konzern hält mit **"Cisco Global"** einen Rahmenvertrag: *Ab 50,0 Mio. € kumuliertem Konzernumsatz greift eine Rückvergütung von 2,0 %.*
* Im SAP-System des Unternehmens existieren jedoch 5 isolierte Kreditoren (Cisco Systems GmbH, Cisco Meraki UK, Acacia Ireland etc.). 
* **Das Problem:** Keine Einzeleinheit reißt für sich allein die 50-Mio-Schwelle. Ein klassisches ERP-Skript (ABAP/SQL) meldet: *Kickback-Anspruch YTD = 0,00 €.*
* **Die Lösung:** Der Cognitive Agent schlägt die Brücke zwischen internen SAP-Tabellen und globalem Wirtschafts-Weltwissen (Knowledge Graphs), verklammert die Entitäten und sichert dem Einkauf einen Cash-Back von **1.048.000 €**.

---

## 🚀 Live Demo (Cloud)

Die Anwendung ist ohne lokale Installation direkt im Browser testbar:

👉 **[Enterprise Kickback Hunter — Live Demo starten](https://proc-kickback-hunter.streamlit.app/)** *(Hinweis: Beim allerersten Aufruf der Instanz kann der Boot-Vorgang ca. 15–20 Sekunden in Anspruch nehmen).*

---

## 🧠 Die Agentic Reasoning Pipeline

Der Prototyp simuliert das kognitive Handeln eines autonomen Einkaufs-Auditors in 5 synchronen Phasen:

```mermaid
graph TD;
    A[SAP Ingestion: LFA1 & EKKO] --> B[Fuzzy Tax-ID Match];
    B --> C[Multi-Hop M&A Knowledge Graph];
    C --> D[Vector RAG: Z_CONTRACTS];
    D --> E[Deterministic Math Engine: SymPy];
    E --> F[SAP FI Commit / BAPI_INCOMINGINVOICE_CREATE];