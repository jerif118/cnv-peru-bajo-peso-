"""Definiciones SQL y gráficos compartidos por los notebooks de análisis (02 y 05)."""

import numpy as np

# Población de análisis: partos únicos 2015-2025 con peso y gestación válidos (2026 sigue en curso)
FILTRO = "anio_nacimiento BETWEEN 2015 AND 2025 AND es_registro_analisis"
CONTEOS = """COUNT(*) AS nacimientos,
       COUNT_IF(es_bajo_peso_nacer) AS bajo_peso,
       COUNT_IF(duracion_embarazo_semanas >= 37) AS nacimientos_termino,
       COUNT_IF(es_bajo_peso_nacer AND duracion_embarazo_semanas >= 37) AS bajo_peso_termino"""
GRUPO_EDAD = """CASE WHEN edad_madre BETWEEN 10 AND 14 THEN '10-14'
            WHEN edad_madre BETWEEN 15 AND 19 THEN '15-19'
            WHEN edad_madre BETWEEN 20 AND 34 THEN '20-34'
            WHEN edad_madre BETWEEN 35 AND 39 THEN '35-39'
            WHEN edad_madre BETWEEN 40 AND 44 THEN '40-44'
            WHEN edad_madre BETWEEN 45 AND 60 THEN '45-60'
            ELSE 'SIN DATO' END"""
GRUPO_GESTACION = """CASE WHEN duracion_embarazo_semanas BETWEEN 22 AND 27 THEN '22-27 semanas'
            WHEN duracion_embarazo_semanas BETWEEN 28 AND 31 THEN '28-31 semanas'
            WHEN duracion_embarazo_semanas BETWEEN 32 AND 33 THEN '32-33 semanas'
            WHEN duracion_embarazo_semanas BETWEEN 34 AND 36 THEN '34-36 semanas'
            WHEN duracion_embarazo_semanas BETWEEN 37 AND 41 THEN '37-41 semanas'
            ELSE '42-44 semanas' END"""
GRUPO_ALTITUD = """CASE WHEN altitud_msnm < 500 THEN '<500 m'
            WHEN altitud_msnm < 1500 THEN '500-1499 m'
            WHEN altitud_msnm < 2500 THEN '1500-2499 m'
            WHEN altitud_msnm < 3000 THEN '2500-2999 m'
            WHEN altitud_msnm < 3500 THEN '3000-3499 m'
            WHEN altitud_msnm < 4000 THEN '3500-3999 m'
            WHEN altitud_msnm >= 4000 THEN '4000+ m'
            ELSE 'SIN DATO' END"""
GRUPO_POBREZA = """CASE WHEN pobreza_pct < 20 THEN '<20 %'
            WHEN pobreza_pct < 40 THEN '20-39 %'
            WHEN pobreza_pct < 60 THEN '40-59 %'
            WHEN pobreza_pct >= 60 THEN '60+ %'
            ELSE 'SIN DATO' END"""
GRUPO_IDH = """CASE WHEN idh_2019 < 0.3 THEN '<0.30'
            WHEN idh_2019 < 0.4 THEN '0.30-0.39'
            WHEN idh_2019 < 0.5 THEN '0.40-0.49'
            WHEN idh_2019 < 0.6 THEN '0.50-0.59'
            WHEN idh_2019 >= 0.6 THEN '0.60+'
            ELSE 'SIN DATO' END"""
ORDEN_ALTITUD = ['<500 m', '500-1499 m', '1500-2499 m', '2500-2999 m', '3000-3499 m', '3500-3999 m', '4000+ m']
ORDEN_POBREZA = ['<20 %', '20-39 %', '40-59 %', '60+ %']
ORDEN_IDH = ['<0.30', '0.30-0.39', '0.40-0.49', '0.50-0.59', '0.60+']
ORDEN_EDAD = ['10-14', '15-19', '20-34', '35-39', '40-44', '45-60']
ORDEN_GESTACION = ['22-27 semanas', '28-31 semanas', '32-33 semanas', '34-36 semanas',
                   '37-41 semanas', '42-44 semanas']
ORDEN_EDUCACION = ['NINGUN NIVEL/ILETRADO', 'INICIAL/PRE-ESCOLAR', 'PRIMARIA INCOMPLETA',
                   'PRIMARIA COMPLETA', 'SECUNDARIA INCOMPLETA', 'SECUNDARIA COMPLETA',
                   'SUPERIOR NO UNIV. INCOMPLETA', 'SUPERIOR NO UNIV. COMPLETA',
                   'SUPERIOR UNIV. INCOMPLETA', 'SUPERIOR UNIV. COMPLETA']


def con_intervalos(consulta):
    """Añade el % de bajo peso (total y a término) con IC 95 % de Wilson a una consulta de CONTEOS."""
    wilson = "1.96 * SQRT(p * (1 - p) / nacimientos + 0.9604 / POW(nacimientos, 2))"
    return f"""WITH conteos AS ({consulta}),
tasas AS (SELECT *, bajo_peso / nacimientos AS p,
                 bajo_peso_termino / NULLIF(nacimientos_termino, 0) AS p_termino
          FROM conteos)
SELECT * EXCEPT (p, p_termino),
       ROUND(100 * p, 2) AS porcentaje_bajo_peso,
       ROUND(100 * (p + 1.9208 / nacimientos - {wilson}) / (1 + 3.8416 / nacimientos), 2) AS ic95_inferior,
       ROUND(100 * (p + 1.9208 / nacimientos + {wilson}) / (1 + 3.8416 / nacimientos), 2) AS ic95_superior,
       ROUND(100 * p_termino, 2) AS porcentaje_bajo_peso_termino
FROM tasas"""


def barras(ax, datos, titulo, orden=None):
    """% de bajo peso por categoría: todos (con IC 95 %) y solo a término."""
    datos = datos.set_index('valor')
    if orden:
        datos = datos.loc[[v for v in orden if v in datos.index]].iloc[::-1]
    else:
        datos = datos.sort_values('porcentaje_bajo_peso')
    y = np.arange(len(datos))
    error = [datos['porcentaje_bajo_peso'] - datos['ic95_inferior'],
             datos['ic95_superior'] - datos['porcentaje_bajo_peso']]
    ax.barh(y + 0.2, datos['porcentaje_bajo_peso'], height=0.4, xerr=error,
            color='#20639B', label='Todos los partos únicos')
    ax.barh(y - 0.2, datos['porcentaje_bajo_peso_termino'], height=0.4,
            color='#D8892B', label='Solo a término (≥37 semanas)')
    ax.set_yticks(y, datos.index)
    ax.set(title=titulo, xlabel='% bajo peso al nacer (<2500 g)')
    ax.grid(axis='x', alpha=0.2)
    ax.set_axisbelow(True)
