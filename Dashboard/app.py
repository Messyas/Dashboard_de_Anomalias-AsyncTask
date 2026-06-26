from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Dashboard de Anomalias",
    page_icon=":bar_chart:",
    layout="wide",
)


st.title("Dashboard de Anomalias")
st.caption("Estrutura inicial do dashboard. As analises serao adicionadas depois.")

BASE_DIR = Path(__file__).resolve().parents[1]
BPMN_IMAGE = BASE_DIR / "BPMN-as-is.png"


with st.sidebar:
    st.header("Filtros")
    st.info("Filtros serao adicionados quando os dados forem integrados.")


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
    st.subheader("Visao geral")
    st.info("Area reservada para KPIs gerais do processo.")


with tab_failures:
    st.subheader("Falhas")
    st.info("Area reservada para Pareto, Jig x etapa e analises de defeitos.")


with tab_time:
    st.subheader("Tempo e paradas")
    st.info("Area reservada para cycle time, falhas no tempo e downtime.")


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
