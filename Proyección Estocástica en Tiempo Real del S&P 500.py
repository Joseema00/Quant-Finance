import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
import pandas as pd
import yfinance as yf
from datetime import timedelta 

# --- 1. CALIBRACIÓN  ---
TICKER = "^GSPC" 
print(f"--- INICIANDO CRONO-SIMULACIÓN: {TICKER} ---")

datos = yf.download(TICKER, start = "2020-01-01", end = "2025-11-19", progress=False)
if datos.empty: exit()

# Limpieza de datos (Tu seguridad habitual)
if isinstance(datos.columns, pd.MultiIndex):
    datos = datos.xs('Close', axis=1, level=0) if 'Close' in datos.columns.get_level_values(0) else datos['Close']
else:
    datos = datos['Close']

# A. Precio Inicial
precio_raw = datos.iloc[-1]
precio_actual = float(precio_raw.iloc[0]) if isinstance(precio_raw, pd.Series) else float(precio_raw)

# B. Fecha Inicial (El ancla temporal)
# Convertimos el indice de pandas a un objeto datetime de python
fecha_actual = datos.index[-1].to_pydatetime()

# C. Volatilidad
retornos_hist = np.log(datos / datos.shift(1))
vol_raw = retornos_hist.std()
vol_real = float(vol_raw.iloc[0]) if isinstance(vol_raw, pd.Series) else float(vol_raw)

print(f"Fecha de Inicio: {fecha_actual.strftime('%Y-%m-%d')}")
print(f"Precio: ${precio_actual:.2f}")

# --- 2. PREPARACIÓN GRÁFICA ---
plt.ion()
fig, (ax_price, ax_ret) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
fig.subplots_adjust(hspace=0.2, bottom=0.2) # Dejar espacio abajo para las fechas inclinadas

# Listas ahora guardan OBJETOS FECHA, no enteros
lista_fechas = [fecha_actual]
lista_precios = [precio_actual]
lista_retornos = [0.0]

# Formateador de fechas (Ej: "Nov 19")
date_fmt = mdates.DateFormatter('%b %d %Y')

# --- 3. BUCLE DE TIEMPO ---
while True:
    # === A. AVANZAR EL CALENDARIO ===
    # Simulamos que pasa 1 día por cada tick de la simulación
    # Si quisieras simular minutos, usarías: timedelta(minutes=1)
    fecha_actual = fecha_actual + timedelta(days=1)
    
    # === B. MATEMÁTICA (SDE) ===
    dWt = np.random.normal(0, 1)
    cambio_pct = 0.0 + vol_real * dWt # Drift 0 para simplificar
    nuevo_precio = precio_actual * (1 + cambio_pct)
    
    precio_actual = nuevo_precio
    
    # Guardar datos
    lista_fechas.append(fecha_actual)
    lista_precios.append(precio_actual)
    lista_retornos.append(cambio_pct * 100)

    # Mantener ventana de 100 días
    if len(lista_precios) > 100:
        lista_precios.pop(0)
        lista_fechas.pop(0)
        lista_retornos.pop(0)

    # === C. VISUALIZACIÓN ===
    ax_price.clear()
    ax_ret.clear()

    # --- PANEL PRECIO ---
    col_p = '#00ff00' if lista_precios[-1] > lista_precios[0] else '#ff0055'
    ax_price.plot(lista_fechas, lista_precios, color=col_p, lw=2)
    ax_price.set_title(f"{TICKER} PROYECCIÓN FUTURA | {fecha_actual.strftime('%Y-%m-%d')}", color='white', fontsize=12)
    ax_price.set_facecolor('#0f172a')
    ax_price.grid(True, color='gray', alpha=0.2)

    # --- PANEL RETORNOS ---
    colores_barras = ['#00ff00' if r > 0 else '#ff0055' for r in lista_retornos]
    
    ax_ret.bar(lista_fechas, lista_retornos, color=colores_barras, width=0.8)
    ax_ret.set_facecolor('black')
    ax_ret.grid(True, color='gray', alpha=0.2)
    ax_ret.axhline(vol_real*100, color='gray', linestyle='--', alpha=0.5)
    ax_ret.axhline(-vol_real*100, color='gray', linestyle='--', alpha=0.5)

    # === D. FORMATEO DEL EJE X (MAGIA DE FECHAS) ===
    # Aplicamos el formato de fecha al eje compartido
    ax_ret.xaxis.set_major_formatter(date_fmt)
    ax_ret.xaxis.set_major_locator(mdates.AutoDateLocator()) 
    
    # Rotar las fechas para que no se pisen
    fig.autofmt_xdate()

    # Estética General
    fig.patch.set_facecolor('#0f172a')
    ax_price.tick_params(axis='y', colors='white')
    ax_ret.tick_params(axis='y', colors='white')
    ax_ret.tick_params(axis='x', colors='white') 

    plt.pause(0.05)