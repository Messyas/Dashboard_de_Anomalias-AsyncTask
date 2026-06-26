from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Dashboard de Anomalias",
    page_icon=":bar_chart:",
    layout="wide",
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "Data" / "recording_test_setupbox.xlsx"
BPMN_IMAGE = BASE_DIR / "BPMN-as-is.png"


@st.cache_data(show_spinner="Carregando arquivo...")
def load_data(path: Path):
    recordings = pd.read_excel(path, sheet_name="recordings")
    line_stops = pd.read_excel(path, sheet_name="line_stops")
    data_dictionary = pd.read_excel(path, sheet_name="data_dictionary")

    return recordings, line_stops, data_dictionary


st.title("Dashboard de Anomalias")
st.caption("Estrutura inicial do dashboard. As analises serao adicionadas depois.")

if not DATA_PATH.exists():
    st.error(f"Arquivo nao encontrado: {DATA_PATH}")
    st.stop()

recordings, line_stops, data_dictionary = load_data(DATA_PATH)


with st.sidebar:
    st.header("Filtros")
    st.success("Arquivo carregado")
    st.caption(DATA_PATH.name)
    st.info("Filtros serao adicionados depois.")


tab_overview, tab_failures, tab_time, tab_audit, tab_docs = st.tabs(
    [
        "Visao geral",
        "Falhas",
        "Tempo e paradas",
        "Auditoria",
        "BPMN e PDD",
    ]
)


with tab_overview:
    st.subheader("Dados carregados")

    col1, col2, col3 = st.columns(3)
    col1.metric("recordings", f"{len(recordings):,} linhas")
    col2.metric("line_stops", f"{len(line_stops):,} linhas")
    col3.metric("data_dictionary", f"{len(data_dictionary):,} linhas")

    st.subheader("Previa da base principal")
    st.dataframe(recordings.head(100), use_container_width=True)


with tab_failures:
    st.subheader("Falhas")
    st.info("Area reservada para Pareto, Jig x etapa e analises de defeitos.")


with tab_time:
    st.subheader("Tempo e paradas")
    st.info("Area reservada para cycle time, falhas no tempo e downtime.")

    st.subheader("Previa de paradas de linha")
    st.dataframe(line_stops.head(100), use_container_width=True)


with tab_audit:
    st.subheader("Auditoria")
    st.info("Area reservada para tabela filtravel e exportacao CSV.")


with tab_docs:
    st.subheader("BPMN e PDD")
    if BPMN_IMAGE.exists():
        st.image(str(BPMN_IMAGE), caption="BPMN as-is do processo")
    else:
        st.info("Adicione o arquivo BPMN-as-is.png na raiz do projeto.")

    st.info("Area reservada para o PDD do processo.")
