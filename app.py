import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(page_title="Copa do Mundo 2026", layout="wide", page_icon="🏆")

# CSS Customizado Premium para UI/UX
st.markdown("""
<style>
    /* Estilo de fundo e fontes */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers com gradiente de texto */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    /* Estilo de cartões (Glassmorphism) para colunas */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    [data-testid="column"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Inputs numéricos menores e mais elegantes */
    input[type="number"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        color: white !important;
        border-radius: 8px !important;
        text-align: center;
        font-weight: bold;
    }
    
    input[type="number"]:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    /* Tabelas (Dataframes) modernizadas */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Abas customizadas */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0 0;
        border: 1px solid rgba(255,255,255,0.1);
        border-bottom: none;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.1);
        border-top: 2px solid #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# Funcoes auxiliares
def get_flag_url(iso_code):
    return f"https://flagcdn.com/24x18/{iso_code}.png"

def load_data():
    if "groups" not in st.session_state:
        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as f:
            data = json.load(f)
            st.session_state.groups = data["groups"]
            
        # Initialize matches
        matches = {}
        for g_name, teams in st.session_state.groups.items():
            matches[g_name] = [
                {"id": f"{g_name}_1", "t1": teams[0], "t2": teams[1], "s1": None, "s2": None},
                {"id": f"{g_name}_2", "t1": teams[2], "t2": teams[3], "s1": None, "s2": None},
                {"id": f"{g_name}_3", "t1": teams[0], "t2": teams[2], "s1": None, "s2": None},
                {"id": f"{g_name}_4", "t1": teams[1], "t2": teams[3], "s1": None, "s2": None},
                {"id": f"{g_name}_5", "t1": teams[0], "t2": teams[3], "s1": None, "s2": None},
                {"id": f"{g_name}_6", "t1": teams[1], "t2": teams[2], "s1": None, "s2": None},
            ]
        
        # Load from persistence if exists
        results_path = os.path.join(os.path.dirname(__file__), 'results.json')
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                saved_matches = json.load(f)
                matches.update(saved_matches)

        st.session_state.matches = matches

def save_results():
    results_path = os.path.join(os.path.dirname(__file__), 'results.json')
    with open(results_path, 'w') as f:
        json.dump(st.session_state.matches, f)

def calculate_standings(group_name):
    teams = st.session_state.groups[group_name]
    matches = st.session_state.matches[group_name]
    
    standings = {t["id"]: {"name": t["name"], "iso": t["iso"], "pts": 0, "pld": 0, "win": 0, "draw": 0, "loss": 0, "gf": 0, "ga": 0, "gd": 0} for t in teams}
    
    for m in matches:
        if m["s1"] is not None and m["s2"] is not None:
            t1, t2 = m["t1"]["id"], m["t2"]["id"]
            s1, s2 = int(m["s1"]), int(m["s2"])
            
            standings[t1]["pld"] += 1
            standings[t2]["pld"] += 1
            standings[t1]["gf"] += s1
            standings[t2]["gf"] += s2
            standings[t1]["ga"] += s2
            standings[t2]["ga"] += s1
            standings[t1]["gd"] += (s1 - s2)
            standings[t2]["gd"] += (s2 - s1)
            
            if s1 > s2:
                standings[t1]["pts"] += 3
                standings[t1]["win"] += 1
                standings[t2]["loss"] += 1
            elif s1 < s2:
                standings[t2]["pts"] += 3
                standings[t2]["win"] += 1
                standings[t1]["loss"] += 1
            else:
                standings[t1]["pts"] += 1
                standings[t2]["pts"] += 1
                standings[t1]["draw"] += 1
                standings[t2]["draw"] += 1
                
    # Sort by pts, gd, gf
    sorted_standings = sorted(standings.values(), key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True)
    return sorted_standings

load_data()

# Gráficos (Banner e Marca d'água)
import base64

def get_base64_image(prefix):
    for ext in ['png', 'jpg', 'jpeg', 'webp']:
        path = os.path.join(os.path.dirname(__file__), f'{prefix}.{ext}')
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

def render_graphics():
    banner_b64 = get_base64_image('banner')
    logo_b64 = get_base64_image('logo')
    
    # Marca d'água no fundo (Logo)
    if logo_b64:
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{logo_b64}"), linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
                background-repeat: no-repeat, no-repeat !important;
                background-position: center center, center center !important;
                background-attachment: fixed, fixed !important;
                background-size: 50% auto, cover !important;
                background-blend-mode: overlay, normal !important;
            }}
            </style>
        ''', unsafe_allow_html=True)
        
    # Header e Banner
    header_html = '<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem; margin-top: 1rem;">'
    
    if banner_b64:
        header_html += f'<img src="data:image/png;base64,{banner_b64}" style="width: 100%; max-width: 1200px; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">'
        
    header_html += '<h1 style="text-align: center; margin-bottom: 0;">🏆 Copa do Mundo FIFA 2026</h1>'
    header_html += '</div>'
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    if not banner_b64:
        st.markdown('<p style="text-align:center; color: #94a3b8;">(Salve a imagem do banner como banner.png na pasta do projeto para exibir aqui)</p>', unsafe_allow_html=True)

render_graphics()

tab1, tab2 = st.tabs(["Fase de Grupos", "Fase Eliminatória (Chaveamento)"])

with tab1:
    st.header("Fase de Grupos")
    
    group_names = list(st.session_state.groups.keys())
    group_tabs = st.tabs([f"Grupo {g}" for g in group_names])
    
    for i, g_name in enumerate(group_names):
        with group_tabs[i]:
            st.subheader(f"Partidas - Grupo {g_name}")
            
            # Show matches divididos em 2 colunas para ficar mais compacto
            match_col1, match_col2 = st.columns(2)
            
            for m_idx, m in enumerate(st.session_state.matches[g_name]):
                col_target = match_col1 if m_idx < 3 else match_col2
                
                with col_target:
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 1.5, 1.5, 0.5, 1.5, 1.5, 0.5])
                    c1.image(get_flag_url(m["t1"]["iso"]))
                    c2.markdown(f"<div style='text-align: right; padding-top: 5px; font-weight: bold;'>{m['t1']['id']}</div>", unsafe_allow_html=True)
                    
                    # Inputs
                    new_s1 = c3.number_input("", key=f"{m['id']}_1", min_value=0, max_value=20, value=m["s1"], label_visibility="collapsed")
                    
                    c4.markdown("<div style='text-align: center; padding-top: 5px; color: #94a3b8;'>X</div>", unsafe_allow_html=True)
                    
                    new_s2 = c5.number_input("", key=f"{m['id']}_2", min_value=0, max_value=20, value=m["s2"], label_visibility="collapsed")
                    
                    c6.markdown(f"<div style='text-align: left; padding-top: 5px; font-weight: bold;'>{m['t2']['id']}</div>", unsafe_allow_html=True)
                    c7.image(get_flag_url(m["t2"]["iso"]))
                    
                    if new_s1 != m["s1"] or new_s2 != m["s2"]:
                        st.session_state.matches[g_name][st.session_state.matches[g_name].index(m)]["s1"] = new_s1
                        st.session_state.matches[g_name][st.session_state.matches[g_name].index(m)]["s2"] = new_s2
                        save_results()
                        st.toast("Placar Atualizado! ⚽", icon="✅")
            
            st.write("---")
            st.subheader("Classificação Atualizada")
            # Show Standings
            standings = calculate_standings(g_name)
            df = pd.DataFrame(standings)
            if not df.empty:
                df = df[["name", "pts", "pld", "win", "draw", "loss", "gf", "ga", "gd"]]
                df.columns = ["Seleção", "Pts", "J", "V", "E", "D", "GP", "GC", "SG"]
                st.dataframe(df, hide_index=True, use_container_width=True)

def get_qualified_teams():
    firsts = []
    seconds = []
    thirds = []
    
    for g_name in st.session_state.groups.keys():
        standings = calculate_standings(g_name)
        if len(standings) >= 3:
            firsts.append((g_name, standings[0]))
            seconds.append((g_name, standings[1]))
            thirds.append((g_name, standings[2]))
            
    # sort thirds by pts, gd, gf
    thirds.sort(key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]), reverse=True)
    best_thirds = thirds[:8]
    return firsts, seconds, best_thirds

def is_group_stage_finished():
    for g_name in st.session_state.groups.keys():
        for m in st.session_state.matches[g_name]:
            if m["s1"] is None or m["s2"] is None:
                return False
    return True

with tab2:
    st.header("Chaveamento - Round of 32 até a Final")
    
    if not is_group_stage_finished():
        st.info("Preencha todos os resultados da fase de grupos para liberar o chaveamento.")
    else:
        st.success("Fase de grupos concluída! Aqui estão os classificados para o Round of 32.")
        
        firsts, seconds, thirds = get_qualified_teams()
        
        st.subheader("Seleções Classificadas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**1ºs Colocados**")
            for g, t in firsts:
                st.write(f"{t['name']} (Gr. {g})")
        with col2:
            st.write("**2ºs Colocados**")
            for g, t in seconds:
                st.write(f"{t['name']} (Gr. {g})")
        with col3:
            st.write("**Melhores 3ºs**")
            for g, t in thirds:
                st.write(f"{t['name']} (Gr. {g})")
                
        st.divider()
        st.subheader("Simulação do Round of 32 (Exemplo de cruzamento)")
        
        all_teams = [t[1] for t in firsts] + [t[1] for t in seconds] + [t[1] for t in thirds]
        
        # Criação de confrontos simulados simples
        for i in range(16):
            c1, c2, c3, c4, c5 = st.columns([1, 3, 1, 3, 1])
            t1 = all_teams[i]
            t2 = all_teams[31-i]
            
            c1.image(get_flag_url(t1["iso"]))
            c2.write(t1["name"])
            c3.write(" vs ")
            c4.write(t2["name"])
            c5.image(get_flag_url(t2["iso"]))
