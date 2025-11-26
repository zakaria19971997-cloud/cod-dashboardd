import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import base64
from io import StringIO

# Configuration Streamlit
st.set_page_config(
    page_title="COD Dashboard Africa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .insight-box {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 1. CONNEXION À GOOGLE SHEETS
# ============================================

@st.cache_resource
def get_gsheet_data():
    """Connexion à Google Sheets et récupération des données"""
    try:
        # Créer les credentials depuis le fichier JSON
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Créer manuellement les credentials (à adapter avec ta clé)
        creds_dict = {
            "type": "service_account",
            "project_id": "smooth-ocean-479419-r8",
            "private_key_id": "168a8d82e2f5cb58460f6ce894f9f3845a89eb32",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCHiPGpWpbleti7\np45u/HLpdt2H4PTxeAk8qiqLtGOslgQdY+k+GQxXZEcK2rQmV2luVK+SIdMn+Hr1\nKcu46AF9MQ//P6y9QzECYUMFE8RPSSNGsNUrrjPMUrBzQ3J5HR99h5OJGLMZtXt2\nmunLUJ8h0BQFJoddJ/RhKsdZCsR2Py/LwxyBRxCIleiTz2UkJScCsMtHdqj1qCF/\n3X6L1X6YmukX/m+PuckBVSoMOjozYuqePeagi8gXbZRgWlGIeNt3pcLk0dnWN8pD\nRnumswU9nfEhdMRqPjMXHzTw8Zm0EVOUKb+ttjP84lLQv0WxDy+Vqrpy9Gy4o7lB\njZqXg9+hAgMBAAECggEACqgg4EEINlj3a6HcGCvvWR4IgyOT/tyCVWvH1p5DbBGL\nl0gA0eokR0bSMy9JFO6wkoVEHMheEvl9qYM0yoArhc1yxY4bJfJ/iwFcxKxuNhG5\nHVjQGhQjbIBf8WAvQwigLj2XwyLXCkFzyLqbgWoAaSc0O8dww0ld9LnpXL30/psR\n+t3Qhw9yFaFJDK0P/RRsWM+9F+zXp8t5FKUfsKRRTGbtppw2bVfK/WYd/HvWJ0nz\n2Xq4cwbqNfie1MICUu086ivLUY328dBf0yttmoZ2tjCeVxAeDaAbxBy+bGdh6UfT\n98ltv0WFsOU8LEUKqHC+e5mWOFilBdzb0iglsxETBQKBgQC73uB8XCllytV3fd5x\na2gZiQ6ydT74/faigTh5DuxmZwV7B1mQxlyDCdvZnJcGfU87epfDqs219rNzZzhm\nQOsLsSHdcQuChkZP5uTHq9Xth9H2SC2hfQOSGUKFgBcyx5mzBn65sevKwpe550mi\nr9xdQ0kKe6768LnyZcq+GXt51wKBgQC4r3EJuIRlyCqGJuBgKmKp9G/5iiKk23gF\n0d96WLGOMnd4a9zoP3E6YbvQ+kDBMW0zRBx6Nc+yAMqVJ8ouM44EqgNzHyfv49L+\nFay7FiJvEH7mcjggmsClQM4aPrxhOi3wjpefKUiy7oiLbHRZQYOOGCdF2mn9jf4P\n1lkAM5LzRwKBgBxYZEZfIV/aWprMwuMZ8Xro0u7aAcZPiwa5uGuLdN9+a7VERp8x\nToP22NTca2zvOyUeOgernZ32utyOllPXN59r+lAO3k2zNKiZjasSohRUibk+6qOS\n2RcR+Jdr3BQtSWNZd4VM8uaEtZ+25cVGA1mO7VZHkv8JkwSflxdXgOnBAoGAa5nT\n6wz1HnPjyqtF2OF5AHoo7yN7Eb/IiuN/J8IbGLTwhFmbqDimWJRun8/eAHEypUbO\nrKlDa/soDITVN9vTp4YCYoVJeGutF1o7e/jmcP0UYmEzsFNZYC6EpifdC2yhLWF2\nl0WvVIjDRzAWDZas9hG+d+VMEW00E7gXvJVPzasCgYAoZxfpyywEdbVP3sT5J/Cb\nXBmZejXZFZsdaf65YSNKseA7KcFwsQyVow/ug2nWMI7UkBqyfAgXRbfthWHy71v7\nFaYz2E8sXFb0BqqXcU9PyxVpqQFg/6No4V7p0iV+BFDo6lJyd0NeGO5o1nVsaY7Z\nW48g+uFGV9yxh0TlkJwrpQ==\n-----END PRIVATE KEY-----\n",
            "client_email": "zak-cod-dashboard-bot@smooth-ocean-479419-r8.iam.gserviceaccount.com",
            "client_id": "108257432574590261434",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/zak-cod-dashboard-bot%40smooth-ocean-479419-r8.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes=scope)
        gc = gspread.authorize(creds)
        
        # Ouvrir le Google Sheet
        spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1LDLdQixgZfs7DUs0C26tdC-BOr8GNN7BGg08dHfdc8s/edit")
        
        return spreadsheet
    except Exception as e:
        st.error(f"Erreur connexion Google Sheets: {str(e)}")
        return None

# ============================================
# 2. CHARGER LES DONNÉES
# ============================================

def load_sheets_data():
    """Charger les données depuis tous les onglets"""
    try:
        spreadsheet = get_gsheet_data()
        if spreadsheet is None:
            return None, None, None, None
        
        # Charger chaque onglet
        ventes_mois = pd.DataFrame(spreadsheet.worksheet("VENTES_MOIS").get_all_values()[1:], 
                                   columns=spreadsheet.worksheet("VENTES_MOIS").get_all_values()[0])
        
        ventes_pays = pd.DataFrame(spreadsheet.worksheet("VENTES_PAYS").get_all_values()[1:],
                                   columns=spreadsheet.worksheet("VENTES_PAYS").get_all_values()[0])
        
        sourcing_stock = pd.DataFrame(spreadsheet.worksheet("SOURCING_STOCK").get_all_values()[1:],
                                      columns=spreadsheet.worksheet("SOURCING_STOCK").get_all_values()[0])
        
        tests_produits = pd.DataFrame(spreadsheet.worksheet("TESTS_PRODUITS").get_all_values()[1:],
                                      columns=spreadsheet.worksheet("TESTS_PRODUITS").get_all_values()[0])
        
        # Nettoyer les données (convertir en numériques)
        for col in ventes_mois.columns:
            if col not in ['Year', 'Month']:
                ventes_mois[col] = pd.to_numeric(ventes_mois[col], errors='coerce')
        
        for col in ventes_pays.columns:
            if col != 'Country':
                ventes_pays[col] = pd.to_numeric(ventes_pays[col], errors='coerce')
        
        return ventes_mois, ventes_pays, sourcing_stock, tests_produits
    except Exception as e:
        st.error(f"Erreur chargement données: {str(e)}")
        return None, None, None, None

# ============================================
# 3. GÉNÉRER DES INSIGHTS IA
# ============================================

def generate_insights(ventes_mois, ventes_pays):
    """Générer des insights basés sur les données"""
    insights = []
    
    if ventes_mois is not None and len(ventes_mois) > 0:
        # Insight 1: Mois le plus rentable
        best_month_idx = ventes_mois['Net Profit'].astype(float).idxmax()
        best_month = ventes_mois.loc[best_month_idx]
        insights.append(f"✅ **Mois le plus rentable**: {best_month['Month']} {best_month['Year']} avec un profit net de ${float(best_month['Net Profit']):,.0f}")
        
        # Insight 2: Trend de marge
        avg_margin = ventes_mois['Margin %'].astype(float).mean()
        insights.append(f"📈 **Marge moyenne**: {avg_margin:.2f}% - Objectif: maintenir > 20%")
        
        # Insight 3: ROI ads
        total_sells = ventes_mois['Total Sells'].astype(float).sum()
        total_ads = ventes_mois['Ads Spend'].astype(float).sum()
        roi = (total_sells / total_ads) if total_ads > 0 else 0
        insights.append(f"💰 **ROI Publicités**: {roi:.2f}x - Pour chaque 1$ dépensé, tu gagnes ${roi:.2f}")
    
    if ventes_pays is not None and len(ventes_pays) > 0:
        # Insight 4: Pays le plus rentable
        best_country_idx = ventes_pays['Net Profit'].astype(float).idxmax()
        best_country = ventes_pays.loc[best_country_idx]
        insights.append(f"🌍 **Pays star**: {best_country['Country']} avec ${float(best_country['Net Profit']):,.0f} de profit")
        
        # Insight 5: Performance par pays
        ventes_pays['Profit_Margin'] = (ventes_pays['Net Profit'].astype(float) / ventes_pays['Total Sells'].astype(float) * 100)
        top_margin = ventes_pays.loc[ventes_pays['Profit_Margin'].idxmax()]
        insights.append(f"🎯 **Meilleure marge par pays**: {top_margin['Country']} avec {float(top_margin['Profit_Margin']):.1f}%")
    
    return insights

# ============================================
# 4. INTERFACE STREAMLIT
# ============================================

# Header
st.markdown('<p class="main-header">📊 Dashboard COD Africa Intelligence</p>', unsafe_allow_html=True)
st.write("Analyse automatique de vos performances e-commerce multi-pays")

# Charger les données
ventes_mois, ventes_pays, sourcing_stock, tests_produits = load_sheets_data()

if ventes_mois is None:
    st.error("⚠️ Impossible de charger les données. Vérifie la connexion à Google Sheets.")
    st.stop()

# ============================================
# MENU DE NAVIGATION
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["📈 Vue Globale", "🌍 Par Pays", "📦 Stock & Sourcing", "💡 Idées IA"])

# ============================================
# TAB 1: VUE GLOBALE
# ============================================

with tab1:
    st.subheader("Performance Globale")
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sells = ventes_mois['Total Sells'].astype(float).sum()
        st.metric("Total Ventes", f"${total_sells:,.0f}")
    
    with col2:
        net_profit = ventes_mois['Net Profit'].astype(float).sum()
        st.metric("Profit Net", f"${net_profit:,.0f}")
    
    with col3:
        avg_margin = ventes_mois['Margin %'].astype(float).mean()
        st.metric("Marge Moy", f"{avg_margin:.2f}%")
    
    with col4:
        total_ads = ventes_mois['Ads Spend'].astype(float).sum()
        st.metric("Total Ads Spend", f"${total_ads:,.0f}")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique CA par mois
        fig_ca = px.line(ventes_mois, x='Month', y='Total Sells', 
                         title='Chiffre d\'affaires par mois',
                         markers=True)
        fig_ca.update_layout(hovermode='x unified')
        st.plotly_chart(fig_ca, use_container_width=True)
    
    with col2:
        # Graphique Profit par mois
        fig_profit = px.bar(ventes_mois, x='Month', y='Net Profit',
                            title='Profit Net par mois',
                            color='Net Profit')
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # Tableau des données mensuelles
    st.subheader("Détail Mensuel")
    st.dataframe(ventes_mois, use_container_width=True)

# ============================================
# TAB 2: PAR PAYS
# ============================================

with tab2:
    st.subheader("Performance par Pays")
    
    # Sélecteur de pays
    countries = ventes_pays['Country'].unique()
    selected_country = st.selectbox("Sélectionne un pays", countries)
    
    # Filtrer les données
    country_data = ventes_pays[ventes_pays['Country'] == selected_country].iloc[0]
    
    # KPIs du pays
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ventes", f"${float(country_data['Total Sells']):,.0f}")
    
    with col2:
        st.metric("Profit", f"${float(country_data['Net Profit']):,.0f}")
    
    with col3:
        st.metric("Ads Spend", f"${float(country_data['Ads Spend']):,.0f}")
    
    with col4:
        profit_margin = (float(country_data['Net Profit']) / float(country_data['Total Sells']) * 100) if float(country_data['Total Sells']) > 0 else 0
        st.metric("Marge %", f"{profit_margin:.1f}%")
    
    # Graphique comparatif
    fig_countries = px.bar(ventes_pays, x='Country', y='Net Profit',
                           title='Profit Net par Pays',
                           color='Net Profit')
    st.plotly_chart(fig_countries, use_container_width=True)
    
    # Tableau des pays
    st.subheader("Comparaison Tous Pays")
    st.dataframe(ventes_pays, use_container_width=True)

# ============================================
# TAB 3: STOCK & SOURCING
# ============================================

with tab3:
    st.subheader("Gestion du Stock et Sourcing")
    
    # Filtrer par pays
    countries_stock = sourcing_stock['Country'].unique()
    selected_country_stock = st.selectbox("Sélectionne un pays pour le stock", countries_stock)
    
    # Données du pays
    country_stock = sourcing_stock[sourcing_stock['Country'] == selected_country_stock]
    
    # Résumé du stock
    total_qty = pd.to_numeric(country_stock['Quantity Imported'], errors='coerce').sum()
    total_value = pd.to_numeric(country_stock['Importation Price'], errors='coerce').sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Stock Total (unités)", f"{int(total_qty)}")
    
    with col2:
        st.metric("Valeur Stock", f"${total_value:,.0f}")
    
    with col3:
        st.metric("Produits", len(country_stock['Product Name'].unique()))
    
    # Tableau détaillé
    st.subheader(f"Détail Stock - {selected_country_stock}")
    st.dataframe(country_stock, use_container_width=True)

# ============================================
# TAB 4: IDÉES IA
# ============================================

with tab4:
    st.subheader("💡 Insights IA - Recommandations Automatiques")
    
    # Générer les insights
    insights = generate_insights(ventes_mois, ventes_pays)
    
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    
    # Recommandations supplémentaires
    st.markdown("---")
    st.subheader("🎯 Recommandations d'Action")
    
    recommendations = [
        "📊 **Augmente les dépenses pub** sur les pays avec marge > 25%",
        "🛑 **Réduis ou arrête** les tests sur les pays avec marge < 5%",
        "📦 **Planifie un sourcing** pour les produits avec stock < 100 unités",
        "💰 **Optimise le coût COD** - Cherche des partenaires moins chers",
        "🔄 **Teste de nouveaux produits** dans les pays les plus rentables en premier"
    ]
    
    for rec in recommendations:
        st.markdown(f"✓ {rec}")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9em;">
    <p>Dashboard COD Africa | Mise à jour automatique | Données depuis Google Sheets</p>
    <p>Créé avec Streamlit + PandasAI</p>
</div>
""", unsafe_allow_html=True)
