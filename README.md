# **Simulação IoT para Controle de Energia em Escritório**  
### (Baseado em dados reais da EPE – Sudeste, Classe Comercial, Setembro/2024) (Link: https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/consumo-de-energia-eletrica)

Este projeto implementa uma simulação simples de automação IoT para reduzir o consumo energético de um escritório.  
O modelo utiliza o padrão real de consumo mensal da **EPE (Empresa de Pesquisa Energética)** — Região Sudeste, Classe Comercial, Setembro de 2024 — e escala o valor para representar um escritório pequeno que consome **800 kWh/mês**.

A simulação aplica uma automação IoT que reduz a carga para **modo standby (30 W)** quando não há presença no ambiente.

---

## **Estrutura do Projeto:**

programa/
│── main.py # Script principal da simulação IoT
│
resultados_iot/
│── simulacao_detalhada.csv # Consumo horário antes/depois
│── resumo_simulacao.csv # Resumo geral da economia
│── grafico_rolling_24h.png # Gráfico acumulado
│── grafico_consumo_diario.png # Gráfico diário
│
README.md

---

## **Como executar**

Para gerar **todos os gráficos, arquivos CSV e resultados**, execute o comando:

```bash
python programa/main.py
