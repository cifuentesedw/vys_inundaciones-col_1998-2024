"""
==============================================================================
 GENERADOR DE DASHBOARD INTERACTIVO — RIESGO HÍDRICO EN COLOMBIA 1998–2024
==============================================================================

 Este script construye un dashboard HTML interactivo tipo heatmap coroplético
 sobre el mapa de municipios de Colombia, con granularidad mensual y anual.

 El proceso se divide en 4 etapas principales:

   ETAPA 1 — Simplificación geométrica del GeoJSON de municipios
   ETAPA 2 — Agregación de datos de inundaciones por municipio, año y mes
   ETAPA 3 — Cálculo de estadísticas resumen y breakdown por tipo de evento
   ETAPA 4 — Ensamblaje del HTML con Leaflet.js y los datos embebidos

 Entradas requeridas:
   - CONSOLIDADO_EMERGENCIAS_1998-2024.csv  (dataset modelado, separador ;)
   - MunicipiosVeredas19MB.json             (GeoJSON de municipios de Colombia)

 Salida:
   - dashboard_inundaciones_colombia.html   (archivo autocontenido, ~2 MB)

 Dependencias: pandas, json, math, os (todas incluidas en Python estándar
 excepto pandas).

 Autor: Edwin Cifuentes - UNIANDES 2026
        github.com/cifuentesedw/vys_inundaciones-col_1998-2024
==============================================================================
"""

import pandas as pd
import json
import math
import os


# ============================================================================
# CONFIGURACIÓN DE ARCHIVOS DE ENTRADA Y SALIDA
# ============================================================================
# El analista debe ajustar estas rutas según la ubicación de sus archivos.

ARCHIVO_CSV = "CONSOLIDADO_EMERGENCIAS_1998-2024.csv"
ARCHIVO_GEOJSON = "MunicipiosVeredas19MB.json"
ARCHIVO_SALIDA = "inundaciones_colombia_1998-2024.html"


# ============================================================================
# ETAPA 1 — SIMPLIFICACIÓN GEOMÉTRICA DEL GEOJSON
# ============================================================================
# El GeoJSON original pesa ~19 MB con 508,924 coordenadas, lo cual haría
# que el navegador se congele al renderizar. Esta etapa reduce la complejidad
# geométrica mediante dos técnicas:
#
#   1. Algoritmo de Douglas-Peucker: elimina puntos redundantes en cada
#      polígono manteniendo la forma general. Se utiliza un epsilon de 0.008
#      grados (~890 metros), suficiente para un mapa coroplético nacional
#      pero preservando la silueta reconocible de cada municipio.
#
#   2. Reducción de precisión decimal: las coordenadas se redondean a 3
#      decimales (~111 metros de resolución), eliminando dígitos que no
#      aportan información visual a la escala del dashboard.
#
# El resultado pasa de 508,924 a ~33,800 coordenadas (reducción del 93%),
# y de 19 MB a ~0.7 MB. Además, se simplifican las propiedades de cada
# feature para conservar solo el código DIVIPOLA ('c') y el nombre ('n'),
# reduciendo aún más el peso del JSON embebido.
# ============================================================================

def _punto_distancia_a_linea(punto, inicio, fin):
    """
    Calcula la distancia perpendicular de un punto a una línea definida
    por dos extremos. Este cálculo es el núcleo del algoritmo Douglas-Peucker:
    el algoritmo identifica el punto más lejano de la línea simplificada
    y decide si debe conservarse o descartarse según un umbral (epsilon).
    """
    if inicio[0] == fin[0] and inicio[1] == fin[1]:
        return math.sqrt((punto[0] - inicio[0])**2 + (punto[1] - inicio[1])**2)

    dx = fin[0] - inicio[0]
    dy = fin[1] - inicio[1]
    t = max(0, min(1, ((punto[0] - inicio[0]) * dx + (punto[1] - inicio[1]) * dy) / (dx * dx + dy * dy)))
    proj_x = inicio[0] + t * dx
    proj_y = inicio[1] + t * dy
    return math.sqrt((punto[0] - proj_x)**2 + (punto[1] - proj_y)**2)


def _douglas_peucker(puntos, epsilon):
    """
    Implementación recursiva del algoritmo de Douglas-Peucker para
    simplificación de líneas. El algoritmo funciona así:

      1. Se traza una línea recta entre el primer y el último punto.
      2. Se busca el punto intermedio con mayor distancia perpendicular
         a esa línea.
      3. Si esa distancia supera el epsilon, se divide la línea en dos
         segmentos y se aplica el mismo proceso recursivamente.
      4. Si no supera el epsilon, todos los puntos intermedios se
         descartan, conservando solo los extremos.

    El epsilon controla la agresividad de la simplificación: valores más
    altos producen polígonos más simples (menos puntos) pero con mayor
    pérdida de detalle. Para este dashboard, 0.008 grados ofrece un
    buen equilibrio entre rendimiento y fidelidad visual.
    """
    if len(puntos) <= 2:
        return puntos

    distancia_max = 0
    indice_max = 0

    for i in range(1, len(puntos) - 1):
        d = _punto_distancia_a_linea(puntos[i], puntos[0], puntos[-1])
        if d > distancia_max:
            indice_max = i
            distancia_max = d

    if distancia_max > epsilon:
        # El punto más lejano supera el umbral: se conserva y se subdivide.
        izquierda = _douglas_peucker(puntos[:indice_max + 1], epsilon)
        derecha = _douglas_peucker(puntos[indice_max:], epsilon)
        return izquierda[:-1] + derecha
    else:
        # Todos los puntos intermedios están dentro del umbral: se descartan.
        return [puntos[0], puntos[-1]]


def _simplificar_anillo(anillo, epsilon=0.008):
    """
    Aplica Douglas-Peucker a un anillo de coordenadas (exterior o hueco
    de un polígono). Un anillo válido en GeoJSON requiere al menos 4
    puntos (triángulo cerrado). Si la simplificación produce menos de 4
    puntos, se conserva el anillo original para evitar geometrías inválidas.
    """
    simplificado = _douglas_peucker(anillo, epsilon)
    if len(simplificado) < 4:
        return anillo if len(anillo) >= 4 else anillo
    return simplificado


def _redondear_coordenadas(coords, precision=3):
    """
    Reduce recursivamente la precisión de las coordenadas a N decimales.
    Con 3 decimales la resolución es de ~111 metros en latitud, más que
    suficiente para un mapa coroplético nacional donde cada municipio
    se pinta de un solo color.
    """
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], precision), round(coords[1], precision)]
    return [_redondear_coordenadas(c, precision) for c in coords]


def _simplificar_geometria(geom, epsilon=0.008):
    """
    Simplifica una geometría GeoJSON (Polygon o MultiPolygon) aplicando
    Douglas-Peucker a cada anillo de cada polígono. Los MultiPolygon
    son comunes en municipios con islas o territorios discontinuos
    (por ejemplo, San Andrés y Providencia).
    """
    tipo = geom['type']
    coords = geom['coordinates']

    if tipo == 'Polygon':
        geom['coordinates'] = [_simplificar_anillo(anillo, epsilon) for anillo in coords]
    elif tipo == 'MultiPolygon':
        nuevos = []
        for poligono in coords:
            nuevos.append([_simplificar_anillo(anillo, epsilon) for anillo in poligono])
        geom['coordinates'] = nuevos

    return geom


def _contar_coordenadas(coords):
    """Cuenta recursivamente el total de puntos en una estructura de coordenadas."""
    if isinstance(coords[0], (int, float)):
        return 1
    return sum(_contar_coordenadas(c) for c in coords)


def simplificar_geojson(ruta_geojson):
    """
    Función principal de la Etapa 1. Carga el GeoJSON original de municipios,
    simplifica las geometrías y reduce las propiedades a solo código y nombre.

    Retorna el GeoJSON simplificado como string JSON compacto (sin espacios
    ni indentación) para minimizar el peso del HTML final.
    """
    print("=" * 70)
    print(" ETAPA 1 — Simplificación geométrica del GeoJSON")
    print("=" * 70)

    with open(ruta_geojson, 'r', encoding='utf-8') as f:
        geo = json.load(f)

    total_features = len(geo['features'])
    coords_antes = sum(_contar_coordenadas(feat['geometry']['coordinates']) for feat in geo['features'])

    print(f"  GeoJSON cargado: {total_features} municipios, {coords_antes:,} coordenadas")

    # Se procesa cada feature: simplificación geométrica + reducción de propiedades.
    for feat in geo['features']:
        feat['geometry'] = _simplificar_geometria(feat['geometry'], epsilon=0.008)
        feat['geometry']['coordinates'] = _redondear_coordenadas(feat['geometry']['coordinates'], 3)

        # Solo se conservan dos propiedades para el dashboard:
        #   'c' = código DIVIPOLA (para hacer join con los datos)
        #   'n' = nombre del municipio (para mostrar en el tooltip)
        feat['properties'] = {
            'c': feat['properties']['DPTOMPIO'],
            'n': feat['properties']['MPIO_CNMBR']
        }

    coords_despues = sum(_contar_coordenadas(feat['geometry']['coordinates']) for feat in geo['features'])
    reduccion = (1 - coords_despues / coords_antes) * 100

    print(f"  Coordenadas simplificadas: {coords_antes:,} → {coords_despues:,} ({reduccion:.1f}% reducción)")

    # Se serializa sin espacios para minimizar el tamaño.
    geo_str = json.dumps(geo, separators=(',', ':'))
    peso_mb = len(geo_str.encode('utf-8')) / 1e6
    print(f"  GeoJSON simplificado: {peso_mb:.1f} MB")

    return geo_str


# ============================================================================
# ETAPA 2 — AGREGACIÓN DE DATOS POR MUNICIPIO, AÑO Y MES
# ============================================================================
# El dataset modelado contiene 17,828 registros individuales de eventos.
# Para el dashboard, se necesitan datos agregados por cada combinación de
# municipio × año × mes. Además, se calculan totales intermedios:
#
#   - Por municipio × año (mes=0): total del año en cada municipio
#   - Por municipio × mes (año=0): total histórico de ese mes
#   - Por municipio (año=0, mes=0): gran total histórico
#
# Estas agregaciones permiten que el slider de año y el slider de mes
# funcionen de forma independiente o combinada. La estructura resultante
# es un diccionario anidado:
#
#   { "05001": { "0_0": {e:174, p:50000, ...},    ← total histórico
#                "2011_0": {e:14, p:3200, ...},    ← total año 2011
#                "2011_5": {e:3, p:800, ...},      ← mayo 2011
#                "0_5": {e:40, p:12000, ...},      ← todos los mayos
#                ... }, ... }
#
# Donde: e=eventos, p=personas afectadas, m=muertos, f=familias.
# ============================================================================

def agregar_datos(ruta_csv):
    """
    Función principal de la Etapa 2. Carga el CSV modelado y produce el
    diccionario de datos agregados que alimentará el mapa coroplético.
    """
    print("\n" + "=" * 70)
    print(" ETAPA 2 — Agregación de datos por municipio, año y mes")
    print("=" * 70)

    df = pd.read_csv(
        ruta_csv, encoding='utf-8-sig', sep=';', low_memory=False,
        dtype={'DIVIPOLA': str, 'CODIFICACIÓN SEGUN DIVIPOLA': str}
    )
    df['AÑO'] = df['AÑO'].fillna(0).astype(int)
    df['MES'] = df['MES'].fillna(0).astype(int)

    print(f"  Dataset cargado: {len(df):,} registros")
    print(f"  Municipios únicos: {df['DIVIPOLA'].nunique()}")
    print(f"  Rango temporal: {df['AÑO'].min()}–{df['AÑO'].max()}")

    # Campos que se agregan: conteo de eventos y suma de afectación.
    campos_agg = {
        'e': ('EVENTO', 'size'),
        'p': ('PERSONAS', 'sum'),
        'm': ('MUERTOS', 'sum'),
        'f': ('FAMILIAS', 'sum')
    }

    # -- Nivel 1: detalle completo (municipio × año × mes) --
    # Cada registro tiene año y mes, se agrupa para contar eventos
    # y sumar afectación en cada combinación única.
    agg_detalle = df.groupby(['DIVIPOLA', 'AÑO', 'MES']).agg(**campos_agg).reset_index()

    # -- Nivel 2: total por año (municipio × año, mes=0) --
    # Se utiliza cuando el slider de mes está en "Todos".
    agg_anual = df.groupby(['DIVIPOLA', 'AÑO']).agg(**campos_agg).reset_index()
    agg_anual['MES'] = 0

    # -- Nivel 3: total por mes histórico (municipio × mes, año=0) --
    # Se utiliza cuando el slider de año está en "Todos".
    agg_mensual = df.groupby(['DIVIPOLA', 'MES']).agg(**campos_agg).reset_index()
    agg_mensual['AÑO'] = 0

    # -- Nivel 4: gran total (municipio, año=0, mes=0) --
    # Se utiliza cuando ambos sliders están en "Todos".
    agg_total = df.groupby('DIVIPOLA').agg(**campos_agg).reset_index()
    agg_total['AÑO'] = 0
    agg_total['MES'] = 0

    # Se combinan los 4 niveles en un solo DataFrame.
    combinado = pd.concat([agg_detalle, agg_anual, agg_mensual, agg_total], ignore_index=True)
    for c in ['p', 'm', 'f']:
        combinado[c] = combinado[c].fillna(0).astype(int)

    # Se construye el diccionario anidado { divipola: { "año_mes": {e,p,m,f} } }.
    data_dict = {}
    for _, row in combinado.iterrows():
        codigo = row['DIVIPOLA']
        clave = f"{int(row['AÑO'])}_{int(row['MES'])}"
        if codigo not in data_dict:
            data_dict[codigo] = {}
        data_dict[codigo][clave] = {
            'e': int(row['e']),
            'p': int(row['p']),
            'm': int(row['m']),
            'f': int(row['f'])
        }

    data_str = json.dumps(data_dict, separators=(',', ':'))
    print(f"  Municipios con datos: {len(data_dict)}")
    print(f"  Combinaciones año×mes: {len(combinado):,}")
    print(f"  JSON de datos: {len(data_str.encode('utf-8')) / 1e6:.2f} MB")

    return data_str, df


# ============================================================================
# ETAPA 3 — ESTADÍSTICAS RESUMEN Y BREAKDOWN POR TIPO DE EVENTO
# ============================================================================
# Para cada combinación de año × mes, se calculan dos conjuntos de métricas:
#
#   A) Resumen global: total de eventos, personas, muertos y municipios
#      afectados. Estos alimentan las 4 tarjetas de estadísticas del
#      panel izquierdo del dashboard.
#
#   B) Breakdown por tipo: conteo de cada uno de los 4 tipos de evento
#      (INUNDACION, CRECIENTE SUBITA, TEMPORAL, AVENIDA TORRENCIAL).
#      Estos alimentan las barras proporcionales del panel de breakdown.
#
# Ambos usan la misma clave "año_mes" que los datos del mapa, lo que
# permite que todos los paneles se actualicen sincrónicamente al mover
# los sliders.
# ============================================================================

def calcular_estadisticas(df):
    """
    Función principal de la Etapa 3. Recorre todas las combinaciones
    posibles de año × mes y calcula las métricas globales y por tipo.
    """
    print("\n" + "=" * 70)
    print(" ETAPA 3 — Estadísticas resumen y breakdown por tipo de evento")
    print("=" * 70)

    años = [0] + list(range(1998, 2025))
    meses = list(range(0, 13))

    summary = {}
    evt_breakdown = {}
    combinaciones = 0

    for y in años:
        for m in meses:
            # Se selecciona el subconjunto correspondiente a la combinación.
            if y == 0 and m == 0:
                sub = df                                        # Todo el dataset
            elif y == 0:
                sub = df[df['MES'] == m]                        # Todos los años, mes específico
            elif m == 0:
                sub = df[df['AÑO'] == y]                        # Año específico, todos los meses
            else:
                sub = df[(df['AÑO'] == y) & (df['MES'] == m)]   # Año y mes específicos

            if len(sub) == 0:
                continue

            clave = f"{y}_{m}"
            combinaciones += 1

            # Resumen global: alimenta las tarjetas de estadísticas.
            summary[clave] = {
                'e': int(len(sub)),
                'p': int(sub['PERSONAS'].sum()) if sub['PERSONAS'].notna().any() else 0,
                'm': int(sub['MUERTOS'].sum()) if sub['MUERTOS'].notna().any() else 0,
                'mu': int(sub['DIVIPOLA'].nunique())
            }

            # Breakdown por tipo: alimenta las barras proporcionales.
            evt_breakdown[clave] = {
                'IN': int((sub['EVENTO'] == 'INUNDACION').sum()),
                'CS': int((sub['EVENTO'] == 'CRECIENTE SUBITA').sum()),
                'TE': int((sub['EVENTO'] == 'TEMPORAL').sum()),
                'AT': int((sub['EVENTO'] == 'AVENIDA TORRENCIAL').sum()),
            }

    summary_str = json.dumps(summary, separators=(',', ':'))
    evt_str = json.dumps(evt_breakdown, separators=(',', ':'))

    print(f"  Combinaciones año×mes calculadas: {combinaciones}")
    print(f"  JSON resumen: {len(summary_str.encode('utf-8')) / 1e3:.1f} KB")
    print(f"  JSON breakdown: {len(evt_str.encode('utf-8')) / 1e3:.1f} KB")

    return summary_str, evt_str


# ============================================================================
# ETAPA 4 — ENSAMBLAJE DEL DASHBOARD HTML
# ============================================================================
# El dashboard es un archivo HTML autocontenido que embebe:
#
#   - Leaflet.js (vía CDN) para el mapa interactivo
#   - El GeoJSON simplificado como variable JavaScript
#   - Los 3 JSONs de datos como variables JavaScript
#   - Todo el CSS y JavaScript inline
#
# Arquitectura visual del dashboard:
#
#   ┌─────────────────────────────────────────────────────────┐
#   │  HEADER: título + badge de período seleccionado         │
#   ├──────────┬──────────────────────────┬───────────────────┤
#   │  STATS   │                          │  SPARKLINE        │
#   │  (4 KPIs)│      MAPA COROPLÉTICO    │  (barras mensuales│
#   │          │      LEAFLET + GEOJSON   │   clicables)      │
#   │ BREAKDOWN│                          ├───────────────────┤
#   │ (4 tipos)│                          │  TOOLTIP (hover)  │
#   │          │                          ├───────────────────┤
#   │          │                          │  LEYENDA          │
#   ├──────────┴──────────────────────────┴───────────────────┤
#   │  CONTROLES: slider año + slider mes + botones play      │
#   └─────────────────────────────────────────────────────────┘
#
# Flujo de interacción:
#   1. El usuario mueve el slider de año y/o mes.
#   2. Se construye la clave "año_mes" correspondiente.
#   3. Se recorre el GeoJSON y para cada municipio se busca su dato
#      en DATA[divipola][clave].
#   4. Se calcula el color según una escala de 7 pasos (azul → rojo)
#      normalizada al máximo del período seleccionado.
#   5. Se actualizan simultáneamente: mapa, stats, breakdown, sparkline
#      y leyenda.
#
# La escala de color utiliza los siguientes umbrales sobre el ratio
# valor/máximo: 0.04, 0.10, 0.20, 0.35, 0.55, 0.75, 1.0.
# Los colores van de azul oscuro (pocos eventos) a rojo intenso
# (municipios más afectados), pasando por cian, verde, amarillo y naranja.
# ============================================================================

def ensamblar_html(geo_str, data_str, summary_str, evt_str):
    """
    Función principal de la Etapa 4. Inserta los datos en la plantilla
    HTML y escribe el archivo final.

    El HTML utiliza:
      - Leaflet 1.9.4 para el mapa (tiles de CartoDB Dark)
      - Google Fonts: DM Sans (UI) + JetBrains Mono (números/datos)
      - CSS Grid/Flexbox para el layout responsive
      - JavaScript vanilla para toda la lógica de interacción
    """
    print("\n" + "=" * 70)
    print(" ETAPA 4 — Ensamblaje del dashboard HTML")
    print("=" * 70)

    # ── PLANTILLA HTML ──
    # Se utiliza una f-string multilínea con las variables de datos
    # insertadas directamente como constantes JavaScript.
    # Las llaves dobles {{ }} escapan las llaves de JavaScript dentro
    # del f-string de Python.

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Riesgo Hídrico Colombia 1998–2024</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── RESET Y BASE ── */
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'DM Sans',sans-serif;background:#060b18;color:#c8d6e5;overflow:hidden;height:100vh;}}
#map{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:1;background:#060b18;}}
.leaflet-container{{background:#060b18!important;}}

/* ── HEADER: barra superior con título y badge de período ── */
.header{{
  position:absolute;top:0;left:0;right:0;z-index:1000;
  background:linear-gradient(180deg,rgba(6,11,24,0.97) 0%,rgba(6,11,24,0.8) 70%,transparent 100%);
  padding:14px 20px 28px;display:flex;align-items:flex-start;justify-content:space-between;
}}
.header-left h1{{
  font-size:19px;font-weight:700;letter-spacing:-0.3px;
  background:linear-gradient(135deg,#56d4f5 0%,#00acc1 60%,#00838f 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}}
.header-left .sub{{font-size:10.5px;color:#546e7a;letter-spacing:0.8px;text-transform:uppercase;margin-top:1px;}}
.period-badge{{
  background:rgba(0,172,193,0.08);border:1px solid rgba(0,172,193,0.25);
  border-radius:8px;padding:8px 14px;text-align:center;
}}
.period-badge .yr{{font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:#56d4f5;line-height:1;letter-spacing:-1px;}}
.period-badge .mo{{font-family:'JetBrains Mono',monospace;font-size:13px;color:#00acc1;margin-top:1px;}}

/* ── STATS: tarjetas de KPIs en el costado izquierdo ── */
.stats{{
  position:absolute;top:66px;left:16px;z-index:1000;
  display:flex;flex-direction:column;gap:6px;
}}
.scard{{
  background:rgba(8,14,30,0.92);border:1px solid rgba(86,212,245,0.1);
  border-radius:8px;padding:10px 14px;min-width:170px;backdrop-filter:blur(8px);
  transition:border-color 0.3s;
}}
.scard:hover{{border-color:rgba(86,212,245,0.3);}}
.scard .lab{{font-size:9.5px;color:#546e7a;text-transform:uppercase;letter-spacing:1.1px;margin-bottom:3px;}}
.scard .val{{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600;color:#56d4f5;}}
.scard .val.red{{color:#ef5350;}} .scard .val.amber{{color:#ffb74d;}} .scard .val.green{{color:#66bb6a;}}

/* ── BREAKDOWN: barras proporcionales por tipo de evento ── */
.breakdown{{
  position:absolute;top:66px;left:200px;z-index:1000;
  background:rgba(8,14,30,0.92);border:1px solid rgba(86,212,245,0.1);
  border-radius:8px;padding:12px 14px;backdrop-filter:blur(8px);min-width:190px;
}}
.breakdown .title{{font-size:9.5px;color:#546e7a;text-transform:uppercase;letter-spacing:1.1px;margin-bottom:8px;}}
.brow{{display:flex;align-items:center;gap:6px;margin-bottom:5px;}}
.brow .blabel{{font-size:10px;color:#78909c;width:75px;text-align:right;}}
.brow .bbar-bg{{flex:1;height:6px;background:rgba(255,255,255,0.04);border-radius:3px;overflow:hidden;position:relative;}}
.brow .bbar{{height:100%;border-radius:3px;transition:width 0.5s ease;}}
.brow .bcount{{font-family:'JetBrains Mono',monospace;font-size:10px;color:#90a4ae;width:42px;text-align:right;}}

/* ── SPARKLINE: distribución mensual del año seleccionado ── */
.sparkline-panel{{
  position:absolute;top:66px;right:16px;z-index:1000;
  background:rgba(8,14,30,0.92);border:1px solid rgba(86,212,245,0.1);
  border-radius:8px;padding:12px 14px;backdrop-filter:blur(8px);width:220px;
}}
.sparkline-panel .title{{font-size:9.5px;color:#546e7a;text-transform:uppercase;letter-spacing:1.1px;margin-bottom:8px;}}
.spark-row{{display:flex;align-items:flex-end;gap:2px;height:50px;}}
.spark-bar{{flex:1;border-radius:2px 2px 0 0;transition:all 0.4s ease;min-height:1px;position:relative;cursor:default;}}
.spark-bar:hover{{filter:brightness(1.3);}}
.spark-bar .spark-tip{{
  display:none;position:absolute;bottom:calc(100% + 4px);left:50%;transform:translateX(-50%);
  background:rgba(8,14,30,0.95);border:1px solid rgba(86,212,245,0.3);border-radius:4px;
  padding:3px 6px;font-size:9px;color:#56d4f5;font-family:'JetBrains Mono',monospace;white-space:nowrap;z-index:10;
}}
.spark-bar:hover .spark-tip{{display:block;}}
.spark-labels{{display:flex;gap:2px;margin-top:3px;}}
.spark-labels span{{flex:1;text-align:center;font-size:8px;color:#455a64;font-family:'JetBrains Mono',monospace;}}
.spark-labels span.active{{color:#56d4f5;font-weight:600;}}

/* ── TOOLTIP: información del municipio al hacer hover ── */
.info-tt{{
  position:absolute;top:200px;right:16px;z-index:1000;
  background:rgba(8,14,30,0.94);border:1px solid rgba(86,212,245,0.2);
  border-radius:8px;padding:14px;min-width:210px;backdrop-filter:blur(8px);display:none;
}}
.info-tt.visible{{display:block;}}
.info-tt .mn{{font-size:15px;font-weight:700;color:#e0e6f0;margin-bottom:1px;}}
.info-tt .mc{{font-size:10px;color:#546e7a;margin-bottom:8px;}}
.info-tt .dr{{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.04);}}
.info-tt .dr:last-child{{border:none;}}
.info-tt .dl{{font-size:10.5px;color:#78909c;}} .info-tt .dv{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#56d4f5;}}
.info-tt .dv.red{{color:#ef5350;}}

/* ── LEYENDA: escala de color del mapa ── */
.legend{{
  position:absolute;bottom:160px;right:16px;z-index:1000;
  background:rgba(8,14,30,0.92);border:1px solid rgba(86,212,245,0.1);
  border-radius:8px;padding:12px 14px;backdrop-filter:blur(8px);
}}
.legend .lt{{font-size:9.5px;color:#546e7a;text-transform:uppercase;letter-spacing:1.1px;margin-bottom:6px;}}
.lrow{{display:flex;align-items:center;gap:7px;font-size:10.5px;color:#78909c;margin-bottom:3px;}}
.lbox{{width:18px;height:10px;border-radius:2px;flex-shrink:0;}}

/* ── CONTROLES: sliders de año y mes + botones de animación ── */
.controls{{
  position:absolute;bottom:0;left:0;right:0;z-index:1000;
  background:linear-gradient(0deg,rgba(6,11,24,0.97) 0%,rgba(6,11,24,0.85) 65%,transparent 100%);
  padding:28px 20px 16px;
}}
.sliders-wrap{{max-width:900px;margin:0 auto;}}
.slider-group{{margin-bottom:8px;}}
.slider-group label{{font-size:9.5px;color:#546e7a;text-transform:uppercase;letter-spacing:1.2px;display:block;margin-bottom:4px;}}
.slider-row{{display:flex;align-items:center;gap:10px;}}
.slider-row input[type=range]{{flex:1;}}
.slider-row .play-btn{{
  width:30px;height:30px;border-radius:50%;border:1.5px solid rgba(86,212,245,0.3);
  background:rgba(8,14,30,0.9);color:#56d4f5;cursor:pointer;display:flex;
  align-items:center;justify-content:center;font-size:11px;transition:all 0.2s;flex-shrink:0;
}}
.slider-row .play-btn:hover{{background:rgba(86,212,245,0.12);border-color:#56d4f5;}}
input[type=range]{{
  -webkit-appearance:none;height:3px;border-radius:2px;outline:none;cursor:pointer;
  background:linear-gradient(90deg,#0d47a1,#00838f,#56d4f5,#ffb74d,#ef5350);
}}
input[type=range]::-webkit-slider-thumb{{
  -webkit-appearance:none;width:16px;height:16px;background:#56d4f5;border-radius:50%;cursor:pointer;
  box-shadow:0 0 14px rgba(86,212,245,0.4),0 0 4px rgba(86,212,245,0.7);transition:transform 0.15s;
}}
input[type=range]::-webkit-slider-thumb:hover{{transform:scale(1.25);}}
input[type=range]::-moz-range-thumb{{
  width:16px;height:16px;background:#56d4f5;border-radius:50%;cursor:pointer;border:none;
  box-shadow:0 0 14px rgba(86,212,245,0.4);
}}
.tick-labels{{display:flex;justify-content:space-between;margin-top:3px;padding:0 2px;}}
.tick-labels span{{font-size:9px;color:#37474f;font-family:'JetBrains Mono',monospace;}}
.tick-labels span.active{{color:#56d4f5;font-weight:600;}}

/* ── OVERRIDES DE LEAFLET: se ajustan los controles de zoom al tema oscuro ── */
.leaflet-control-attribution{{display:none!important;}}
.leaflet-control-zoom{{border:none!important;}}
.leaflet-control-zoom a{{
  background:rgba(8,14,30,0.9)!important;color:#56d4f5!important;
  border:1px solid rgba(86,212,245,0.15)!important;width:28px!important;height:28px!important;
  line-height:28px!important;font-size:14px!important;
}}
.leaflet-control-zoom a:hover{{background:rgba(86,212,245,0.12)!important;}}

/* ── RESPONSIVE: en pantallas pequeñas se oculta el breakdown ── */
@media(max-width:900px){{
  .breakdown{{display:none;}} .sparkline-panel{{width:160px;}}
  .stats{{gap:4px;}} .scard{{padding:8px 10px;min-width:130px;}} .scard .val{{font-size:16px;}}
}}
</style>
</head>
<body>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- ESTRUCTURA HTML DEL DASHBOARD                                      -->
<!-- Cada sección tiene un ID que el JavaScript actualiza dinámicamente  -->
<!-- ═══════════════════════════════════════════════════════════════════ -->

<!-- Contenedor del mapa Leaflet -->
<div id="map"></div>

<!-- Barra superior: título del proyecto y badge del período seleccionado -->
<div class="header">
  <div class="header-left">
    <h1>🌊 Riesgo Hídrico en Colombia</h1>
    <div class="sub">Inundaciones · Crecientes súbitas · Avenidas torrenciales · Temporales · UNGRD 1998–2024</div>
  </div>
  <div class="period-badge">
    <div class="yr" id="badge-yr">1998–2024</div>
    <div class="mo" id="badge-mo">Todos los meses</div>
  </div>
</div>

<!-- Panel de estadísticas globales (se actualiza con cada cambio de slider) -->
<div class="stats">
  <div class="scard"><div class="lab">Eventos</div><div class="val" id="st-e">-</div></div>
  <div class="scard"><div class="lab">Personas afectadas</div><div class="val amber" id="st-p">-</div></div>
  <div class="scard"><div class="lab">Fallecidos</div><div class="val red" id="st-m">-</div></div>
  <div class="scard"><div class="lab">Municipios</div><div class="val green" id="st-mu">-</div></div>
</div>

<!-- Panel de breakdown por tipo de evento hídrico -->
<div class="breakdown" id="breakdown">
  <div class="title">Tipo de evento</div>
  <div class="brow"><span class="blabel">Inundación</span><div class="bbar-bg"><div class="bbar" id="bb-in" style="background:#0288d1;width:0"></div></div><span class="bcount" id="bc-in">-</span></div>
  <div class="brow"><span class="blabel">Crec. súbita</span><div class="bbar-bg"><div class="bbar" id="bb-cs" style="background:#f9a825;width:0"></div></div><span class="bcount" id="bc-cs">-</span></div>
  <div class="brow"><span class="blabel">Temporal</span><div class="bbar-bg"><div class="bbar" id="bb-te" style="background:#66bb6a;width:0"></div></div><span class="bcount" id="bc-te">-</span></div>
  <div class="brow"><span class="blabel">Av. torrencial</span><div class="bbar-bg"><div class="bbar" id="bb-at" style="background:#ef5350;width:0"></div></div><span class="bcount" id="bc-at">-</span></div>
</div>

<!-- Sparkline mensual: muestra los 12 meses como barras clicables -->
<div class="sparkline-panel">
  <div class="title" id="spark-title">Estacionalidad mensual</div>
  <div class="spark-row" id="spark-bars"></div>
  <div class="spark-labels" id="spark-labels"></div>
</div>

<!-- Tooltip: aparece al hacer hover sobre un municipio del mapa -->
<div class="info-tt" id="tooltip">
  <div class="mn" id="tt-n">-</div>
  <div class="mc" id="tt-c">-</div>
  <div class="dr"><span class="dl">Eventos</span><span class="dv" id="tt-e">-</span></div>
  <div class="dr"><span class="dl">Personas</span><span class="dv" id="tt-p">-</span></div>
  <div class="dr"><span class="dl">Familias</span><span class="dv" id="tt-f">-</span></div>
  <div class="dr"><span class="dl">Fallecidos</span><span class="dv red" id="tt-m">-</span></div>
</div>

<!-- Leyenda: escala de color dinámica que se ajusta al rango del período -->
<div class="legend">
  <div class="lt">Eventos de riesgo hídrico</div>
  <div id="legend-items"></div>
</div>

<!-- Panel de controles: dos sliders (año y mes) con botones de animación -->
<div class="controls">
  <div class="sliders-wrap">
    <div class="slider-group">
      <label>Año</label>
      <div class="slider-row">
        <input type="range" id="sliderY" min="0" max="27" value="0" step="1">
        <button class="play-btn" id="playY" title="Animar años">▶</button>
      </div>
      <div class="tick-labels" id="ticksY"></div>
    </div>
    <div class="slider-group">
      <label>Mes</label>
      <div class="slider-row">
        <input type="range" id="sliderM" min="0" max="12" value="0" step="1">
        <button class="play-btn" id="playM" title="Animar meses">▶</button>
      </div>
      <div class="tick-labels" id="ticksM"></div>
    </div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// DATOS EMBEBIDOS
// Los 4 objetos JSON se insertan directamente en el HTML como constantes
// JavaScript. Esto hace que el dashboard sea completamente autocontenido
// (no requiere servidor ni archivos externos para los datos).
// ═══════════════════════════════════════════════════════════════════════

const GEO = {geo_str};       // GeoJSON simplificado de municipios
const DATA = {data_str};     // Datos agregados: {{divipola: {{"año_mes": {{e,p,m,f}}}} }}
const STATS = {summary_str}; // Resumen global: {{"año_mes": {{e,p,m,mu}}}}
const EVT = {evt_str};       // Breakdown por tipo: {{"año_mes": {{IN,CS,TE,AT}}}}

// ═══════════════════════════════════════════════════════════════════════
// CONSTANTES Y ESTADO
// ═══════════════════════════════════════════════════════════════════════

// Arreglo de años: posición 0 = "Todos" (codificado como año 0),
// posiciones 1-27 = años 1998 a 2024.
const YEARS = [0,...Array.from({{length:27}},(_,i)=>1998+i)];

// Nombres de meses: posición 0 = "Todos".
const MNAMES = ['Todos','Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const MFULL = ['Todos los meses','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

// Estado actual de los sliders.
let curY = 0, curM = 0;

// ═══════════════════════════════════════════════════════════════════════
// ESCALA DE COLOR
// Se utiliza una escala secuencial de 7 pasos que va de azul oscuro
// (baja incidencia) a rojo intenso (alta incidencia). La normalización
// se hace contra el máximo del período seleccionado, no contra un valor
// fijo, lo que permite que la escala se adapte automáticamente.
// ═══════════════════════════════════════════════════════════════════════

function getColor(v, mx) {{
  if (!v || v===0) return 'transparent';
  const r = Math.min(v/Math.max(mx,1),1);
  if(r<=0.04) return '#0a1929';   // Azul muy oscuro (1-2 eventos)
  if(r<=0.10) return '#0d47a1';   // Azul profundo
  if(r<=0.20) return '#0277bd';   // Azul medio
  if(r<=0.35) return '#00897b';   // Verde azulado
  if(r<=0.55) return '#f9a825';   // Amarillo (zona de transición)
  if(r<=0.75) return '#ef6c00';   // Naranja intenso
  return '#c62828';               // Rojo (máxima incidencia)
}}

// Calcula el valor máximo de eventos para una combinación año_mes dada.
// Se usa para normalizar la escala de color.
function getMax(y,m) {{
  const k = y+'_'+m;
  let mx=0;
  for(const c in DATA){{const d=DATA[c][k]; if(d&&d.e>mx) mx=d.e;}}
  return mx;
}}

// ═══════════════════════════════════════════════════════════════════════
// INICIALIZACIÓN DEL MAPA LEAFLET
// Se usan tiles de CartoDB Dark (sin etiquetas) como base, y una segunda
// capa de solo etiquetas encima con un z-index superior. Esto permite
// que los nombres de ciudades se lean sobre los polígonos coloreados.
// ═══════════════════════════════════════════════════════════════════════

const map = L.map('map',{{center:[4.5,-73.5],zoom:6,zoomControl:true,minZoom:5,maxZoom:12}});

// Capa base: mapa oscuro sin etiquetas.
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_nolabels/{{z}}/{{x}}/{{y}}{{r}}.png',{{
  subdomains:'abcd',maxZoom:19
}}).addTo(map);

// Capa de etiquetas: se coloca en un pane separado con z-index alto
// y pointer-events desactivados para que no interfiera con el hover.
const lp=map.createPane('labels');
lp.style.zIndex=650;
lp.style.pointerEvents='none';
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_only_labels/{{z}}/{{x}}/{{y}}{{r}}.png',{{
  subdomains:'abcd',maxZoom:19,pane:'labels'
}}).addTo(map);

// ═══════════════════════════════════════════════════════════════════════
// CAPA GEOJSON: POLÍGONOS MUNICIPALES
// Cada polígono se colorea según el número de eventos del municipio
// en el período seleccionado. El estilo se recalcula cada vez que
// el usuario mueve un slider.
// ═══════════════════════════════════════════════════════════════════════

let geoLayer;

// Función de estilo: se invoca para cada feature del GeoJSON.
function styleF(f){{
  const c=f.properties.c, k=curY+'_'+curM;
  const d=DATA[c]&&DATA[c][k]; const v=d?d.e:0; const mx=getMax(curY,curM);
  return{{
    fillColor:getColor(v,mx),
    weight:0.4,            // Grosor del borde entre municipios
    opacity:0.5,           // Opacidad del borde
    color:'#0d1b3e',       // Color del borde (azul muy oscuro)
    fillOpacity:v>0?0.85:0.12  // Municipios sin datos son casi transparentes
  }};
}}

// Eventos de hover: al pasar el mouse sobre un municipio, se resalta
// el borde y se muestra el tooltip con los datos del período seleccionado.
function onEach(f,layer){{
  layer.on({{
    mouseover(e){{
      const c=f.properties.c,n=f.properties.n,k=curY+'_'+curM;
      const d=DATA[c]&&DATA[c][k];
      document.getElementById('tt-n').textContent=n;
      document.getElementById('tt-c').textContent='DIVIPOLA: '+c;
      document.getElementById('tt-e').textContent=d?d.e.toLocaleString('es-CO'):'0';
      document.getElementById('tt-p').textContent=d?d.p.toLocaleString('es-CO'):'0';
      document.getElementById('tt-f').textContent=d?d.f.toLocaleString('es-CO'):'0';
      document.getElementById('tt-m').textContent=d?d.m.toLocaleString('es-CO'):'0';
      document.getElementById('tooltip').classList.add('visible');
      e.target.setStyle({{weight:2,color:'#56d4f5',fillOpacity:0.95}});
      e.target.bringToFront();
    }},
    mouseout(e){{
      geoLayer.resetStyle(e.target);
      document.getElementById('tooltip').classList.remove('visible');
    }}
  }});
}}

// Se agrega la capa GeoJSON al mapa.
geoLayer = L.geoJSON(GEO,{{style:styleF,onEachFeature:onEach}}).addTo(map);

// ═══════════════════════════════════════════════════════════════════════
// FUNCIÓN DE ACTUALIZACIÓN GLOBAL
// Esta función se ejecuta cada vez que el usuario interactúa con un
// slider o un botón. Actualiza todos los paneles simultáneamente.
// ═══════════════════════════════════════════════════════════════════════

function update(){{
  const k=curY+'_'+curM;

  // 1. Badge de período: muestra el año y mes seleccionados.
  document.getElementById('badge-yr').textContent = curY==0?'1998–2024':String(curY);
  document.getElementById('badge-mo').textContent = MFULL[curM];

  // 2. Tarjetas de estadísticas globales.
  const s=STATS[k]||{{e:0,p:0,m:0,mu:0}};
  document.getElementById('st-e').textContent=(s.e||0).toLocaleString('es-CO');
  document.getElementById('st-p').textContent=(s.p||0).toLocaleString('es-CO');
  document.getElementById('st-m').textContent=(s.m||0).toLocaleString('es-CO');
  document.getElementById('st-mu').textContent=(s.mu||0).toLocaleString('es-CO');

  // 3. Barras de breakdown por tipo de evento.
  const ev=EVT[k]||{{IN:0,CS:0,TE:0,AT:0}};
  const mx2=Math.max(ev.IN,ev.CS,ev.TE,ev.AT,1);
  document.getElementById('bb-in').style.width=(ev.IN/mx2*100)+'%'; document.getElementById('bc-in').textContent=ev.IN.toLocaleString('es-CO');
  document.getElementById('bb-cs').style.width=(ev.CS/mx2*100)+'%'; document.getElementById('bc-cs').textContent=ev.CS.toLocaleString('es-CO');
  document.getElementById('bb-te').style.width=(ev.TE/mx2*100)+'%'; document.getElementById('bc-te').textContent=ev.TE.toLocaleString('es-CO');
  document.getElementById('bb-at').style.width=(ev.AT/mx2*100)+'%'; document.getElementById('bc-at').textContent=ev.AT.toLocaleString('es-CO');

  // 4. Leyenda dinámica: se recalculan los umbrales según el máximo actual.
  const mxL=getMax(curY,curM);
  const steps=[[0,'Sin datos','rgba(255,255,255,0.04)'],[Math.max(1,Math.round(mxL*0.04)),null,'#0a1929'],
    [Math.round(mxL*0.1),null,'#0d47a1'],[Math.round(mxL*0.2),null,'#0277bd'],
    [Math.round(mxL*0.35),null,'#00897b'],[Math.round(mxL*0.55),null,'#f9a825'],
    [Math.round(mxL*0.75),null,'#ef6c00'],[mxL,null,'#c62828']];
  document.getElementById('legend-items').innerHTML=steps.map(([v,l,c])=>{{
    const t=l||(v<=1?'1':'≤ '+v);
    return '<div class="lrow"><div class="lbox" style="background:'+c+'"></div>'+t+'</div>';
  }}).join('');

  // 5. Sparkline mensual.
  updateSparkline();

  // 6. Mapa: se recalcula el estilo de todos los polígonos.
  geoLayer.setStyle(styleF);

  // 7. Resaltado de ticks activos en los sliders.
  document.querySelectorAll('#ticksY span').forEach((s,i)=>s.classList.toggle('active',i===parseInt(document.getElementById('sliderY').value)));
  document.querySelectorAll('#ticksM span').forEach((s,i)=>s.classList.toggle('active',i===curM));
}}

// ═══════════════════════════════════════════════════════════════════════
// SPARKLINE MENSUAL
// Muestra una barra por cada mes del año seleccionado. Las barras son
// clicables: al hacer clic en una barra, el slider de mes salta a ese
// mes. La barra del mes actualmente seleccionado se resalta en cian.
// ═══════════════════════════════════════════════════════════════════════

function updateSparkline(){{
  const bars=document.getElementById('spark-bars');
  const lbls=document.getElementById('spark-labels');
  const title=document.getElementById('spark-title');

  // El título cambia según si se ve un año específico o el acumulado.
  title.textContent = curY==0?'Estacionalidad mensual (todos los años)':'Distribución mensual '+curY;

  // Se obtiene el total de eventos para cada mes del año seleccionado.
  let vals=[];
  for(let m=1;m<=12;m++){{
    const sk=curY+'_'+m;
    const st=STATS[sk];
    vals.push(st?st.e:0);
  }}

  // Se normalizan las alturas contra el mes con más eventos.
  const mx=Math.max(...vals,1);
  bars.innerHTML=vals.map((v,i)=>{{
    const h=Math.max(v/mx*100,1);
    const active=curM===(i+1);
    const bg=active?'#56d4f5':(v>0?'rgba(0,172,193,0.5)':'rgba(255,255,255,0.04)');
    return '<div class="spark-bar" style="height:'+h+'%;background:'+bg+'" data-m="'+(i+1)+'"><div class="spark-tip">'+MNAMES[i+1]+': '+v.toLocaleString('es-CO')+'</div></div>';
  }}).join('');

  // Etiquetas de mes (primera letra).
  lbls.innerHTML=MNAMES.slice(1).map((n,i)=>{{
    const active=curM===(i+1);
    return '<span'+(active?' class="active"':'')+'>'+n.charAt(0)+'</span>';
  }}).join('');

  // Se asignan los eventos de clic a cada barra del sparkline.
  bars.querySelectorAll('.spark-bar').forEach(b=>{{
    b.addEventListener('click',()=>{{
      const m=parseInt(b.dataset.m);
      curM=m;
      document.getElementById('sliderM').value=m;
      update();
    }});
  }});
}}

// ═══════════════════════════════════════════════════════════════════════
// ETIQUETAS DE LOS SLIDERS
// Se generan dinámicamente: el slider de años muestra "Todo" en la
// primera posición y luego los dos últimos dígitos de cada año
// (solo para años divisibles por 5, más 1998 y 2024).
// El slider de meses muestra los nombres abreviados de cada mes.
// ═══════════════════════════════════════════════════════════════════════

document.getElementById('ticksY').innerHTML=YEARS.map((y,i)=>{{
  const l=y===0?'Todo':(y%5===0||y===1998||y===2024?String(y).slice(2):'');
  return '<span>'+l+'</span>';
}}).join('');

document.getElementById('ticksM').innerHTML=MNAMES.map(n=>'<span>'+n+'</span>').join('');

// ═══════════════════════════════════════════════════════════════════════
// EVENTOS DE LOS SLIDERS
// Cada slider actualiza la variable de estado correspondiente y luego
// invoca la función update() para refrescar todos los paneles.
// ═══════════════════════════════════════════════════════════════════════

document.getElementById('sliderY').addEventListener('input',function(){{
  curY=YEARS[parseInt(this.value)];
  update();
}});

document.getElementById('sliderM').addEventListener('input',function(){{
  curM=parseInt(this.value);
  update();
}});

// ═══════════════════════════════════════════════════════════════════════
// BOTONES DE ANIMACIÓN (PLAY)
// Cada botón Play inicia un setInterval que avanza el slider
// correspondiente cada 700ms. Al llegar al final, se detiene
// automáticamente. Presionar de nuevo pausa la animación.
// ═══════════════════════════════════════════════════════════════════════

function makePlayer(btnId, sliderId, maxVal, setCur){{
  let playing=false, intv;
  document.getElementById(btnId).addEventListener('click',function(){{
    if(playing){{
      clearInterval(intv);
      this.textContent='▶';
      playing=false;
      return;
    }}
    playing=true;
    this.textContent='⏸';
    let idx=parseInt(document.getElementById(sliderId).value);
    if(idx>=maxVal) idx=0;
    intv=setInterval(()=>{{
      idx++;
      if(idx>maxVal){{
        clearInterval(intv);
        document.getElementById(btnId).textContent='▶';
        playing=false;
        idx=0;
      }}
      document.getElementById(sliderId).value=idx;
      setCur(idx);
      update();
    }},700);
  }});
}}

// Se inicializan los dos botones de animación.
makePlayer('playY','sliderY',27,(i)=>{{curY=YEARS[i];}});
makePlayer('playM','sliderM',12,(i)=>{{curM=i;}});

// ═══════════════════════════════════════════════════════════════════════
// INICIALIZACIÓN: se renderiza el estado inicial (todos los años,
// todos los meses) al cargar la página.
// ═══════════════════════════════════════════════════════════════════════
update();
</script>
</body>
</html>'''

    # Se escribe el archivo HTML final.
    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        f.write(html)

    peso = os.path.getsize(ARCHIVO_SALIDA) / 1e6
    print(f"  Dashboard generado: {ARCHIVO_SALIDA} ({peso:.1f} MB)")


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================
# El script ejecuta las 4 etapas en secuencia. Si algún archivo de entrada
# no existe, se muestra un mensaje de error descriptivo y se detiene.
# ============================================================================

def main():
    """
    Orquesta la ejecución completa del pipeline de generación del dashboard.
    Las 4 etapas son independientes entre sí en cuanto a lógica, pero
    comparten datos a través de los retornos de cada función.
    """
    print("\n" + "▓" * 70)
    print("  GENERADOR DE DASHBOARD — RIESGO HÍDRICO EN COLOMBIA 1998–2024")
    print("▓" * 70)

    # Verificación de archivos de entrada.
    for archivo, descripcion in [(ARCHIVO_CSV, "CSV modelado"), (ARCHIVO_GEOJSON, "GeoJSON municipios")]:
        if not os.path.exists(archivo):
            print(f"\n  ❌ ERROR: No se encontró el archivo {descripcion}:")
            print(f"     → {archivo}")
            print(f"     Ubicación actual: {os.getcwd()}")
            return

    # Etapa 1: se simplifica el GeoJSON para que el navegador lo renderice
    # sin problemas de rendimiento.
    geo_str = simplificar_geojson(ARCHIVO_GEOJSON)

    # Etapa 2: se agregan los datos de inundaciones por municipio, año y mes
    # para alimentar el mapa coroplético.
    data_str, df = agregar_datos(ARCHIVO_CSV)

    # Etapa 3: se calculan las métricas globales y el breakdown por tipo
    # de evento para los paneles informativos.
    summary_str, evt_str = calcular_estadisticas(df)

    # Etapa 4: se ensambla el HTML final con todos los datos embebidos
    # y la lógica de interacción en JavaScript.
    ensamblar_html(geo_str, data_str, summary_str, evt_str)

    print("\n" + "▓" * 70)
    print(f"  ✅ Dashboard listo: {ARCHIVO_SALIDA}")
    print(f"     Abrirlo en un navegador web para visualizar.")
    print("▓" * 70 + "\n")


if __name__ == "__main__":
    main()
