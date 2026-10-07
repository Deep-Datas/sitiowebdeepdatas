"""Casos de éxito.

Cada caso se publica solo cuando 'publicado' es True. Mientras esté en
False es un borrador: no aparece en el sitio, pero se puede revisar con

    python build.py --borradores

que genera una vista previa en vista-previa/ (esa carpeta no se sube).

Cada caso lleva de uno a tres resultados, que deben ser reales y verificables.
'duration' es opcional (None para no mostrarla). Además, si el cliente no autoriza
su nombre, usá una descripción ('Empresa multinacional de consumo masivo')
y dejá 'logo' en None.
"""

PENDIENTE = '[completar]'

CASES = [
    {
        'id': 'distribuidores',
        'short': 'Red de distribuidores',
        'publicado': True,
        'client': 'Empresa de consumo masivo líder en la comercialización de papas fritas',
        'logo': None,                       # por ejemplo 'clientes/mccain.png' si el cliente lo autoriza
        'industry': 'Consumo masivo',
        'title': 'Una sola versión de las ventas para toda la red de distribuidores',
        'summary': 'Unificamos las ventas que cada distribuidor informaba en su propia planilla en un tablero que se actualiza solo.',
        'results': [
            ('40', 'distribuidores integrados en un único modelo'),
        ],
        'challenge': 'Cada distribuidor enviaba sus ventas en planillas con formatos y criterios propios. Consolidarlas llevaba días de trabajo manual y la dirección no confiaba del todo en el número final.',
        'solution': 'Automatizamos la recepción de los archivos, unificamos códigos de producto y cliente, y publicamos un tablero de performance con filtros por región, canal y categoría.',
        'outcome': 'La dirección y el equipo comercial trabajan con el mismo número y detectan a tiempo qué distribuidor o canal se aleja del objetivo.',
        'sources': ['Excel y planillas', 'Archivos .txt y .csv', 'ERP'],
        'stack': ['Power BI', 'Azure', 'SQL'],
        'duration': None,
        'quote': None,                      # ('Texto del testimonio', 'Nombre Apellido', 'Cargo, Empresa')
        'example': 'distribuidores',        # tablero de ejemplo relacionado en /ejemplos/
    },
    {
        'id': 'cobertura',
        'short': 'Cobertura y venta cruzada',
        'publicado': False,
        'client': 'Empresa de alimentos',
        'logo': None,
        'industry': 'Consumo masivo',
        'title': 'Cada vendedor sabe a qué cliente ofrecerle qué producto',
        'summary': 'Cruzamos las compras de cada punto de venta por línea de producto para encontrar oportunidades de venta cruzada.',
        'results': [
            (PENDIENTE, 'puntos de venta analizados'),
            (PENDIENTE, 'aumento de la cobertura de las líneas foco'),
            (PENDIENTE, 'oportunidades de venta cruzada identificadas'),
        ],
        'challenge': 'El equipo comercial conocía el volumen de ventas, pero no en qué puntos de venta faltaba cada línea de producto ni qué vendedor tenía más oportunidades.',
        'solution': 'Integramos las ventas por punto de venta del ERP con la cartera de cada vendedor y armamos un tablero de cobertura con listas de oportunidades por vendedor.',
        'outcome': 'Cada vendedor sale a la calle con una lista concreta de clientes a los que ofrecerles la línea que todavía no compran.',
        'sources': ['ERP', 'CRM', 'Excel y planillas'],
        'stack': ['Power BI', 'SQL'],
        'duration': PENDIENTE,
        'quote': None,
        'example': 'cobertura',
    },
    {
        'id': 'pronostico',
        'short': 'Pronóstico de demanda',
        'publicado': True,
        'client': 'Distribuidora mayorista',
        'logo': None,
        'industry': 'Distribución y retail',
        'title': 'Compras planificadas con un pronóstico de demanda',
        'summary': 'Un modelo predictivo que anticipa la demanda semanal y sugiere qué reponer antes de que falte.',
        'results': [
            ('12%', 'menos quiebres de stock'),
        ],
        'challenge': 'Las compras se planificaban con promedios históricos: algunos productos se quedaban sin stock en los picos y otros se acumulaban en el depósito.',
        'solution': 'Entrenamos un modelo que combina el historial de ventas con la estacionalidad y las promociones, y lo integramos en un tablero de reposición semanal.',
        'outcome': 'El equipo de compras sabe qué reponer y cuánto antes de que falte.',
        'sources': ['ERP', 'APIs y e-commerce'],
        'stack': ['Python', 'Azure', 'Power BI'],
        'duration': None,
        'quote': None,
        'example': 'pronostico',
    },
]


# Textos de cada caso en inglés (para /en/case-studies/). Mismas claves que en CASES;
# lo que no está acá se toma del caso en español.
CASES_EN = {
    'distribuidores': {
        'short': 'Distributor network',
        'client': 'Leading consumer goods company in the potato chip market',
        'industry': 'Consumer goods',
        'title': 'A single version of sales for the entire distributor network',
        'summary': 'We brought the sales each distributor reported in its own spreadsheet into a dashboard that updates itself.',
        'results': [
            ('40', 'distributors integrated into a single model'),
        ],
        'challenge': 'Each distributor sent its sales in spreadsheets with its own formats and criteria. Consolidating them took days of manual work and leadership didn’t fully trust the final number.',
        'solution': 'We automated how the files are received, unified product and customer codes, and published a performance dashboard with filters by region, channel and category.',
        'outcome': 'Leadership and the sales team work with the same number and spot early which distributor or channel is drifting away from target.',
        'sources': ['Excel and spreadsheets', '.txt and .csv files', 'ERP'],
    },
    'cobertura': {
        'short': 'Coverage and cross-selling',
        'client': 'Food company',
        'industry': 'Consumer goods',
        'title': 'Every sales rep knows which product to offer each customer',
        'summary': 'We cross-referenced each point of sale’s purchases by product line to find cross-selling opportunities.',
        'results': [
            (PENDIENTE, 'points of sale analyzed'),
            (PENDIENTE, 'increase in coverage of focus lines'),
            (PENDIENTE, 'cross-selling opportunities identified'),
        ],
        'challenge': 'The sales team knew its sales volume, but not which points of sale were missing each product line or which rep had the most opportunities.',
        'solution': 'We integrated point-of-sale sales from the ERP with each rep’s accounts and built a coverage dashboard with opportunity lists by sales rep.',
        'outcome': 'Every sales rep heads out with a concrete list of customers to offer the line they don’t buy yet.',
        'sources': ['ERP', 'CRM', 'Excel and spreadsheets'],
    },
    'pronostico': {
        'short': 'Demand forecasting',
        'client': 'Wholesale distributor',
        'industry': 'Distribution and retail',
        'title': 'Purchasing planned with a demand forecast',
        'summary': 'A predictive model that anticipates weekly demand and suggests what to restock before it runs out.',
        'results': [
            ('12%', 'fewer stockouts'),
        ],
        'challenge': 'Purchasing was planned with historical averages: some products ran out of stock at peak times while others piled up in the warehouse.',
        'solution': 'We trained a model that combines sales history with seasonality and promotions, and integrated it into a weekly replenishment dashboard.',
        'outcome': 'The purchasing team knows what to restock, and how much, before it runs out.',
        'sources': ['ERP', 'APIs and e-commerce'],
    },
}


def localized_cases(cases, lang):
    """Casos con los textos del idioma pedido."""
    if lang == 'es':
        return cases
    texts = {'en': CASES_EN}[lang]
    return [{**case, **texts.get(case['id'], {})} for case in cases]
