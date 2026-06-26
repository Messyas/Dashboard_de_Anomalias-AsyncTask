from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Dashboard de Anomalias",
    page_icon=":bar_chart:",
    layout="wide",
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "Data" / "recording_test_setupbox.xlsx"
BPMN_IMAGE = BASE_DIR / "BPMN-as-is.png"
PDD_PATH = BASE_DIR / "pdd-setupbox.md"


@st.cache_data(show_spinner="Carregando arquivo...")
def load_data(path: Path):
    recordings = pd.read_excel(path, sheet_name="recordings")
    line_stops = pd.read_excel(path, sheet_name="line_stops")
    data_dictionary = pd.read_excel(path, sheet_name="data_dictionary")

    recordings["timestamp"] = pd.to_datetime(recordings["timestamp"], errors="coerce")
    line_stops["stop_start"] = pd.to_datetime(line_stops["stop_start"], errors="coerce")
    line_stops["stop_end"] = pd.to_datetime(line_stops["stop_end"], errors="coerce")

    return recordings, line_stops, data_dictionary


def get_options(data: pd.DataFrame, column: str):
    return sorted(data[column].dropna().unique().tolist())


def apply_multiselect_filter(data: pd.DataFrame, column: str, selected_values):
    if not selected_values:
        return data
    return data[data[column].isin(selected_values)]


def filter_recordings(data: pd.DataFrame, start_date, end_date, filters):
    filtered = data.copy()
    filtered = filtered[
        (filtered["timestamp"].dt.date >= start_date)
        & (filtered["timestamp"].dt.date <= end_date)
    ]

    for column, selected_values in filters.items():
        filtered = apply_multiselect_filter(filtered, column, selected_values)

    return filtered


def filter_line_stops(data: pd.DataFrame, start_date, end_date, selected_lines):
    filtered = data.copy()
    filtered = filtered[
        (filtered["stop_start"].dt.date <= end_date)
        & (filtered["stop_end"].dt.date >= start_date)
    ]

    if selected_lines:
        filtered = filtered[filtered["line"].isin(selected_lines)]

    return filtered


def build_pareto(data: pd.DataFrame, column: str):
    pareto = (
        data[column]
        .dropna()
        .value_counts()
        .rename_axis(column)
        .reset_index(name="count")
    )

    if pareto.empty:
        pareto["pct"] = []
        pareto["cum_pct"] = []
        return pareto

    pareto["pct"] = pareto["count"] / pareto["count"].sum()
    pareto["cum_pct"] = pareto["pct"].cumsum()
    return pareto


def plot_pareto(pareto: pd.DataFrame, column: str, title: str):
    fig = go.Figure()
    fig.add_bar(
        x=pareto[column],
        y=pareto["count"],
        name="Quantidade",
        text=pareto["count"],
        textposition="outside",
    )
    fig.add_scatter(
        x=pareto[column],
        y=pareto["cum_pct"],
        name="% acumulado",
        mode="lines+markers",
        yaxis="y2",
    )
    fig.add_hline(
        y=0.8,
        line_dash="dash",
        line_color="#777",
        yref="y2",
    )
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="Quantidade de falhas",
        yaxis2={
            "title": "% acumulado",
            "overlaying": "y",
            "side": "right",
            "tickformat": ".0%",
            "range": [0, 1.05],
        },
        legend={"orientation": "h", "y": 1.12},
        margin={"t": 80},
    )
    return fig


def format_pareto_table(pareto: pd.DataFrame):
    display_data = pareto.copy()
    display_data["pct"] = display_data["pct"].map("{:.2%}".format)
    display_data["cum_pct"] = display_data["cum_pct"].map("{:.2%}".format)
    return display_data


def add_main_defect_flags(data: pd.DataFrame):
    flagged = data.copy()
    flagged["is_fail"] = flagged["result"].eq("FAIL")
    flagged["is_main_defect"] = (
        flagged["failed_step"].eq("drm_keys")
        | flagged["error_code"].eq("ERR_DRM")
    )
    return flagged


def summarize_main_defect(data: pd.DataFrame, dimension: str):
    summary = (
        data.groupby(dimension, dropna=False)
        .agg(
            total_attempts=("result", "size"),
            total_failures=("is_fail", "sum"),
            main_defects=("is_main_defect", "sum"),
        )
        .reset_index()
    )
    summary["failure_rate"] = summary["total_failures"] / summary["total_attempts"]
    summary["main_defect_rate"] = (
        summary["main_defects"] / summary["total_attempts"]
    )
    summary["ppm_main_defect"] = summary["main_defect_rate"] * 1_000_000
    return summary.sort_values("main_defect_rate", ascending=False)


st.title("Dashboard de Anomalias")
st.caption("Estrutura inicial do dashboard. As analises serao adicionadas depois.")

if not DATA_PATH.exists():
    st.error(f"Arquivo nao encontrado: {DATA_PATH}")
    st.stop()

recordings, line_stops, data_dictionary = load_data(DATA_PATH)

min_date = recordings["timestamp"].dt.date.min()
max_date = recordings["timestamp"].dt.date.max()


with st.sidebar:
    st.header("Filtros")
    st.success("Arquivo carregado")
    st.caption(DATA_PATH.name)

    date_range = st.date_input(
        "Periodo",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    selected_filters = {
        "line": st.multiselect("Linha", get_options(recordings, "line")),
        "station": st.multiselect("Estacao", get_options(recordings, "station")),
        "jig_id": st.multiselect("Jig", get_options(recordings, "jig_id")),
        "operator": st.multiselect("Operador", get_options(recordings, "operator")),
        "shift": st.multiselect("Turno", get_options(recordings, "shift")),
        "model": st.multiselect("Modelo", get_options(recordings, "model")),
        "firmware_version": st.multiselect(
            "Firmware",
            get_options(recordings, "firmware_version"),
        ),
        "result": st.multiselect("Resultado", get_options(recordings, "result")),
        "disposition": st.multiselect(
            "Disposition",
            get_options(recordings, "disposition"),
        ),
        "error_code": st.multiselect(
            "Codigo de erro",
            get_options(recordings, "error_code"),
        ),
    }


filtered_recordings = filter_recordings(
    recordings,
    start_date,
    end_date,
    selected_filters,
)
filtered_line_stops = filter_line_stops(
    line_stops,
    start_date,
    end_date,
    selected_filters["line"],
)


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

    st.subheader("Dados filtrados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros filtrados", f"{len(filtered_recordings):,}")
    col2.metric("Seriais unicos", f"{filtered_recordings['serial_number'].nunique():,}")
    col3.metric("Paradas filtradas", f"{len(filtered_line_stops):,}")

    st.subheader("Previa da base principal")
    st.dataframe(filtered_recordings.head(100), use_container_width=True)


with tab_failures:
    st.subheader("Falhas")

    failures = filtered_recordings[filtered_recordings["result"].eq("FAIL")].copy()

    col1, col2, col3 = st.columns(3)
    col1.metric("Tentativas filtradas", f"{len(filtered_recordings):,}")
    col2.metric("Falhas filtradas", f"{len(failures):,}")
    failure_rate = len(failures) / len(filtered_recordings) if len(filtered_recordings) else 0
    col3.metric("Taxa de falha", f"{failure_rate:.2%}")

    st.subheader("Pareto de defeitos")
    pareto_column = st.radio(
        "Agrupar Pareto por",
        ["failed_step", "error_code"],
        format_func={
            "failed_step": "Etapa com falha",
            "error_code": "Codigo de erro",
        }.get,
        horizontal=True,
    )

    pareto = build_pareto(failures, pareto_column)
    if pareto.empty:
        st.info("Nao ha falhas para os filtros atuais.")
    else:
        st.plotly_chart(
            plot_pareto(
                pareto,
                pareto_column,
                "Pareto de falhas",
            ),
            use_container_width=True,
        )
        st.dataframe(
            format_pareto_table(pareto),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Defeito principal do EDA: drm_keys / ERR_DRM")
    analysis_data = add_main_defect_flags(filtered_recordings)
    main_defect = analysis_data[analysis_data["is_main_defect"]]
    total_failures = analysis_data["is_fail"].sum()
    main_share_failures = (
        len(main_defect) / total_failures if total_failures else 0
    )
    main_share_attempts = (
        len(main_defect) / len(analysis_data) if len(analysis_data) else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Ocorrencias", f"{len(main_defect):,}")
    col2.metric("Participacao nas falhas", f"{main_share_failures:.2%}")
    col3.metric("Participacao nas tentativas", f"{main_share_attempts:.2%}")

    if main_defect.empty:
        st.info("O defeito principal nao aparece nos filtros atuais.")
    else:
        start_defect = main_defect["timestamp"].min()
        end_defect = main_defect["timestamp"].max()
        st.caption(
            f"Janela filtrada do defeito: {start_defect} ate {end_defect}"
        )

        dimension = st.selectbox(
            "Recortar defeito principal por",
            [
                "line",
                "station",
                "jig_id",
                "firmware_version",
                "model",
                "api_key",
            ],
            format_func={
                "line": "Linha",
                "station": "Estacao",
                "jig_id": "Jig",
                "firmware_version": "Firmware",
                "model": "Modelo",
                "api_key": "API key",
            }.get,
        )

        summary = summarize_main_defect(analysis_data, dimension).head(12)
        fig = go.Figure()
        fig.add_bar(
            x=summary["main_defect_rate"],
            y=summary[dimension].astype(str),
            orientation="h",
            text=summary["main_defect_rate"].map("{:.2%}".format),
            textposition="auto",
            customdata=summary[
                [
                    "total_attempts",
                    "total_failures",
                    "main_defects",
                    "ppm_main_defect",
                ]
            ],
            hovertemplate=(
                "%{y}<br>"
                "Taxa do defeito: %{x:.2%}<br>"
                "Tentativas: %{customdata[0]:,}<br>"
                "Falhas: %{customdata[1]:,}<br>"
                "Defeitos principais: %{customdata[2]:,}<br>"
                "PPM: %{customdata[3]:,.0f}<extra></extra>"
            ),
        )
        fig.update_layout(
            title="Taxa do defeito principal por dimensao",
            xaxis_title="Taxa do defeito principal",
            yaxis_title="",
            xaxis_tickformat=".0%",
            yaxis={"autorange": "reversed"},
        )
        st.plotly_chart(fig, use_container_width=True)

        display_summary = summary.copy()
        display_summary["failure_rate"] = display_summary["failure_rate"].map(
            "{:.2%}".format
        )
        display_summary["main_defect_rate"] = display_summary[
            "main_defect_rate"
        ].map("{:.2%}".format)
        display_summary["ppm_main_defect"] = display_summary[
            "ppm_main_defect"
        ].map("{:,.0f}".format)
        st.dataframe(display_summary, use_container_width=True, hide_index=True)


with tab_time:
    st.subheader("Tempo e paradas")
    st.info("Area reservada para cycle time, falhas no tempo e downtime.")

    st.subheader("Previa de paradas de linha")
    st.dataframe(filtered_line_stops.head(100), use_container_width=True)


with tab_audit:
    st.subheader("Auditoria")

    audit_columns = [
        "timestamp",
        "date",
        "time",
        "shift",
        "line",
        "station",
        "jig_id",
        "operator",
        "model",
        "sku",
        "wifi_band",
        "has_bluetooth",
        "has_cable",
        "firmware_version",
        "serial_number",
        "mac_address",
        "api_key",
        "attempt",
        "total_cycle_s",
        "result",
        "failed_step",
        "error_code",
        "disposition",
    ]
    audit_columns = [
        column for column in audit_columns if column in filtered_recordings.columns
    ]
    audit_data = filtered_recordings[audit_columns].sort_values("timestamp")

    st.caption(f"{len(audit_data):,} registros encontrados com os filtros atuais.")
    st.dataframe(audit_data, use_container_width=True, hide_index=True)

    csv_data = audit_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar auditoria CSV",
        data=csv_data,
        file_name="auditoria_filtrada.csv",
        mime="text/csv",
        disabled=audit_data.empty,
    )


with tab_docs:
    st.subheader("BPMN e PDD")
    if BPMN_IMAGE.exists():
        st.image(str(BPMN_IMAGE), caption="BPMN as-is do processo")
    else:
        st.info("Adicione o arquivo BPMN-as-is.png na raiz do projeto.")

    st.subheader("PDD")
    if PDD_PATH.exists():
        st.markdown(PDD_PATH.read_text(encoding="utf-8"))
    else:
        st.info("Adicione o arquivo pdd-setupbox.md na raiz do projeto.")
