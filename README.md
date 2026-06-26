# Dashboard de Anomalias - Setupbox

Projeto de analise exploratoria e dashboard para diagnostico de anomalias no processo de gravacao de setupboxes.

## Equipe

- André Filipe Aloise
- Gustavo Morais de Almada
- Messyas Gois França
- Teodorio Ferreira Neto

## Artefatos da entrega

- EDA: [Notebooks/1-EDA.ipynb](Notebooks/1-EDA.ipynb)
- Dashboard: [Dashboard/app.py](Dashboard/app.py)
- Dataset: [Data/recording_test_setupbox.xlsx](Data/recording_test_setupbox.xlsx)
- Enunciado: [Docs/Tarefa01-Dashboard-de-Anomalias.pdf](Docs/Tarefa01-Dashboard-de-Anomalias.pdf)
- BPMN as-is: [BPMN-as-is.png](BPMN-as-is.png)
- PDD: [pdd-setupbox.md](pdd-setupbox.md)

## Como executar

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Abra e execute o notebook de EDA:

```bash
jupyter notebook Notebooks/1-EDA.ipynb
```

3. Execute o dashboard:

```bash
streamlit run Dashboard/app.py
```
