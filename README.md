# Vulnerabilidad y Severidad de Inundaciones en Colombia (1998–2024)

## Autores

| Nombre | Correo electrónico |
|---|---|
| Edwin Alexander Cifuentes Bastidas | ea.cifuentes@uniandes.edu.co |
| Luis Fernando Moreta Cruz | l.moreta@hotmail.com |
| María del Pilar Muñoz | md.munoz@uniandes.edu.co |
| Erick Andrés Pérez Álvarez | ea.pereza1@uniandes.edu.co |

---

## Resumen

Este repositorio contiene un conjunto de datos integrado para el análisis de vulnerabilidad y severidad de eventos de inundación en Colombia durante el período 1998–2024. El dataset resulta de la consolidación, limpieza e integración de fuentes de datos públicas del Estado colombiano: registros de emergencias de la Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD) para los años 1998 a 2024. El repositorio incluye además datos geoespaciales de referencia a nivel municipal y de vereda, así como la tabla de codificación territorial DIVIPOLA del Departamento Administrativo Nacional de Estadística (DANE).

---

## Contenido del repositorio

| Archivo | Descripción | Fuente | Registros |
|---|---|---|---|
| `CONSOLIDADO_EMERGENCIAS_1998-2024.csv` | Registros de emergencias por fenómenos naturales y antrópicos no intencionales en Colombia | UNGRD | 72.807 filas × 45 cols |
| `DIVIPOLA.csv` | Tabla de referencia de códigos de división político-administrativa | DANE | 1.122 filas × 5 cols |
| `MunicipiosVeredas19MB.json` | Geometrías vectoriales de municipios y veredas de Colombia | IGAC / DANE | 1.122 features |
| `Modelado Dataset Emergencias.pdf` | Documento técnico del proceso de construcción y modelado del dataset | Cifuentes, Moreta, Muñoz y Pérez | — |

---

## Fuentes de datos

### 1. Dataset de emergencias — UNGRD

| Campo | Detalle |
|---|---|
| **Productor** | Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD) — Subdirección para el Manejo de Desastres |
| **Portal de datos abiertos** | https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Emergencias-UNGRD-/wwkg-r6te/about_data |
| **Portal institucional** | https://portal.gestiondelriesgo.gov.co/Paginas/Consolidado-Atencion-de-Emergencias.aspx |
| **Cobertura temporal** | 1 de enero de 1998 – 31 de diciembre de 2024 |
| **Cobertura geográfica** | Nacional (32 departamentos) |
| **Granularidad** | Evento por municipio |
| **Frecuencia de actualización** | Anual |
| **Licencia original** | Dominio Público — publicado en cumplimiento de la Ley 1712 de 2014 |

El dataset de emergencias contiene el registro de eventos naturales o antrópicos no intencionales reportados diariamente por los Consejos Departamentales y Municipales de Gestión del Riesgo de Desastres (CDGRD/CMGRD), la Defensa Civil Colombiana, la Cruz Roja Colombiana y el Sistema Nacional de Bomberos.

Los reportes originales son publicados en archivos anuales de formato `.xls`. Para la construcción del consolidado se unificaron los 27 archivos anuales disponibles para el período 1998–2024. Este proceso implicó resolver múltiples inconsistencias estructurales descritas en la sección [Proceso de modelado y limpieza](#proceso-de-modelado-y-limpieza).

#### Variables principales del dataset de emergencias

| Variable | Descripción | Tipo |
|---|---|---|
| `FECHA` | Fecha del evento | datetime |
| `DEPARTAMENTO` | Departamento donde ocurrió el evento | string |
| `MUNICIPIO` | Municipio donde ocurrió el evento | string |
| `EVENTO` | Clasificación del fenómeno (36+ tipos) | string |
| `CODIFICACIÓN SEGUN DIVIPOLA` | Código DIVIPOLA del municipio (DANE) | string |
| `MUERTOS` | Número de víctimas mortales | int |
| `HERIDOS` | Número de personas heridas | int |
| `DESAPA.` | Número de personas desaparecidas | int |
| `PERSONAS` | Número de personas afectadas | int |
| `FAMILIAS` | Número de familias afectadas | int |
| `VIV.DESTRU.` | Viviendas destruidas | int |
| `VIV.AVER.` | Viviendas averiadas | int |
| `VIAS` | Vías afectadas | int |
| `PTES.VEHIC.` | Puentes vehiculares dañados | int |
| `PTES.PEAT.` | Puentes peatonales dañados | int |
| `ACUED.` | Acueductos afectados | int |
| `ALCANT.` | Alcantarillados afectados | int |
| `C. SALUD` | Centros de salud afectados | int |
| `C.EDUCAT.` | Centros educativos afectados | int |
| `C.COMUNIT.` | Centros comunitarios afectados | int |
| `HECTAREAS` | Hectáreas afectadas | int |
| `RECURSOS EJECUTADOS` | Recursos del FNGRD ejecutados (COP) | float |
| `Otros` | Descripción del evento | string |

### 2. DIVIPOLA — DANE

| Campo | Detalle |
|---|---|
| **Productor** | Departamento Administrativo Nacional de Estadística (DANE) |
| **Descripción** | División Político-Administrativa de Colombia. Sistema de codificación única de departamentos, distritos y municipios del territorio nacional, administrado por el DANE desde 1953. |
| **Referencia normativa** | Constitución Política de Colombia de 1991, artículos sobre organización territorial |
| **Documentación** | https://www.dane.gov.co/files/investigaciones/divipola/divipola2007.pdf |
| **Licencia** | Datos abiertos del Estado colombiano — CC BY-SA 4.0 |

Tabla de referencia con los códigos de la División Político-Administrativa de Colombia (DANE). Permite cruzar el código DIVIPOLA del dataset con nombres oficiales de departamentos y municipios.

### 3. GeoJSON de municipios y veredas

| Campo | Detalle |
|---|---|
| **Productor** | Instituto Geográfico Agustín Codazzi (IGAC) / DANE |
| **Descripción** | Geometrías vectoriales de polígonos de municipios y veredas de Colombia para análisis espacial y cartografía temática |
| **Formato** | GeoJSON |
| **Tamaño** | ~19 MB |
| **Licencia** | Datos abiertos del Estado colombiano — CC BY-SA 4.0 |

Archivo tipo GeoJSON con los polígonos de los 1.121 municipios de Colombia. Propiedades por feature:

| Propiedad | Descripción | Ejemplo |
|---|---|---|
| `DPTOMPIO` | Código concatenado depto+municipio (5 dígitos) | `05001` |
| `DPTO_CCDGO` | Código departamento (2 dígitos) | `05` |
| `MPIO_CCDGO` | Código municipio (3 dígitos) | `001` |
| `MPIO_CNMBR` | Nombre del municipio | `MEDELLÍN` |
| `MPIO_CCNCT` | Código concatenado (igual a DPTOMPIO) | `05001` |

**Join recomendado**: `DIVIPOLA` del CSV ↔ `DPTOMPIO` del GeoJSON.

---

## Proceso de modelado y limpieza

### Dataset de emergencias (UNGRD)

La construcción del consolidado de emergencias 1998–2024 requirió resolver múltiples inconvenientes de calidad y compatibilidad en los archivos fuente.

**Problemas identificados en los archivos originales:**

- Archivos `.xls` con macros internas de ejecución automática, representando riesgo de seguridad, y en algunos casos protección por contraseña que impedía la exportación directa a CSV.
- Número variable de columnas entre años: los reportes anteriores a 2019 no presentan una estructura homogénea.
- Ausencia frecuente del código DIVIPOLA en registros anteriores a 2018.
- Falta de estandarización en los campos de texto de departamento y municipio (variaciones ortográficas, ausencia de tildes, inclusión o exclusión de designaciones como "D.C.", "Distrito Especial", etc.). Ejemplo: *Bogotá*, *Bogota*, *Bogota D.C.*, *Santa Fe de Bogotá*.
- Ausencia de coordenadas GPS en todos los registros; la georreferenciación solo está disponible a nivel de municipio.
- Presencia de columnas vacías en la totalidad de registros de algunos años.
- Cambio estructural en el formato de reporte de recursos del Fondo Nacional de Gestión del Riesgo de Desastres (FNGRD) a partir del año 2023.

**Actividades de transformación realizadas:**

1. Conversión de los 27 archivos `.xls` anuales (1998–2024) a formato procesable en ambiente controlado, evitando la ejecución de macros.
2. Mapeo explícito de columnas por índice posicional para cada año, dado que los encabezados presentan inconsistencias entre períodos.
3. Estandarización de nombres de departamentos y municipios mediante cruce con el catálogo oficial del DANE.
4. Asignación programática del código DIVIPOLA a los registros con campo ausente, mediante coincidencia de texto normalizado con la tabla de referencia del DANE.
5. Unificación de columnas conceptualmente equivalentes con denominaciones distintas entre años.
6. Eliminación de columnas vacías en la totalidad del período consolidado.
7. Aplicación de técnicas de *data wrangling* y *data cleaning* sobre el dataset unificado.

**Resultado de unificación:** 72.807 registros × 45 columnas para el período 1998–2024, de todo tipo de emergencias (incendios forestales, sismos, deslizamientos, accidentes, etc.).

> **Nota sobre 2023–2024:** A partir del año 2023, la UNGRD modificó el esquema de reporte de los recursos de Asistencia Humanitaria de Emergencia (AHE). El nuevo formato desglosa la ayuda por ítem físico (kits de alimento, kits de aseo, colchonetas, carpas, etc.) en lugar de las categorías resumidas presentes en años anteriores (`AP.ALIMENT.`, `SUBSIDIO DE ARRIENDO`, `MATERIALES CONSTRUCCION`, etc.). Como consecuencia, **dichas columnas de recursos se encuentran vacías para los años 2023 y 2024**. La única variable de recursos disponible para ese período es `RECURSOS EJECUTADOS`, que corresponde al valor total del apoyo del FNGRD por evento.

### Limpieza general

- **Eliminación de columnas vacías**: se removió la columna `RUD` (99,9 % nula) y `COMENTARIOS` (texto libre no estructurado con caracteres que truncan la lectura, como saltos de línea y separadores de columna).
- **Normalización de texto**: departamentos, municipios y tipos de evento normalizados a mayúsculas, con limpieza de espacios y valores nulos. En el caso de los municipios, los nombres se estandarizaron según lo reportado por el DANE (ej.: *Santa Fe de Bogotá* → *Bogotá*).
- **Código DIVIPOLA como texto**: se preservan los ceros a la izquierda del código municipal (5 dígitos, estándar DANE). Ejemplo: `05001` (Medellín), no `5001`.
- **Eliminación de duplicados**: se removieron 80 registros duplicados (mismos datos para el evento).
- **Columna multilínea corregida**: `HORAS MAQUINA\nRETROEXCAVADORA\nBULLDOCER\nINTERVENTORIA` normalizada a nombre de una sola línea.
- **Columnas derivadas**: se agregaron `AÑO` y `MES` a partir de la columna `FECHA` para facilitar análisis temporal.

### Filtrado de eventos de riesgo hídrico

Se seleccionaron 4 tipos de evento según la clasificación técnica de la UNGRD:

| Evento en el dataset | Mecanismo físico | Registros |
|---|---|---:|
| `INUNDACION` | Desbordamiento lento o progresivo de cuerpos de agua sobre terrenos planos | 15.434 |
| `CRECIENTE SUBITA` | Subida brusca de caudal en ríos o quebradas | 1.427 |
| `TEMPORAL` | Lluvias prolongadas con encharcamiento o inundación gradual | 484 |
| `AVENIDA TORRENCIAL` | Flujo súbito y violento de agua con sedimentos y escombros por cauce encajonado | 483 |
| **Total** | | **17.828** |

Se unificaron variantes de escritura: `INUNDACIÓN`, `INUNDACIoN` → `INUNDACION`; `CRECIENTE SÚBITA` → `CRECIENTE SUBITA`.

> **Nota**: Se eliminaron las columnas que no aportaban datos al análisis por estar vacías o contener errores de lectura.

---

## Estructura del dataset modelado

**Formato**: CSV con separador `;` (punto y coma) · **Encoding**: UTF-8 con BOM · **Registros**: 17.828 filas × 45 columnas

### Columnas de identificación

| Columna | Tipo | % datos | Descripción |
|---|---|---:|---|
| `FECHA` | texto (dd/mm/aaaa) | 100 % | Fecha del evento |
| `DEPARTAMENTO` | texto | 100 % | Departamento (mayúsculas) |
| `MUNICIPIO` | texto | 100 % | Municipio (mayúsculas) |
| `EVENTO` | texto | 100 % | Tipo de evento: `INUNDACION`, `CRECIENTE SUBITA`, `TEMPORAL`, `AVENIDA TORRENCIAL` |
| `CODIFICACIÓN SEGUN DIVIPOLA` | texto | 100 % | Código DIVIPOLA del municipio (5 dígitos con ceros a la izquierda) |
| `DIVIPOLA` | texto | 98 % | Código DIVIPOLA (campo complementario) |
| `AÑO` | numérico | 99 % | Año extraído de FECHA |
| `MES` | numérico | 99 % | Mes extraído de FECHA (1–12) |

### Columnas de afectación a personas

| Columna | Tipo | % datos | Descripción |
|---|---|---:|---|
| `MUERTOS` | numérico | 5,4 % | Número de fallecidos |
| `HERIDOS` | numérico | 4,0 % | Número de heridos |
| `DESAPA.` | numérico | 3,3 % | Número de desaparecidos |
| `PERSONAS` | numérico | 71,7 % | Personas afectadas |
| `FAMILIAS` | numérico | 71,5 % | Familias afectadas |

### Columnas de daños a infraestructura

| Columna | Tipo | % datos | Descripción |
|---|---|---:|---|
| `VIV.DESTRU.` | numérico | 12,5 % | Viviendas destruidas |
| `VIV.AVER.` | numérico | 51,6 % | Viviendas averiadas |
| `VIAS` | numérico | 13,3 % | Vías afectadas |
| `PTES.VEHIC.` | numérico | 7,0 % | Puentes vehiculares afectados |
| `PTES.PEAT.` | numérico | 5,1 % | Puentes peatonales afectados |
| `ACUED.` | numérico | 7,5 % | Acueductos afectados |
| `ALCANT.` | numérico | 4,8 % | Alcantarillados afectados |
| `C. SALUD` | numérico | 3,5 % | Centros de salud afectados |
| `C.EDUCAT.` | numérico | 6,9 % | Centros educativos afectados |
| `C.COMUNIT.` | numérico | 4,1 % | Centros comunitarios afectados |
| `HECTAREAS` | numérico | 8,1 % | Hectáreas afectadas |

### Columnas de respuesta institucional

| Columna | % datos | Descripción |
|---|---:|---|
| `SUBSIDIO DE ARRIENDO` | 42,7 % | Subsidios de arriendo otorgados |
| `ASISTENCIA NO ALIMENTARIA` | 69,1 % | Kits no alimentarios entregados |
| `AP.ALIMENT.` | 69,1 % | Ayudas alimentarias entregadas |
| `MATERIALES CONSTRUCCION` | 69,1 % | Materiales de construcción entregados |
| `SACOS - BIGBAG` | 69,1 % | Sacos de arena / bigbags entregados |
| `OBRAS DE EMERGENCIA` | 27,0 % | Obras de emergencia ejecutadas |
| `CARROTANQUES - MOTOBOMBAS-PLANTA POTABILIZADORA` | 26,4 % | Equipos de agua desplegados |
| `HORAS MAQUINA RETROEXCAVADORA BULLDOCER INTERVENTORIA` | 26,4 % | Horas máquina utilizadas |
| `APOYO AEREO / TERRESTRE` | 29,9 % | Apoyo logístico desplegado |
| `FIC / TRANSFERENCIAS ECONOMICAS` | 42,8 % | Transferencias económicas realizadas |
| `RECURSOS EJECUTADOS` | 52,1 % | Recursos financieros ejecutados |
| `TRAMITE ANTE UNGRD` | 57,2 % | Estado del trámite ante la UNGRD |
| `ATENDIDO` | 49,8 % | Indicador de atención |

---

## Estadísticas descriptivas

### Distribución temporal

| Indicador | Valor |
|---|---|
| Período cubierto | 1998–2024 (27 años) |
| Total de eventos | 17.828 |
| Promedio anual | ~660 eventos |
| Año más crítico | **2011** — 1.683 eventos (fenómeno de La Niña) |
| Año con menos eventos | **2001** — 104 eventos |

### Estacionalidad mensual (bimodal)

```
Ene ▓░░░░░░░░░░░░░░░░░                           458
Feb ▓▓░░░░░░░░░░░░░░░░░░░                         669
Mar ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░              1.173
Abr ▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   2.137
May ▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2.791  ← pico 1
Jun ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        1.864
Jul ▓▓▓▓░░░░░░░░░░░░░░░░░░░                     1.117
Ago ▓▓▓░░░░░░░░░░░░░░░░░░                         889
Sep ▓▓▓░░░░░░░░░░░░░░░░░░                         892
Oct ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░       1.965
Nov ▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2.737  ← pico 2
Dic ▓▓▓░░░░░░░░░░░░░░░░░░░░                       995
```

La distribución bimodal corresponde a las dos temporadas de lluvias de Colombia: **abril–mayo** (primera) y **octubre–noviembre** (segunda).

### Top 10 departamentos más afectados

| # | Departamento | Eventos |
|---|---|---:|
| 1 | Cundinamarca | 1.640 |
| 2 | Antioquia | 1.541 |
| 3 | Santander | 1.093 |
| 4 | Valle del Cauca | 911 |
| 5 | Cauca | 858 |
| 6 | Chocó | 824 |
| 7 | Tolima | 808 |
| 8 | Bolívar | 772 |
| 9 | Meta | 737 |
| 10 | Huila | 669 |

---

## Consideraciones sobre la clasificación de eventos hídricos

La UNGRD distingue técnicamente entre fenómenos que coloquialmente pueden denominarse "inundación". La tabla siguiente resume los eventos del dataset relevantes para el análisis de riesgo hídrico:

| Evento en el dataset | Mecanismo físico | Registros |
|---|---|---:|
| `INUNDACION` / `INUNDACIÓN` | Desbordamiento lento o progresivo de cuerpos de agua sobre terrenos planos | 15.434 |
| `CRECIENTE SUBITA` / `CRECIENTE SÚBITA` | Subida brusca de caudal en ríos o quebradas | 1.427 |
| `AVENIDA TORRENCIAL` | Flujo súbito y violento de agua con sedimentos y escombros por cauce encajonado | 483 |
| `TEMPORAL` | Lluvias prolongadas con encharcamiento o inundación gradual | 484 |

Dependiendo del marco conceptual del análisis, estos eventos pueden tratarse de forma diferenciada (mecanismos físicos distintos, niveles de destrucción diferentes) o agrupados bajo un criterio de **riesgo hídrico general**.

---

## Uso rápido con Python

```python
import pandas as pd

# Cargar dataset (separador ; y encoding UTF-8 BOM)
df = pd.read_csv('CONSOLIDADO_EMERGENCIAS_1998-2024.csv',
                 sep=';', encoding='utf-8-sig',
                 dtype={'DIVIPOLA': str, 'CODIFICACIÓN SEGUN DIVIPOLA': str},
                 low_memory=False)

# Filtrar solo inundaciones progresivas
inundaciones = df[df['EVENTO'] == 'INUNDACION']

# Agrupar por departamento y año
resumen = df.groupby(['DEPARTAMENTO', 'AÑO']).agg(
    eventos=('EVENTO', 'size'),
    personas=('PERSONAS', 'sum'),
    fallecidos=('MUERTOS', 'sum')
).reset_index()
```

---

## Advertencias sobre calidad y uso de los datos

### Datos de emergencias (UNGRD)

- Los registros dependen del reporte de las entidades territoriales; pueden existir subregistros, en particular en años anteriores a 2010.
- El campo `EVENTO` presenta variaciones tipográficas a lo largo de los años (p. ej., `INUNDACION` / `INUNDACIÓN`, `CRECIENTE SUBITA` / `CRECIENTE SÚBITA`). Se recomienda normalizar este campo antes de cualquier agrupación o análisis de frecuencias.
- Los registros no incluyen coordenadas GPS; la referencia espacial se limita al nivel municipal.

---

## Marco legal y licencias

Los datos que componen este repositorio provienen de entidades del Estado colombiano y son publicados como datos abiertos en cumplimiento del marco normativo nacional:

- **Ley 1712 de 2014** — Transparencia y del Derecho de Acceso a la Información Pública Nacional.
- **Política de Gobierno Digital** (MinTIC) — Marco de apertura de datos públicos.
- **Constitución Política de Colombia de 1991**, artículo 74 — Derecho de acceso a documentos públicos.

| Fuente | Licencia declarada |
|---|---|
| UNGRD — Emergencias | Dominio Público |
| DANE — DIVIPOLA | CC BY-SA 4.0 |
| IGAC/DANE — GeoJSON | CC BY-SA 4.0 |

El trabajo de consolidación, limpieza, integración y documentación contenido en este repositorio se publica bajo la licencia:

**[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es)**

Esta licencia permite el uso, distribución y adaptación del material para cualquier propósito, incluso comercial, siempre que se otorgue el crédito correspondiente.

---

## Cómo citar

### Cita del dataset (APA 7)

> Cifuentes Bastidas, E. A., Moreta Cruz, L. F., Muñoz, M. del P. y Pérez Álvarez, E. A. (2025). *Vulnerabilidad y severidad de inundaciones en Colombia 1998–2024* [Conjunto de datos]. GitHub. https://github.com/cifuentesedw/vys_inundaciones-col_1998-2024

### Fuentes primarias (APA 7)

> Unidad Nacional para la Gestión del Riesgo de Desastres. (1998–2024). *Consolidado anual de emergencias* [Conjunto de datos]. Subdirección para el Manejo de Desastres. https://portal.gestiondelriesgo.gov.co/Paginas/Consolidado-Atencion-de-Emergencias.aspx

> Instituto de Hidrología, Meteorología y Estudios Ambientales. (2001–2024). *Datos hidrometeorológicos crudos — Red de estaciones automáticas* [Precipitación, temperatura ambiente del aire, presión atmosférica]. Portal de Datos Abiertos de Colombia. https://www.datos.gov.co

> Departamento Administrativo Nacional de Estadística. (2024). *División Político-Administrativa de Colombia (DIVIPOLA)* [Conjunto de datos]. https://www.dane.gov.co

---

## Contacto

Para preguntas sobre el dataset, el proceso de construcción o posibles errores, se puede abrir un [Issue](https://github.com/cifuentesedw/vys_inundaciones-col_1998-2024/issues) en este repositorio o contactar a los autores a través de los correos indicados.

---

*Última actualización del repositorio: marzo de 2026. Datos de emergencias hasta diciembre de 2024; DIVIPOLA actualizada a 20 de febrero de 2026.*