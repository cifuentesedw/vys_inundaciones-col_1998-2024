# Vulnerabilidad y Severidad de Inundaciones en Colombia (1998–2024)

## Resumen

Este repositorio contiene un conjunto de datos integrado para el análisis de vulnerabilidad y severidad de eventos de inundación en Colombia durante el período 1998–2024. El dataset resulta de la consolidación, limpieza e integración de cuatro fuentes de datos públicas del Estado colombiano: registros de emergencias de la Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD), y series hidrometeorológicas de precipitación, temperatura del aire y presión atmosférica del Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM). El repositorio incluye además datos geoespaciales de referencia a nivel municipal y de vereda, así como la tabla de codificación territorial DIVIPOLA del Departamento Administrativo Nacional de Estadística (DANE).

---

## Contenido del repositorio

| Archivo | Descripción | Fuente | Registros |
|---|---|---|---|
| `CONSOLIDADO_EMERGENCIAS_1998-2024.csv` | Registros de emergencias por fenómenos naturales y antrópicos no intencionales en Colombia | UNGRD | 72.807 filas × 45 cols |
| `precipitacion.csv` | Series temporales de precipitación de estaciones automáticas | IDEAM | ~270M filas × 12 cols |
| `temperatura.csv` | Series temporales de temperatura ambiente del aire | IDEAM | ~88,7M filas × 12 cols |
| `presion_atmosferica.csv` | Series temporales de presión atmosférica | IDEAM | ~32,4M filas × 12 cols |
| `DIVIPOLA.csv` | Tabla de referencia de códigos de división político-administrativa | DANE | — |
| `MunicipiosVeredas19MB.json` | Geometrías vectoriales de municipios y veredas de Colombia | IGAC / DANE | — |
| `Modelado Dataset Emergencias.pdf` | Documento técnico del proceso de construcción y modelado del dataset | Autoría propia | — |

---

## Fuentes de datos

### 1. Dataset de Emergencias — UNGRD

| Campo | Detalle |
|---|---|
| **Productor** | Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD) — Subdirección para el Manejo de Desastres |
| **Portal datos abiertos** | https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Emergencias-UNGRD-/wwkg-r6te/about_data |
| **Portal institucional** | https://portal.gestiondelriesgo.gov.co/Paginas/Consolidado-Atencion-de-Emergencias.aspx |
| **Cobertura temporal** | 1 de enero de 1998 – 31 de diciembre de 2024 |
| **Cobertura geográfica** | Nacional (32 departamentos) |
| **Granularidad** | Evento por municipio |
| **Frecuencia de actualización** | Anual |
| **Licencia original** | Dominio Público — publicado en cumplimiento de la Ley 1712 de 2014 |

El dataset de emergencias contiene el registro de eventos naturales o antrópicos no intencionales reportados diariamente por los Consejos Departamentales y Municipales de Gestión del Riesgo de Desastres (CDGRD/CMGRD), la Defensa Civil Colombiana, la Cruz Roja Colombiana y el Sistema Nacional de Bomberos.

Los reportes originales son publicados en archivos anuales de formato `.xls`. Para la construcción del consolidado se unificaron los 27 archivos anuales disponibles para el período 1998–2024. Este proceso implicó resolver múltiples inconsistencias estructurales descritas en la sección [Proceso de construcción del dataset](#proceso-de-construcción-del-dataset).

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


---

### 2. Dataset de Precipitación — IDEAM

| Campo | Detalle |
|---|---|
| **Productor** | Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM) |
| **Portal datos abiertos** | https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Precipitaci-n/s54a-sgyg/about_data |
| **Cobertura temporal** | Enero de 2003 – presente (actualización con rezago de 1 día calendario) |
| **Cobertura geográfica** | Nacional — red de estaciones automáticas del IDEAM y convenios interadministrativos |
| **Granularidad temporal** | Variable: entre 5 y 10 minutos por sensor |
| **Volumen** | ~270 millones de registros (a febrero de 2026) |
| **Estructura** | 12 columnas |
| **Licencia original** | Datos abiertos — Ley 1712 de 2014 |

---

### 3. Dataset de Temperatura Ambiente del Aire — IDEAM

| Campo | Detalle |
|---|---|
| **Productor** | Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM) |
| **Portal datos abiertos** | https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Temperatura-Ambiente-del-Aire/sbwg-7ju4/about_data |
| **Cobertura temporal** | Enero de 2001 – presente (actualización con rezago de 1 día calendario) |
| **Cobertura geográfica** | Nacional — red de estaciones automáticas del IDEAM y convenios interadministrativos |
| **Granularidad temporal** | Variable: entre 5 y 10 minutos por sensor |
| **Volumen** | ~88,7 millones de registros (a febrero de 2026) |
| **Estructura** | 12 columnas |
| **Licencia original** | Datos abiertos — Ley 1712 de 2014 |

---

### 4. Dataset de Presión Atmosférica — IDEAM

| Campo | Detalle |
|---|---|
| **Productor** | Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM) |
| **Portal datos abiertos** | https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Presi-n-Atmosf-rica/62tk-nxj5/about_data |
| **Cobertura temporal** | Marzo de 2001 – presente (actualización con rezago de 1 día calendario) |
| **Cobertura geográfica** | Nacional — red de estaciones automáticas del IDEAM y convenios interadministrativos |
| **Granularidad temporal** | Variable: entre 5 y 10 minutos por sensor |
| **Volumen** | ~32,4 millones de registros (a febrero de 2026) |
| **Estructura** | 12 columnas |
| **Licencia original** | Datos abiertos — Ley 1712 de 2014 |

#### Variables comunes a los tres datasets hidrometeorológicos del IDEAM

| Variable | Descripción |
|---|---|
| `CodigoEstacion` | Código único de la estación de monitoreo |
| `CodigoSensor` | Código del sensor dentro de la estación |
| `FechaObservacion` | Fecha y hora de la observación |
| `ValorObservado` | Valor medido por el sensor |
| `NombreEstacion` | Nombre de la estación |
| `Departamento` | Departamento de ubicación de la estación |
| `Municipio` | Municipio de ubicación de la estación |
| `ZonaHidrografica` | Zona hidrográfica según clasificación del IDEAM |
| `Latitud` | Latitud geográfica de la estación (grados decimales) |
| `Longitud` | Longitud geográfica de la estación (grados decimales) |
| `DescripcionSensor` | Descripción del tipo de sensor y variable medida |
| `UnidadMedida` | Unidad de la variable observada |

---

### 5. DIVIPOLA — DANE

| Campo | Detalle |
|---|---|
| **Productor** | Departamento Administrativo Nacional de Estadística (DANE) |
| **Descripción** | División Político-Administrativa de Colombia. Sistema de codificación única de departamentos, distritos y municipios del territorio nacional, administrado por el DANE desde 1953. |
| **Referencia normativa** | Constitución Política de Colombia de 1991, artículos sobre organización territorial |
| **Documentación** | https://www.dane.gov.co/files/investigaciones/divipola/divipola2007.pdf |
| **Licencia** | Datos abiertos del Estado colombiano — CC BY-SA 4.0 |

---

### 6. GeoJSON Municipios y Veredas

| Campo | Detalle |
|---|---|
| **Productor** | Instituto Geográfico Agustín Codazzi (IGAC) / DANE |
| **Descripción** | Geometrías vectoriales de polígonos de municipios y veredas de Colombia para análisis espacial y cartografía temática. |
| **Formato** | GeoJSON |
| **Tamaño** | ~19 MB |
| **Licencia** | Datos abiertos del Estado colombiano — CC BY-SA 4.0 |

---

## Proceso de construcción del dataset

### Dataset de emergencias (UNGRD)

La construcción del consolidado de emergencias 1998–2024 requirió resolver múltiples inconvenientes de calidad y compatibilidad en los archivos fuente:

**Problemas identificados en los archivos originales:**
- Archivos `.xls` con macros internas de ejecución automática, representando riesgo de seguridad, y en algunos casos protección por contraseña que impedía la exportación directa a CSV.
- Número variable de columnas entre años: los reportes anteriores a 2019 no presentan una estructura homogénea.
- Ausencia frecuente del código DIVIPOLA en registros anteriores a 2018.
- Falta de estandarización en los campos de texto de departamento y municipio (variaciones ortográficas, ausencia de tildes, inclusión o exclusión de designaciones como "D.C.", "Distrito Especial", etc.). Ejemplo: *Bogotá*, *Bogota*, *Bogota D.C.*, *Santa Fe de Bogotá*.
- Ausencia de coordenadas GPS en todos los registros; la georeferenciación solo está disponible a nivel de municipio.
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

**Resultado:** 72.807 registros × 45 columnas para el período 1998–2024.

> **Nota sobre 2023–2024:** A partir del año 2023, la UNGRD modificó el esquema de reporte de los recursos de Asistencia Humanitaria de Emergencia (AHE). El nuevo formato desglosa la ayuda por ítem físico (kits de alimento, kits de aseo, colchonetas, carpas, etc.) en lugar de las categorías resumidas presentes en años anteriores (`AP.ALIMENT.`, `SUBSIDIO DE ARRIENDO`, `MATERIALES CONSTRUCCION`, etc.). Como consecuencia, **dichas columnas de recursos se encuentran vacías para los años 2023 y 2024**. La única variable de recursos disponible para ese período es `RECURSOS EJECUTADOS`, que corresponde al valor total del apoyo del FNGRD por evento.

---

## Advertencias sobre calidad y uso de los datos

### Datos de emergencias (UNGRD)
- Los registros dependen del reporte de las entidades territoriales; pueden existir subregistros, en particular en años anteriores a 2010.
- El campo `EVENTO` presenta variaciones tipográficas a lo largo de los años (p.ej., `INUNDACION` / `INUNDACIÓN`, `CRECIENTE SUBITA` / `CRECIENTE SÚBITA`). Se recomienda normalizar este campo antes de cualquier agrupación o análisis de frecuencias.
- Los registros no incluyen coordenadas GPS; la referencia espacial se limita al nivel municipal.

### Datos hidrometeorológicos (IDEAM)

El IDEAM establece de manera explícita las siguientes cláusulas de uso para sus datasets publicados en el portal de Datos Abiertos del Gobierno Colombiano:

1. Los datos **no han sido validados** por el IDEAM.
2. Son datos crudos instantáneos provenientes de sensores automáticos; pueden presentar errores e inconsistencias, incluso fuera de los rangos considerados normales, como resultado de fallas en los sensores de origen.
3. Es posible que existan rezagos en la transmisión según la frecuencia de envío de cada sensor y el medio de transmisión utilizado.
4. **El posterior uso e interpretación de los datos para cualquier finalidad queda bajo la exclusiva responsabilidad del portador.**
5. Los datos **no podrán ser utilizados como evidencia jurídica** ante entes de control sobre la ocurrencia o no de fenómenos hidroclimatológicos.
6. Para usos que requieran información oficial y validada, el canal autorizado por el IDEAM es el portal DHIME: http://dhime.ideam.gov.co

---

## Consideraciones sobre la clasificación de eventos hídricos

La UNGRD distingue técnicamente entre fenómenos que coloquialmente pueden denominarse "inundación". La tabla siguiente resume los eventos del dataset relevantes para el análisis de riesgo hídrico:

| Evento en el dataset | Mecanismo físico | Registros aprox. |
|---|---|---|
| `INUNDACION` / `INUNDACIÓN` | Desbordamiento lento o progresivo de cuerpos de agua sobre terrenos planos | ~15.500 |
| `AVENIDA TORRENCIAL` | Flujo súbito y violento de agua con sedimentos y escombros por cauce encajonado | ~485 |
| `CRECIENTE SUBITA` / `CRECIENTE SÚBITA` | Subida brusca de caudal en ríos o quebradas | ~1.100 |
| `TEMPORAL` | Lluvias prolongadas con encharcamiento o inundación gradual | ~486 |

Dependiendo del marco conceptual del análisis, estos eventos pueden tratarse de forma diferenciada (mecanismos físicos distintos, niveles de destrucción diferentes) o agrupados bajo un criterio de **riesgo hídrico general**. Se recomienda documentar y justificar explícitamente la decisión adoptada en cada estudio.

---

## Marco legal y licencias

Los datos que componen este repositorio provienen de entidades del Estado colombiano y son publicados como datos abiertos en cumplimiento del marco normativo nacional:

- **Ley 1712 de 2014** — Transparencia y del Derecho de Acceso a la Información Pública Nacional.
- **Política de Gobierno Digital** (MinTIC) — Marco de apertura de datos públicos.
- **Constitución Política de Colombia de 1991**, artículo 74 — Derecho de acceso a documentos públicos.

| Fuente | Licencia declarada |
|---|---|
| UNGRD — Emergencias | Dominio Público |
| IDEAM — Precipitación, Temperatura, Presión | Datos abiertos — Ley 1712 de 2014 |
| DANE — DIVIPOLA | CC BY-SA 4.0 |
| IGAC/DANE — GeoJSON | CC BY-SA 4.0 |

El trabajo de consolidación, limpieza, integración y documentación contenido en este repositorio se publica bajo la licencia:

**[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es)**

Esta licencia permite el uso, distribución y adaptación del material para cualquier propósito, incluso comercial, siempre que se otorgue el crédito correspondiente.

---

## Cómo citar

Si utilizas este repositorio en un trabajo académico o de investigación, se recomienda la siguiente cita:

```
Cifuentes, E. (2025). Vulnerabilidad y Severidad de Inundaciones en Colombia 1998–2024
[Dataset]. GitHub. https://github.com/cifuentesedw/vys_inundaciones-col_1998-2024
```

Y citar las fuentes primarias de forma independiente:

```
Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD). (1998–2024).
Consolidado Anual de Emergencias. Subdirección para el Manejo de Desastres.
https://portal.gestiondelriesgo.gov.co/Paginas/Consolidado-Atencion-de-Emergencias.aspx

Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM). (2001–2024).
Datos Hidrometeorológicos Crudos — Red de Estaciones Automáticas [Precipitación,
Temperatura Ambiente del Aire, Presión Atmosférica]. Portal de Datos Abiertos de Colombia.
https://www.datos.gov.co

Departamento Administrativo Nacional de Estadística (DANE). (2024).
División Político-Administrativa de Colombia (DIVIPOLA).
https://www.dane.gov.co
```

---

## Contacto

Para preguntas sobre el dataset, el proceso de construcción o posibles errores, puedes abrir un [Issue](https://github.com/cifuentesedw/vys_inundaciones-col_1998-2024/issues) en este repositorio.

---

*Última actualización del dataset: febrero de 2025. Datos de emergencias hasta diciembre de 2024; variables hidrometeorológicas hasta 20 de febrero de 2026.*
