import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import json
import os

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
    """Connexion à Google Sheets avec les secrets Replit"""
    try:
        # Lire les credentials depuis Replit Secrets
        creds_json = os.environ.get('GSHEET_CREDENTIALS')
        
        if not creds_json:
            st.error("❌ GSHEET_CREDENTIALS secret not found!")
            return None
        
        # Parser le JSON
        creds_dict = json.loads(creds_json)
        
        # Setup scope et autorisation
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes=scope)
        gc = gspread.authorize(creds)
        
        # Ouvrir le Google Sheet
        spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1LDLdQixgZfs7DUs0C26tdC-BOr8GNN7BGg08dHfdc8s/edit")
        
        return spreadsheet
    except Exception as e:
        st.error(f"❌ Erreur connexion: {str(e)}")
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
        
        # Nettoyer les données
        for col in ventes_mois.columns:
            if col not in ['Year', 'Month']:
                ventes_mois[col] = pd.to_numeric(ventes_mois[col], errors='coerce')
        
        for col in ventes_pays.columns:
            if col != 'Country':
                ventes_pays[col] = pd.to_numeric(ventes_pays[col], errors='coerce')
        
        return ventes_mois, ventes_pays, sourcing_stock, tests_produits
    except Exception as e:
        st.error(f"❌ Erreur chargement: {str(e)}")
        return None, None, None, None

# ============================================
# 3. GÉNÉRER DES INSIGHTS
# ============================================

def generate_insights(ventes_mois, ventes_pays):
    """Générer des insights basés sur les données"""
    insights = []
    
    if ventes_mois is not None and len(ventes_mois) > 0:
        best_month_idx = ventes_mois['Net Profit'].astype(float).idxmax()
        best_month = ventes_mois.loc[best_month_idx]
        insights.append(f"✅ **Mois le plus rentable**: {best_month['Month']} {best_month['Year']} avec ${float(best_month['Net Profit']):,.0f}")
        
        avg_margin = ventes_mois['Margin %'].astype(float).mean()
        insights.append(f"📈 **Marge moyenne**: {avg_margin:.2f}% (Objectif: >20%)")
        
        total_sells = ventes_mois['Total Sells'].astype(float).sum()
        total_ads = ventes_mois['Ads Spend'].astype(float).sum()
        roi = (total_sells / total_ads) if total_ads > 0 else 0
        insights.append(f"💰 **ROI Publicités**: {roi:.2f}x")
    
    if ventes_pays is not None and len(ventes_pays) > 0:
        best_country_idx = ventes_pays['Net Profit'].astype(float).idxmax()
        best_country = ventes_pays.loc[best_country_idx]
        insights.append(f"🌍 **Pays star**: {best_country['Country']} (${float(best_country['Net Profit']):,.0f})")
        
        ventes_pays['Profit_Margin'] = (ventes_pays['Net Profit'].astype(float) / ventes_pays['Total Sells'].astype(float) * 100)
        top_margin = ventes_pays.loc[ventes_pays['Profit_Margin'].idxmax()]
        insights.append(f"🎯 **Meilleure marge**: {top_margin['Country']} ({float(top_margin['Profit_Margin']):.1f}%)")
    
    return insights

# ============================================
# INTERFACE STREAMLIT
# ============================================

st.markdown('<p class="main-header">📊 Dashboard COD Africa Intelligence</p>', unsafe_allow_html=True)
st.write("Analyse automatique de vos performances e-commerce")

ventes_mois, ventes_pays, sourcing_stock, tests_produits = load_sheets_data()

if ventes_mois is None:
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Vue Globale", "🌍 Par Pays", "📦 Stock", "💡 Insights"])

# TAB 1: VUE GLOBALE
with tab1:
    st.subheader("Performance Globale")
    c1, c2, c3, c4 = st.columns(4)
    
    total_sells = ventes_mois['Total Sells'].astype(float).sum()
    net_profit = ventes_mois['Net Profit'].astype(float).sum()
    avg_margin = ventes_mois['Margin %'].astype(float).mean()
    total_ads = ventes_mois['Ads Spend'].astype(float).sum()
    
    with c1:
        st.metric("Total Ventes", f"${total_sells:,.0f}")
    with c2:
        st.metric("Profit Net", f"${net_profit:,.0f}")
    with c3:
        st.metric("Marge Moy", f"{avg_margin:.2f}%")
    with c4:
        st.metric("Ads Spend", f"${total_ads:,.0f}")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(ventes_mois, x='Month', y='Total Sells', markers=True, title='CA par mois')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(ventes_mois, x='Month', y='Net Profit', color='Net Profit', title='Profit par mois')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(ventes_mois, use_container_width=True)

# TAB 2: PAR PAYS
with tab2:
    st.subheader("Performance par Pays")
    countries = ventes_pays['Country'].unique()
    selected = st.selectbox("Sélectionne un pays", countries)
    data = ventes_pays[ventes_pays['Country'] == selected].iloc[0]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Ventes", f"${float(data['Total Sells']):,.0f}")
    with c2:
        st.metric("Profit", f"${float(data['Net Profit']):,.0f}")
    with c3:
        st.metric("Ads", f"${float(data['Ads Spend']):,.0f}")
    with c4:
        margin = (float(data['Net Profit']) / float(data['Total Sells']) * 100) if float(data['Total Sells']) > 0 else 0
        st.metric("Marge %", f"{margin:.1f}%")
    
    fig = px.bar(ventes_pays, x='Country', y='Net Profit', color='Net Profit', title='Profit par Pays')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(ventes_pays, use_container_width=True)

# TAB 3: STOCK
with tab3:
    st.subheader("Gestion du Stock")
    if sourcing_stock is not None:
        countries = sourcing_stock['Country'].unique()
        selected = st.selectbox("Sélectionne un pays", countries)
        data = sourcing_stock[sourcing_stock['Country'] == selected]
        st.dataframe(data, use_container_width=True)

# TAB 4: INSIGHTS
with tab4:
    st.subheader("💡 Insights & Recommandations")
    
    insights = generate_insights(ventes_mois, ventes_pays)
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 Actions à Prendre")
    recommendations = [
        "📊 Augmente les dépenses pub sur les pays avec marge > 25%",
        "🛑 Réduis les tests sur les pays avec marge < 5%",
        "📦 Planifie un sourcing pour stock < 100 unités",
        "💰 Optimise le coût COD",
        "🔄 Teste de nouveaux produits dans les pays profitables"
    ]
    for rec in recommendations:
        st.markdown(f"✓ {rec}")

st.markdown("---")
st.markdown("<div style='text-align:center; color:gray;'>Dashboard COD Africa | Live depuis Replit ✅</div>", unsafe_allow_html=True)
