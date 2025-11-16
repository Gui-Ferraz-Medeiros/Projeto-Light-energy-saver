import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------
# CONFIGURAÇÕES DO MODELO
# --------------------------

REGIAO = "Sudeste"
CLASSE = "Comercial"
MES = "2024-09"
CONSUMO_MENSAL_ESCRITORIO = 800.0     # kWh/mês (escalado)
POTENCIA_STANDBY = 30                 # W
FATOR_CO2 = 0.1                       # kg CO2 por kWh
TARIFA = 0.8                          # R$/kWh

# --------------------------
# CRIAÇÃO DAS PASTAS
# --------------------------

out_dir = Path("resultados_iot")
out_dir.mkdir(exist_ok=True)

# --------------------------
# 1. GERAR PERFIL HORÁRIO 
# --------------------------

data_inicio = datetime.date(2024, 9, 1)
data_fim = datetime.date(2024, 9, 30)

num_dias = (data_fim - data_inicio).days + 1

datas = []
pesos = []

for dia in range(num_dias):
    d = data_inicio + datetime.timedelta(days=dia)
    final_semana = d.weekday() >= 5
    
    for hora in range(24):
        datas.append(datetime.datetime.combine(d, datetime.time(hour=hora)))

        if final_semana:
            if 8 <= hora <= 18:
                peso = 0.6
            else:
                peso = 0.2
        else:
            if 8 <= hora <= 18:
                peso = 1.5
            elif 6 <= hora < 8 or 18 < hora <= 20:
                peso = 0.8
            else:
                peso = 0.3

        pesos.append(peso)

pesos = np.array(pesos)
pesos = pesos / pesos.sum()

kwh_por_hora = pesos * CONSUMO_MENSAL_ESCRITORIO

df = pd.DataFrame({
    "timestamp": datas,
    "kwh_estimated": kwh_por_hora
})

# ---------------------------------
# 2. GERAR PRESENÇA (0/1)
# ---------------------------------

np.random.seed(42)
presenca = []

for ts in df["timestamp"]:
    h = ts.hour
    weekday = ts.weekday() < 5
    
    if weekday:
        if 8 <= h <= 18:
            presenca.append(1 if np.random.rand() < 0.85 else 0)
        else:
            presenca.append(0)
    else:
        if 8 <= h <= 18:
            presenca.append(1 if np.random.rand() < 0.25 else 0)
        else:
            presenca.append(0)

df["presence"] = presenca

# ---------------------------------
# 3. CALCULAR CONSUMO BEFORE / AFTER
# ---------------------------------

df["consumption_w"] = df["kwh_estimated"] * 1000

df["consumption_after_w"] = df.apply(
    lambda r: POTENCIA_STANDBY if r["presence"] == 0 else r["consumption_w"],
    axis=1
)

df["kwh_before"] = df["consumption_w"] / 1000
df["kwh_after"] = df["consumption_after_w"] / 1000

# ---------------------------------
# 4. CÁLCULO DOS RESULTADOS
# ---------------------------------

total_before = df["kwh_before"].sum()
total_after = df["kwh_after"].sum()
economia_kwh = total_before - total_after
economia_co2 = economia_kwh * FATOR_CO2
economia_reais = economia_kwh * TARIFA

# ---------------------------------
# 5. SALVAR ARQUIVOS
# ---------------------------------

df.to_csv(out_dir / "simulacao_detalhada.csv", index=False)

resumo = pd.DataFrame([{
    "regiao": REGIAO,
    "classe": CLASSE,
    "mes": MES,
    "consumo_total_antes_kwh": total_before,
    "consumo_total_depois_kwh": total_after,
    "economia_kwh": economia_kwh,
    "economia_co2_kg": economia_co2,
    "economia_reais": economia_reais
}])

resumo.to_csv(out_dir / "resumo_simulacao.csv", index=False)

# ---------------------------------
# 6. GRÁFICOS
# ---------------------------------

# Gráfico 1 — rolling 24h
plt.figure(figsize=(10,4))
df.set_index("timestamp")[["kwh_before","kwh_after"]].rolling(24).sum().plot()
plt.title("Consumo acumulado 24h — Before vs After")
plt.ylabel("kWh (24h)")
plt.savefig(out_dir / "grafico_rolling_24h.png", bbox_inches='tight')
plt.close()

# Gráfico 2 — consumo diário
daily = df.groupby(df["timestamp"].dt.date)[["kwh_before","kwh_after"]].sum()

plt.figure(figsize=(10,4))
plt.plot(daily.index, daily["kwh_before"], label="Before")
plt.plot(daily.index, daily["kwh_after"], label="After")
plt.title("Consumo diário — Before vs After")
plt.ylabel("kWh/dia")
plt.xticks(rotation=45)
plt.legend()
plt.savefig(out_dir / "grafico_consumo_diario.png", bbox_inches='tight')
plt.close()

# ---------------------------------
# 7. PRINTAR RESULTADOS NO TERMINAL
# ---------------------------------

print("\n=== RESULTADOS DA SIMULAÇÃO IoT ===\n")
print(f"Consumo antes: {total_before:.2f} kWh/mês")
print(f"Consumo depois: {total_after:.2f} kWh/mês")
print(f"Economia: {economia_kwh:.2f} kWh/mês")
print(f"Redução de CO2: {economia_co2:.2f} kg/mês")
print(f"Economia financeira: R$ {economia_reais:.2f}/mês")
print("\nArquivos gerados em: /resultados_iot/\n")