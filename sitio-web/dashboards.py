"""Tableros de ejemplo del sitio, con datos ficticios, en español y en inglés.

Cada tablero se describe con datos simples (valores, etiquetas) y las
funciones de este módulo calculan las posiciones de barras, puntos y
líneas en porcentajes. Las plantillas de src/charts.html los dibujan.
Para cambiar un ejemplo, editá los valores en build_examples() y los textos
de cada idioma en TEXT, y regenerá el sitio.
"""


# ---------- Formatos de números según el idioma ----------

class Fmt:
    """Formatos de cada idioma: en español, punto de miles y coma decimal; en inglés, al revés."""

    def __init__(self, lang):
        self.lang = lang
        self.t = TEXT[lang]

    def num(self, value, decimals=0):
        text = f'{value:,.{decimals}f}'
        if self.lang == 'es':
            text = text.replace(',', 'X').replace('.', ',').replace('X', '.')
        return text

    def money_m(self, value):
        return f'$ {self.num(value, 1)} M' if self.lang == 'es' else f'${self.num(value, 1)}M'

    def pct(self, value, decimals=1):
        return f'{self.num(value, decimals)}%'


# ---------- Geometría de cada tipo de gráfico ----------

def columns_with_target(f, labels, values, targets, step, top, fmt):
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
    ticks = [{'label': f.num(v), 'y': v / top * 100} for v in range(0, int(top) + 1, step)]
    table = {'headers': f.t['columns_head'],
             'rows': [[i['label'], i['value_label'], i['target_label']] for i in items]}
    return {'items': items, 'ticks': ticks, 'table': table}


def bar_list(f, rows, fmt, label_header):
    """Barras horizontales de una sola serie, ordenadas de mayor a menor."""
    rows = sorted(rows, key=lambda r: r[1], reverse=True)
    top = max(v for _, v in rows)
    return {
        'items': [{'label': label, 'value_label': fmt(value), 'w': value / top * 100} for label, value in rows],
        'table': {'headers': [label_header, f.t['value']], 'rows': [[label, fmt(value)] for label, value in rows]},
    }


def grouped_bars(f, rows, series):
    """Barras horizontales agrupadas (porcentajes de 0 a 100)."""
    return {
        'items': [{
            'label': label,
            'bars': [{'key': key, 'name': name, 'value_label': f.pct(v, 0), 'w': v} for (key, name), v in zip(series, values)],
        } for label, values in rows],
        'table': {'headers': [f.t['distributor']] + [name for _, name in series],
                  'rows': [[label] + [f.pct(v, 0) for v in values] for label, values in rows]},
    }


def stacked_100(f, segments):
    """Barra 100% apilada: composición de un total."""
    total = sum(v for _, _, v in segments)
    out = []
    for key, label, value in segments:
        share = value / total * 100
        out.append({'key': key, 'label': label, 'value_label': f.pct(share), 'w': share, 'inside': share >= 12})
    return out


def line_forecast(f, history, forecast, spread, low, high, step, x_labels):
    """Serie real + pronóstico con banda de confianza, en coordenadas 0-100."""
    t = f.t
    n = len(history) + len(forecast) - 1
    first = len(history) - 1

    def x(i):
        return i / n * 100

    def y(v):
        return 100 - (v - low) / (high - low) * 100

    def path(points):
        return 'M' + ' L'.join(f'{a:.2f} {b:.2f}' for a, b in points)

    def span(j):
        return t['range'].format(lo=f.num(forecast[j] - spread[j], 1), hi=f.num(forecast[j] + spread[j], 1))

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
        week = t['week'].format(n=i + 1)
        lines = []
        if i < len(history):
            lines.append(('real', t['tip_real'].format(v=f.num(history[i], 1))))
        else:
            j = i - len(history)
            lines.append(('forecast', t['tip_forecast'].format(v=f.num(forecast[j], 1))))
            lines.append(('band', t['tip_range'].format(span=span(j))))
        hits.append({'x': x(i), 'left': max(x(i) - width / 2, 0), 'w': width if 0 < i < n else width / 2,
                     'title': week, 'lines': lines})
        if i < len(history):
            table_rows.append([week, f.num(history[i], 1), '—', '—'])
        else:
            j = i - len(history)
            table_rows.append([week, '—', f.num(forecast[j], 1), span(j)])

    return {
        'real_line': path(real),
        'real_area': path(real) + f' L{real[-1][0]:.2f} 100 L0 100 Z',
        'forecast_line': path(fc),
        'band': path(band) + ' Z',
        'real_end': {'x': real[-1][0], 'y': 100 - real[-1][1], 'label': t['thousands'].format(v=f.num(history[-1], 1))},
        'forecast_end': {'x': fc[-1][0], 'y': 100 - fc[-1][1], 'label': t['thousands'].format(v=f.num(forecast[-1], 1))},
        'split_x': x(first),
        'ticks': [{'label': f.num(v), 'y': (v - low) / (high - low) * 100} for v in range(low, high + 1, step)],
        'x_labels': [{'label': label, 'x': x(i)} for i, label in x_labels],
        'hits': hits,
        'table': {'headers': t['line_head'], 'rows': table_rows},
    }


def status(f, attainment):
    labels = f.t['status']
    if attainment >= 100:
        return {'key': 'good', 'label': labels['good'], 'icon': 'check-circle-fill'}
    if attainment >= 95:
        return {'key': 'warning', 'label': labels['warning'], 'icon': 'exclamation-circle-fill'}
    return {'key': 'critical', 'label': labels['critical'], 'icon': 'x-circle-fill'}


def stock_status(f, stock, demand):
    labels = f.t['stock_status']
    ratio = stock / demand
    if ratio < 0.7:
        return {'key': 'critical', 'label': labels['critical'], 'icon': 'x-circle-fill'}
    if ratio < 1:
        return {'key': 'warning', 'label': labels['warning'], 'icon': 'exclamation-circle-fill'}
    return {'key': 'good', 'label': labels['good'], 'icon': 'check-circle-fill'}


def suggested_order(f, stock, demand):
    """Unidades a reponer, redondeadas a la centena."""
    gap = demand - stock
    return f.num(-(-gap // 100) * 100) if gap > 0 else '—'


# ---------- Textos de cada idioma ----------

TEXT = {
    'es': {
        'columns_head': ['Mes', 'Real', 'Objetivo'],
        'value': 'Valor',
        'distributor': 'Distribuidor',
        'week': 'Semana {n}',
        'tip_real': 'Real: {v} mil u.',
        'tip_forecast': 'Pronóstico: {v} mil u.',
        'tip_range': 'Rango: {span}',
        'range': '{lo} a {hi}',
        'thousands': '{v} mil',
        'line_head': ['Semana', 'Real (miles)', 'Pronóstico (miles)', 'Rango probable'],
        'status': {'good': 'En objetivo', 'warning': 'Atención', 'critical': 'Debajo'},
        'stock_status': {'good': 'Cubierto', 'warning': 'Atención', 'critical': 'Reponer ya'},
        'months': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        'distributors': ['Distribuidora Centro', 'Distribuidora Norte', 'Distribuidora Litoral',
                         'Distribuidora Cuyo', 'Distribuidora Sur', 'Distribuidora Patagonia'],
        'channels': ['Supermercados', 'Mayoristas', 'Autoservicios', 'Kioscos y almacenes', 'E-commerce'],
        'regions': ['Centro', 'Litoral', 'Norte', 'Sur', 'Cuyo', 'Patagonia'],
        'seller': 'Vendedor {n}',
        'categories': ['Bebidas', 'Snacks', 'Lácteos', 'Limpieza', 'Congelados'],
        'products': ['Gaseosa cola 2,25 L', 'Papas fritas 150 g', 'Yogur bebible 1 L', 'Helado 1 kg', 'Detergente 750 ml'],
        'distribuidores': {
            'tags': ['Consumo masivo', 'Ventas y distribución'],
            'title': 'Tablero de performance de distribuidores',
            'summary': 'Una sola versión de los números para toda la red: facturación, volumen y cumplimiento del objetivo de cada distribuidor, mes a mes.',
            'app_title': 'Performance comercial · Red de distribuidores',
            'filters': [('Período', 'Ene–Dic 2025'), ('Región', 'Todas'), ('Canal', 'Todos')],
            'kpis': [('Facturación neta', None, '▲ 9,2% vs. 2024', True), ('Volumen vendido', '1.284 t', '▲ 4,1% vs. 2024', True),
                     ('Tamaño promedio de pedido', '412 kg', '▼ 2,3% vs. 2024', False), ('Clientes activos', '6.940', '▲ 3,8% vs. 2024', True)],
            'columns': 'Facturación mensual vs. objetivo', 'money_unit': 'Millones de $',
            'legend': [('real', 'Real'), ('target', 'Objetivo')],
            'by_channel': 'Facturación por canal', 'channel': 'Canal',
            'ranking': 'Ranking de distribuidores',
            'story': {
                'challenge': 'Las ventas llegan de cada distribuidor en planillas propias, con criterios distintos. Consolidarlas lleva días y nadie confía del todo en el número final.',
                'solution': 'Integramos las fuentes en un modelo único, unificamos criterios y publicamos un tablero que se actualiza solo, con filtros por región, canal, categoría y producto.',
                'benefit': 'La dirección y el equipo comercial ven el mismo número y detectan a tiempo qué distribuidor o canal se aleja del objetivo.',
            },
        },
        'cobertura': {
            'tags': ['Consumo masivo', 'Fuerza de ventas'],
            'title': 'Tablero de cobertura y venta cruzada',
            'summary': 'Qué líneas de producto compra cada punto de venta y dónde están las oportunidades de venta cruzada, por distribuidor y por vendedor.',
            'app_title': 'Cobertura de puntos de venta · Ciclo junio 2025',
            'filters': [('Ciclo', 'Junio 2025'), ('Distribuidor', 'Todos'), ('Vendedor', 'Todos')],
            'kpis': [('Puntos de venta en cartera', '3.215', '▲ 2,6% vs. ciclo anterior', True), ('Cobertura Línea Clásica', '91,4%', '▲ 1,2 pp', True),
                     ('Cobertura Línea Premium', '63,8%', '▲ 4,5 pp', True), ('Compran ambas líneas', '58,9%', '▲ 3,9 pp', True)],
            'stack': 'Qué compra cada punto de venta', 'stack_unit': '% de los puntos de venta en cartera',
            'segments': ['Solo Línea Clásica', 'Ambas líneas', 'Solo Línea Premium', 'Sin compra en el ciclo'],
            'grouped': 'Cobertura por distribuidor', 'grouped_unit': '% de puntos de venta que compran cada línea',
            'lines': ['Línea Clásica', 'Línea Premium'],
            'opportunities': 'Oportunidades de venta cruzada',
            'opportunities_caption': 'Puntos de venta que compran Línea Clásica pero no Premium',
            'story': {
                'challenge': 'El equipo comercial sabe cuánto vende, pero no en qué puntos de venta falta cada línea de producto ni qué vendedor tiene más oportunidades.',
                'solution': 'Cruzamos las compras de cada punto de venta por línea de producto y armamos un tablero de cobertura con ranking por distribuidor y listas por vendedor.',
                'benefit': 'Cada vendedor sale a la calle con una lista concreta de clientes a los que ofrecerles la línea que todavía no compran.',
            },
        },
        'pronostico': {
            'tags': ['Distribución y retail', 'Modelos predictivos'],
            'title': 'Tablero de pronóstico y reposición',
            'summary': 'Un modelo de Machine Learning que anticipa la demanda de las próximas semanas y recomienda cuánto reponer de cada producto.',
            'app_title': 'Pronóstico de demanda · Depósito central',
            'filters': [('Horizonte', '8 semanas'), ('Categoría', 'Todas'), ('Depósito', 'Central')],
            'kpis': [('Precisión del pronóstico', '92,4%', '▲ 6,1 pp vs. método anterior', True),
                     ('Demanda prevista (8 sem.)', None, '▲ 12,5% vs. últimas 8 sem.', True),
                     ('Productos con riesgo de quiebre', None, '▼ 12 vs. semana anterior', True),
                     ('Sobrestock estimado', '$ 2,3 M', '▼ 18% vs. trimestre anterior', True)],
            'units': '{v} u.',
            'line': 'Ventas semanales y pronóstico', 'line_unit': 'Miles de unidades',
            'legend': [('real', 'Real'), ('forecast', 'Pronóstico'), ('band', 'Rango probable')],
            'week_short': 'Sem. {n}',
            'risk': 'Riesgo de quiebre por categoría', 'risk_unit': 'Cantidad de productos', 'category': 'Categoría',
            'replenish': 'Reposición sugerida', 'replenish_caption': 'Próximas 2 semanas, en unidades',
            'story': {
                'challenge': 'Las compras se planifican con promedios históricos: algunos productos se quedan sin stock en los picos y otros se acumulan en el depósito.',
                'solution': 'Entrenamos un modelo que combina el historial de ventas con la estacionalidad y las promociones, y lo integramos en un tablero de reposición semanal.',
                'benefit': 'El equipo de compras sabe qué reponer y cuánto antes de que falte, y libera capital inmovilizado en sobrestock.',
            },
        },
    },
    'en': {
        'columns_head': ['Month', 'Actual', 'Target'],
        'value': 'Value',
        'distributor': 'Distributor',
        'week': 'Week {n}',
        'tip_real': 'Actual: {v}K units',
        'tip_forecast': 'Forecast: {v}K units',
        'tip_range': 'Range: {span}',
        'range': '{lo} to {hi}',
        'thousands': '{v}K',
        'line_head': ['Week', 'Actual (thousands)', 'Forecast (thousands)', 'Likely range'],
        'status': {'good': 'On target', 'warning': 'Watch', 'critical': 'Below'},
        'stock_status': {'good': 'Covered', 'warning': 'Watch', 'critical': 'Restock now'},
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'distributors': ['Central Distributor', 'North Distributor', 'Litoral Distributor',
                         'Cuyo Distributor', 'South Distributor', 'Patagonia Distributor'],
        'channels': ['Supermarkets', 'Wholesale', 'Self-service stores', 'Convenience stores', 'E-commerce'],
        'regions': ['Central', 'Litoral', 'North', 'South', 'Cuyo', 'Patagonia'],
        'seller': 'Sales rep {n}',
        'categories': ['Beverages', 'Snacks', 'Dairy', 'Cleaning', 'Frozen'],
        'products': ['Cola 2.25 L', 'Potato chips 150 g', 'Drinkable yogurt 1 L', 'Ice cream 1 kg', 'Dish soap 750 ml'],
        'distribuidores': {
            'tags': ['Consumer goods', 'Sales and distribution'],
            'title': 'Distributor performance dashboard',
            'summary': 'A single version of the numbers for the whole network: revenue, volume and target attainment for each distributor, month by month.',
            'app_title': 'Sales performance · Distributor network',
            'filters': [('Period', 'Jan–Dec 2025'), ('Region', 'All'), ('Channel', 'All')],
            'kpis': [('Net revenue', None, '▲ 9.2% vs. 2024', True), ('Volume sold', '1,284 t', '▲ 4.1% vs. 2024', True),
                     ('Average order size', '412 kg', '▼ 2.3% vs. 2024', False), ('Active customers', '6,940', '▲ 3.8% vs. 2024', True)],
            'columns': 'Monthly revenue vs. target', 'money_unit': '$ millions',
            'legend': [('real', 'Actual'), ('target', 'Target')],
            'by_channel': 'Revenue by channel', 'channel': 'Channel',
            'ranking': 'Distributor ranking',
            'story': {
                'challenge': 'Each distributor reports sales in its own spreadsheets, with different criteria. Consolidating them takes days and nobody fully trusts the final number.',
                'solution': 'We integrate the sources into a single model, align the criteria and publish a self-updating dashboard with filters by region, channel, category and product.',
                'benefit': 'Leadership and the sales team see the same number and spot early which distributor or channel is drifting away from target.',
            },
        },
        'cobertura': {
            'tags': ['Consumer goods', 'Sales force'],
            'title': 'Coverage and cross-selling dashboard',
            'summary': 'Which product lines each point of sale buys and where the cross-selling opportunities are, by distributor and by sales rep.',
            'app_title': 'Point-of-sale coverage · June 2025 cycle',
            'filters': [('Cycle', 'June 2025'), ('Distributor', 'All'), ('Sales rep', 'All')],
            'kpis': [('Points of sale in portfolio', '3,215', '▲ 2.6% vs. previous cycle', True), ('Classic Line coverage', '91.4%', '▲ 1.2 pp', True),
                     ('Premium Line coverage', '63.8%', '▲ 4.5 pp', True), ('Buy both lines', '58.9%', '▲ 3.9 pp', True)],
            'stack': 'What each point of sale buys', 'stack_unit': '% of points of sale in portfolio',
            'segments': ['Classic Line only', 'Both lines', 'Premium Line only', 'No purchase this cycle'],
            'grouped': 'Coverage by distributor', 'grouped_unit': '% of points of sale buying each line',
            'lines': ['Classic Line', 'Premium Line'],
            'opportunities': 'Cross-selling opportunities',
            'opportunities_caption': 'Points of sale that buy the Classic Line but not the Premium Line',
            'story': {
                'challenge': 'The sales team knows how much it sells, but not which points of sale are missing each product line or which rep has the most opportunities.',
                'solution': 'We cross-reference each point of sale’s purchases by product line and build a coverage dashboard with a distributor ranking and lists by sales rep.',
                'benefit': 'Every sales rep heads out with a concrete list of customers to offer the line they don’t buy yet.',
            },
        },
        'pronostico': {
            'tags': ['Distribution and retail', 'Predictive models'],
            'title': 'Forecasting and replenishment dashboard',
            'summary': 'A machine learning model that anticipates demand for the coming weeks and recommends how much of each product to restock.',
            'app_title': 'Demand forecast · Central warehouse',
            'filters': [('Horizon', '8 weeks'), ('Category', 'All'), ('Warehouse', 'Central')],
            'kpis': [('Forecast accuracy', '92.4%', '▲ 6.1 pp vs. previous method', True),
                     ('Forecast demand (8 wks)', None, '▲ 12.5% vs. last 8 wks', True),
                     ('Products at risk of stockout', None, '▼ 12 vs. last week', True),
                     ('Estimated overstock', '$2.3M', '▼ 18% vs. last quarter', True)],
            'units': '{v} units',
            'line': 'Weekly sales and forecast', 'line_unit': 'Thousands of units',
            'legend': [('real', 'Actual'), ('forecast', 'Forecast'), ('band', 'Likely range')],
            'week_short': 'Wk {n}',
            'risk': 'Stockout risk by category', 'risk_unit': 'Number of products', 'category': 'Category',
            'replenish': 'Suggested replenishment', 'replenish_caption': 'Next 2 weeks, in units',
            'story': {
                'challenge': 'Purchasing is planned with historical averages: some products run out of stock at peak times while others pile up in the warehouse.',
                'solution': 'We train a model that combines sales history with seasonality and promotions, and integrate it into a weekly replenishment dashboard.',
                'benefit': 'The purchasing team knows what to restock, and how much, before it runs out, and frees up capital tied up in overstock.',
            },
        },
    },
}


# ---------- Ejemplos (datos ficticios) ----------

def build_examples(lang='es'):
    f = Fmt(lang)
    t = f.t

    revenue = [3.6, 3.4, 3.9, 3.8, 4.0, 4.1, 4.3, 4.2, 4.0, 4.3, 4.4, 4.6]
    objective = [3.8, 3.6, 3.9, 3.9, 4.0, 4.1, 4.2, 4.2, 4.2, 4.3, 4.4, 4.5]
    channels = list(zip(t['channels'], [17.4, 12.9, 9.8, 6.1, 2.4]))
    distributors = list(zip(t['distributors'], [12.8, 9.6, 8.7, 6.9, 5.8, 4.8], [104, 98, 101, 92, 96, 89]))  # facturación ($ M), % del objetivo

    # distribuidor, % PDV con Línea Clásica, % PDV con Línea Premium
    coverage = list(zip(t['regions'], [[95, 72], [93, 69], [92, 61], [90, 60], [88, 55], [86, 52]]))
    region = dict(zip(['Centro', 'Litoral', 'Norte', 'Sur', 'Cuyo', 'Patagonia'], t['regions']))
    opportunities = [  # zona y vendedor, PDV que compran Clásica y no Premium, potencial mensual
        (region['Norte'], t['seller'].format(n='07'), 148, 1.9), (region['Cuyo'], t['seller'].format(n='12'), 131, 1.6),
        (region['Sur'], t['seller'].format(n='03'), 117, 1.4), (region['Patagonia'], t['seller'].format(n='09'), 96, 1.1),
        (region['Centro'], t['seller'].format(n='15'), 84, 1.0),
    ]

    history = [21.2, 22.0, 21.6, 23.1, 22.8, 24.0, 23.5, 22.9, 24.6, 25.1, 24.3, 25.8, 26.2, 25.5, 26.9, 27.4]
    forecast = [27.9, 28.3, 27.6, 29.0, 29.4, 28.8, 30.1, 30.5]
    spread = [0.8, 1.1, 1.3, 1.6, 1.8, 2.0, 2.2, 2.4]
    risk = list(zip(t['categories'], [12, 9, 7, 5, 4]))
    replenish = list(zip(t['products'], [1840, 960, 1120, 380, 2400], [3200, 1450, 1300, 520, 1900]))  # stock, demanda prevista 2 semanas

    d, c, p = t['distribuidores'], t['cobertura'], t['pronostico']

    def kpis(rows, computed):
        # Los valores None se calculan a partir de los datos
        return [{'label': label, 'value': value if value is not None else computed[label], 'delta': delta, 'good': good}
                for label, value, delta, good in rows]

    return [
        {
            'id': 'distribuidores',
            'tags': d['tags'],
            'title': d['title'],
            'summary': d['summary'],
            'app_title': d['app_title'],
            'filters': d['filters'],
            'kpis': kpis(d['kpis'], {d['kpis'][0][0]: f.money_m(sum(revenue))}),
            'panels': [
                {'type': 'columns', 'wide': True, 'title': d['columns'],
                 'unit': d['money_unit'], 'legend': d['legend'],
                 'data': columns_with_target(f, t['months'], revenue, objective, 1, 5, f.money_m)},
                {'type': 'bars', 'title': d['by_channel'], 'unit': d['money_unit'],
                 'data': bar_list(f, channels, f.money_m, d['channel'])},
                {'type': 'ranking', 'title': d['ranking'],
                 'rows': [{'name': n, 'revenue': f.money_m(r), 'attainment': f'{a}%', 'meter': min(a, 120) / 120 * 100,
                           'status': status(f, a)} for n, r, a in distributors],
                 'target_x': 100 / 120 * 100},
            ],
            'story': d['story'],
        },
        {
            'id': 'cobertura',
            'tags': c['tags'],
            'title': c['title'],
            'summary': c['summary'],
            'app_title': c['app_title'],
            'filters': c['filters'],
            'kpis': kpis(c['kpis'], {}),
            'panels': [
                {'type': 'stack', 'wide': True, 'title': c['stack'],
                 'unit': c['stack_unit'],
                 'data': stacked_100(f, list(zip(['classic', 'both', 'premium', 'none'], c['segments'], [32.5, 58.9, 4.9, 3.7])))},
                {'type': 'grouped', 'title': c['grouped'], 'unit': c['grouped_unit'],
                 'legend': list(zip(['classic', 'premium'], c['lines'])),
                 'data': grouped_bars(f, coverage, list(zip(['classic', 'premium'], c['lines'])))},
                {'type': 'opportunities', 'title': c['opportunities'],
                 'caption': c['opportunities_caption'],
                 'rows': [{'zone': z, 'seller': s, 'pdv': f.num(n), 'potential': f.money_m(m)} for z, s, n, m in opportunities]},
            ],
            'story': c['story'],
        },
        {
            'id': 'pronostico',
            'tags': p['tags'],
            'title': p['title'],
            'summary': p['summary'],
            'app_title': p['app_title'],
            'filters': p['filters'],
            'kpis': kpis(p['kpis'], {p['kpis'][1][0]: p['units'].format(v=f.num(sum(forecast) * 1000)),
                                     p['kpis'][2][0]: str(sum(v for _, v in risk))}),
            'panels': [
                {'type': 'line', 'wide': True, 'title': p['line'], 'unit': p['line_unit'],
                 'legend': p['legend'],
                 'data': line_forecast(f, history, forecast, spread, 18, 34, 4,
                                       [(i, p['week_short'].format(n=i + 1)) for i in (0, 7, 15, 23)])},
                {'type': 'bars', 'title': p['risk'], 'unit': p['risk_unit'],
                 'data': bar_list(f, risk, lambda v: f.num(v), p['category'])},
                {'type': 'replenish', 'title': p['replenish'],
                 'caption': p['replenish_caption'],
                 'rows': [{'product': name, 'stock': f.num(s), 'demand': f.num(dem), 'suggested': suggested_order(f, s, dem),
                           'status': stock_status(f, s, dem)} for name, s, dem in replenish]},
            ],
            'story': p['story'],
        },
    ]


EXAMPLES = {'es': build_examples('es'), 'en': build_examples('en')}
