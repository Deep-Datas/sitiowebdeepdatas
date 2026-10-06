"""Tableros de ejemplo del sitio, con datos ficticios.

Cada tablero se describe con datos simples (valores, etiquetas) y las
funciones de este módulo calculan las posiciones de barras, puntos y
líneas en porcentajes. Las plantillas de src/charts.html los dibujan.
Para cambiar un ejemplo, editá los valores de EXAMPLES y regenerá el sitio.
"""


# ---------- Formatos (convención argentina: punto de miles, coma decimal) ----------

def num(value, decimals=0):
    text = f'{value:,.{decimals}f}'
    return text.replace(',', 'X').replace('.', ',').replace('X', '.')


def money_m(value):
    return f'$ {num(value, 1)} M'


def pct(value, decimals=1):
    return f'{num(value, decimals)}%'


# ---------- Geometría de cada tipo de gráfico ----------

def columns_with_target(labels, values, targets, step, top, fmt):
    """Columnas mensuales con una marca de objetivo sobre cada una."""
    items = []
    for i, (label, value, target) in enumerate(zip(labels, values, targets)):
        items.append({
            'label': label,
            'value': value,
            'value_label': fmt(value),
            'target_label': fmt(target),
            'h': value / top * 100,
            'target_y': target / top * 100,
            'above': value >= target,
            'show_label': i == len(values) - 1 or value == max(values),
        })
    ticks = [{'label': num(v), 'y': v / top * 100} for v in range(0, int(top) + 1, step)]
    table = {'headers': ['Mes', 'Real', 'Objetivo'],
             'rows': [[i['label'], i['value_label'], i['target_label']] for i in items]}
    return {'items': items, 'ticks': ticks, 'table': table}


def bar_list(rows, fmt, label_header):
    """Barras horizontales de una sola serie, ordenadas de mayor a menor."""
    rows = sorted(rows, key=lambda r: r[1], reverse=True)
    top = max(v for _, v in rows)
    return {
        'items': [{'label': label, 'value_label': fmt(value), 'w': value / top * 100} for label, value in rows],
        'table': {'headers': [label_header, 'Valor'], 'rows': [[label, fmt(value)] for label, value in rows]},
    }


def grouped_bars(rows, series):
    """Barras horizontales agrupadas (porcentajes de 0 a 100)."""
    return {
        'items': [{
            'label': label,
            'bars': [{'key': key, 'name': name, 'value_label': pct(v, 0), 'w': v} for (key, name), v in zip(series, values)],
        } for label, values in rows],
        'table': {'headers': ['Distribuidor'] + [name for _, name in series],
                  'rows': [[label] + [pct(v, 0) for v in values] for label, values in rows]},
    }


def stacked_100(segments):
    """Barra 100% apilada: composición de un total."""
    total = sum(v for _, _, v in segments)
    out = []
    for key, label, value in segments:
        share = value / total * 100
        out.append({'key': key, 'label': label, 'value_label': pct(share), 'w': share, 'inside': share >= 12})
    return out


def line_forecast(history, forecast, spread, low, high, step, x_labels):
    """Serie real + pronóstico con banda de confianza, en coordenadas 0-100."""
    n = len(history) + len(forecast) - 1
    first = len(history) - 1

    def x(i):
        return i / n * 100

    def y(v):
        return 100 - (v - low) / (high - low) * 100

    def path(points):
        return 'M' + ' L'.join(f'{a:.2f} {b:.2f}' for a, b in points)

    real = [(x(i), y(v)) for i, v in enumerate(history)]
    fc = [(x(first + i), y(v)) for i, v in enumerate([history[-1]] + forecast)]
    band_values = [history[-1]] + forecast
    band_spread = [0] + spread
    band = ([(x(first + i), y(v + s)) for i, (v, s) in enumerate(zip(band_values, band_spread))]
            + [(x(first + i), y(v - s)) for i, (v, s) in reversed(list(enumerate(zip(band_values, band_spread))))])

    hits = []
    table_rows = []
    width = 100 / n
    for i in range(n + 1):
        lines = []
        if i < len(history):
            lines.append(('real', f'Real: {num(history[i], 1)} mil u.'))
        else:
            j = i - len(history)
            lines.append(('forecast', f'Pronóstico: {num(forecast[j], 1)} mil u.'))
            lines.append(('band', f'Rango: {num(forecast[j] - spread[j], 1)} a {num(forecast[j] + spread[j], 1)}'))
        hits.append({'x': x(i), 'left': max(x(i) - width / 2, 0), 'w': width if 0 < i < n else width / 2,
                     'title': f'Semana {i + 1}', 'lines': lines})
        if i < len(history):
            table_rows.append([f'Semana {i + 1}', num(history[i], 1), '—', '—'])
        else:
            j = i - len(history)
            table_rows.append([f'Semana {i + 1}', '—', num(forecast[j], 1),
                               f'{num(forecast[j] - spread[j], 1)} a {num(forecast[j] + spread[j], 1)}'])

    return {
        'real_line': path(real),
        'real_area': path(real) + f' L{real[-1][0]:.2f} 100 L0 100 Z',
        'forecast_line': path(fc),
        'band': path(band) + ' Z',
        'real_end': {'x': real[-1][0], 'y': 100 - real[-1][1], 'label': f'{num(history[-1], 1)} mil'},
        'forecast_end': {'x': fc[-1][0], 'y': 100 - fc[-1][1], 'label': f'{num(forecast[-1], 1)} mil'},
        'split_x': x(first),
        'ticks': [{'label': num(v), 'y': (v - low) / (high - low) * 100} for v in range(low, high + 1, step)],
        'x_labels': [{'label': label, 'x': x(i)} for i, label in x_labels],
        'hits': hits,
        'table': {'headers': ['Semana', 'Real (miles)', 'Pronóstico (miles)', 'Rango probable'], 'rows': table_rows},
    }


# ---------- Ejemplos (datos ficticios) ----------

MONTHS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

DISTRIBUTORS = [
    # nombre, facturación ($ M), % del objetivo
    ('Distribuidora Centro', 12.8, 104),
    ('Distribuidora Norte', 9.6, 98),
    ('Distribuidora Litoral', 8.7, 101),
    ('Distribuidora Cuyo', 6.9, 92),
    ('Distribuidora Sur', 5.8, 96),
    ('Distribuidora Patagonia', 4.8, 89),
]


def status(attainment):
    if attainment >= 100:
        return {'key': 'good', 'label': 'En objetivo', 'icon': 'check-circle-fill'}
    if attainment >= 95:
        return {'key': 'warning', 'label': 'Atención', 'icon': 'exclamation-circle-fill'}
    return {'key': 'critical', 'label': 'Debajo', 'icon': 'x-circle-fill'}


def stock_status(stock, demand):
    ratio = stock / demand
    if ratio < 0.7:
        return {'key': 'critical', 'label': 'Reponer ya', 'icon': 'x-circle-fill'}
    if ratio < 1:
        return {'key': 'warning', 'label': 'Atención', 'icon': 'exclamation-circle-fill'}
    return {'key': 'good', 'label': 'Cubierto', 'icon': 'check-circle-fill'}


def suggested_order(stock, demand):
    """Unidades a reponer, redondeadas a la centena."""
    gap = demand - stock
    return num(-(-gap // 100) * 100) if gap > 0 else '—'


def build_examples():
    revenue = [3.6, 3.4, 3.9, 3.8, 4.0, 4.1, 4.3, 4.2, 4.0, 4.3, 4.4, 4.6]
    objective = [3.8, 3.6, 3.9, 3.9, 4.0, 4.1, 4.2, 4.2, 4.2, 4.3, 4.4, 4.5]
    channels = [('Supermercados', 17.4), ('Mayoristas', 12.9), ('Autoservicios', 9.8),
                ('Kioscos y almacenes', 6.1), ('E-commerce', 2.4)]

    coverage = [  # distribuidor, % PDV con Línea Clásica, % PDV con Línea Premium
        ('Centro', [95, 72]), ('Litoral', [93, 69]), ('Norte', [92, 61]),
        ('Sur', [90, 60]), ('Cuyo', [88, 55]), ('Patagonia', [86, 52]),
    ]
    opportunities = [  # zona y vendedor, PDV que compran Clásica y no Premium, potencial mensual
        ('Norte', 'Vendedor 07', 148, 1.9), ('Cuyo', 'Vendedor 12', 131, 1.6),
        ('Sur', 'Vendedor 03', 117, 1.4), ('Patagonia', 'Vendedor 09', 96, 1.1),
        ('Centro', 'Vendedor 15', 84, 1.0),
    ]

    history = [21.2, 22.0, 21.6, 23.1, 22.8, 24.0, 23.5, 22.9, 24.6, 25.1, 24.3, 25.8, 26.2, 25.5, 26.9, 27.4]
    forecast = [27.9, 28.3, 27.6, 29.0, 29.4, 28.8, 30.1, 30.5]
    spread = [0.8, 1.1, 1.3, 1.6, 1.8, 2.0, 2.2, 2.4]
    risk = [('Bebidas', 12), ('Snacks', 9), ('Lácteos', 7), ('Limpieza', 5), ('Congelados', 4)]
    replenish = [  # producto, stock, demanda prevista 2 semanas
        ('Gaseosa cola 2,25 L', 1840, 3200), ('Papas fritas 150 g', 960, 1450),
        ('Yogur bebible 1 L', 1120, 1300), ('Helado 1 kg', 380, 520),
        ('Detergente 750 ml', 2400, 1900),
    ]

    return [
        {
            'id': 'distribuidores',
            'tags': ['Consumo masivo', 'Ventas y distribución'],
            'title': 'Tablero de performance de distribuidores',
            'summary': 'Una sola versión de los números para toda la red: facturación, volumen y cumplimiento del objetivo de cada distribuidor, mes a mes.',
            'app_title': 'Performance comercial · Red de distribuidores',
            'filters': [('Período', 'Ene–Dic 2025'), ('Región', 'Todas'), ('Canal', 'Todos')],
            'kpis': [
                {'label': 'Facturación neta', 'value': money_m(sum(revenue)), 'delta': '▲ 9,2% vs. 2024', 'good': True},
                {'label': 'Volumen vendido', 'value': '1.284 t', 'delta': '▲ 4,1% vs. 2024', 'good': True},
                {'label': 'Tamaño promedio de pedido', 'value': '412 kg', 'delta': '▼ 2,3% vs. 2024', 'good': False},
                {'label': 'Clientes activos', 'value': '6.940', 'delta': '▲ 3,8% vs. 2024', 'good': True},
            ],
            'panels': [
                {'type': 'columns', 'wide': True, 'title': 'Facturación mensual vs. objetivo',
                 'unit': 'Millones de $', 'legend': [('real', 'Real'), ('target', 'Objetivo')],
                 'data': columns_with_target(MONTHS, revenue, objective, 1, 5, money_m)},
                {'type': 'bars', 'title': 'Facturación por canal', 'unit': 'Millones de $',
                 'data': bar_list(channels, money_m, 'Canal')},
                {'type': 'ranking', 'title': 'Ranking de distribuidores',
                 'rows': [{'name': n, 'revenue': money_m(r), 'attainment': f'{a}%', 'meter': min(a, 120) / 120 * 100,
                           'status': status(a)} for n, r, a in DISTRIBUTORS],
                 'target_x': 100 / 120 * 100},
            ],
            'story': {
                'challenge': 'Las ventas llegan de cada distribuidor en planillas propias, con criterios distintos. Consolidarlas lleva días y nadie confía del todo en el número final.',
                'solution': 'Integramos las fuentes en un modelo único, unificamos criterios y publicamos un tablero que se actualiza solo, con filtros por región, canal, categoría y producto.',
                'benefit': 'La dirección y el equipo comercial ven el mismo número y detectan a tiempo qué distribuidor o canal se aleja del objetivo.',
            },
        },
        {
            'id': 'cobertura',
            'tags': ['Consumo masivo', 'Fuerza de ventas'],
            'title': 'Tablero de cobertura y venta cruzada',
            'summary': 'Qué líneas de producto compra cada punto de venta y dónde están las oportunidades de venta cruzada, por distribuidor y por vendedor.',
            'app_title': 'Cobertura de puntos de venta · Ciclo junio 2025',
            'filters': [('Ciclo', 'Junio 2025'), ('Distribuidor', 'Todos'), ('Vendedor', 'Todos')],
            'kpis': [
                {'label': 'Puntos de venta en cartera', 'value': '3.215', 'delta': '▲ 2,6% vs. ciclo anterior', 'good': True},
                {'label': 'Cobertura Línea Clásica', 'value': '91,4%', 'delta': '▲ 1,2 pp', 'good': True},
                {'label': 'Cobertura Línea Premium', 'value': '63,8%', 'delta': '▲ 4,5 pp', 'good': True},
                {'label': 'Compran ambas líneas', 'value': '58,9%', 'delta': '▲ 3,9 pp', 'good': True},
            ],
            'panels': [
                {'type': 'stack', 'wide': True, 'title': 'Qué compra cada punto de venta',
                 'unit': '% de los puntos de venta en cartera',
                 'data': stacked_100([('classic', 'Solo Línea Clásica', 32.5), ('both', 'Ambas líneas', 58.9),
                                      ('premium', 'Solo Línea Premium', 4.9), ('none', 'Sin compra en el ciclo', 3.7)])},
                {'type': 'grouped', 'title': 'Cobertura por distribuidor', 'unit': '% de puntos de venta que compran cada línea',
                 'legend': [('classic', 'Línea Clásica'), ('premium', 'Línea Premium')],
                 'data': grouped_bars(coverage, [('classic', 'Línea Clásica'), ('premium', 'Línea Premium')])},
                {'type': 'opportunities', 'title': 'Oportunidades de venta cruzada',
                 'caption': 'Puntos de venta que compran Línea Clásica pero no Premium',
                 'rows': [{'zone': z, 'seller': s, 'pdv': num(p), 'potential': money_m(m)} for z, s, p, m in opportunities]},
            ],
            'story': {
                'challenge': 'El equipo comercial sabe cuánto vende, pero no en qué puntos de venta falta cada línea de producto ni qué vendedor tiene más oportunidades.',
                'solution': 'Cruzamos las compras de cada punto de venta por línea de producto y armamos un tablero de cobertura con ranking por distribuidor y listas por vendedor.',
                'benefit': 'Cada vendedor sale a la calle con una lista concreta de clientes a los que ofrecerles la línea que todavía no compran.',
            },
        },
        {
            'id': 'pronostico',
            'tags': ['Distribución y retail', 'Modelos predictivos'],
            'title': 'Tablero de pronóstico y reposición',
            'summary': 'Un modelo de Machine Learning que anticipa la demanda de las próximas semanas y recomienda cuánto reponer de cada producto.',
            'app_title': 'Pronóstico de demanda · Depósito central',
            'filters': [('Horizonte', '8 semanas'), ('Categoría', 'Todas'), ('Depósito', 'Central')],
            'kpis': [
                {'label': 'Precisión del pronóstico', 'value': '92,4%', 'delta': '▲ 6,1 pp vs. método anterior', 'good': True},
                {'label': 'Demanda prevista (8 sem.)', 'value': f'{num(sum(forecast) * 1000)} u.', 'delta': '▲ 12,5% vs. últimas 8 sem.', 'good': True},
                {'label': 'Productos con riesgo de quiebre', 'value': str(sum(v for _, v in risk)), 'delta': '▼ 12 vs. semana anterior', 'good': True},
                {'label': 'Sobrestock estimado', 'value': '$ 2,3 M', 'delta': '▼ 18% vs. trimestre anterior', 'good': True},
            ],
            'panels': [
                {'type': 'line', 'wide': True, 'title': 'Ventas semanales y pronóstico', 'unit': 'Miles de unidades',
                 'legend': [('real', 'Real'), ('forecast', 'Pronóstico'), ('band', 'Rango probable')],
                 'data': line_forecast(history, forecast, spread, 18, 34, 4,
                                       [(0, 'Sem. 1'), (7, 'Sem. 8'), (15, 'Sem. 16'), (23, 'Sem. 24')])},
                {'type': 'bars', 'title': 'Riesgo de quiebre por categoría', 'unit': 'Cantidad de productos',
                 'data': bar_list(risk, lambda v: num(v), 'Categoría')},
                {'type': 'replenish', 'title': 'Reposición sugerida',
                 'caption': 'Próximas 2 semanas, en unidades',
                 'rows': [{'product': p, 'stock': num(s), 'demand': num(d), 'suggested': suggested_order(s, d),
                           'status': stock_status(s, d)} for p, s, d in replenish]},
            ],
            'story': {
                'challenge': 'Las compras se planifican con promedios históricos: algunos productos se quedan sin stock en los picos y otros se acumulan en el depósito.',
                'solution': 'Entrenamos un modelo que combina el historial de ventas con la estacionalidad y las promociones, y lo integramos en un tablero de reposición semanal.',
                'benefit': 'El equipo de compras sabe qué reponer y cuánto antes de que falte, y libera capital inmovilizado en sobrestock.',
            },
        },
    ]


EXAMPLES = build_examples()
