"""Contenido y geometría del gráfico «Del dato disperso al agente de IA».

El gráfico de escritorio es un SVG con coordenadas fijas (viewBox); en
pantallas chicas se muestra una versión apilada en HTML con el mismo
contenido. Para cambiar un texto, editalo acá (CONTENT, en cada idioma) y
volvé a ejecutar build.py.
"""

SOURCES_ES = [
    ('crm', 'person-lines-fill', 'CRM', 'Salesforce · HubSpot',
     'Clientes, oportunidades y contactos. Suelen tener registros duplicados, campos incompletos y vendedores que cargan distinto.'),
    ('erp', 'building-gear', 'ERP', 'SAP · Tango · Odoo',
     'Ventas, compras, stock y finanzas. La fuente más confiable, pero con códigos y estructuras pensadas para operar, no para analizar.'),
    ('excel', 'file-earmark-spreadsheet', 'Excel y planillas', 'Objetivos · precios · stock',
     'Objetivos comerciales, listas de precios y controles manuales. Cada área tiene su versión y los formatos cambian mes a mes.'),
    ('txt', 'file-earmark-text', 'Archivos .txt y .csv', 'Exportaciones · logs',
     'Exportaciones de sistemas, reportes de distribuidores y registros. Separadores, codificaciones y fechas distintas en cada archivo.'),
    ('whatsapp', 'whatsapp', 'WhatsApp', 'Pedidos · consultas',
     'Pedidos, reclamos y consultas de clientes en texto libre. Información valiosa que casi nunca llega a los sistemas.'),
    ('email', 'envelope', 'Email', 'Pedidos · adjuntos',
     'Órdenes de compra, confirmaciones y adjuntos que se procesan a mano y quedan en la bandeja de entrada de cada persona.'),
    ('db', 'database', 'Bases de datos', 'SQL Server · Oracle',
     'Sistemas propios y heredados con años de historia, tablas sin documentar y reglas de negocio escondidas.'),
    ('api', 'cloud-arrow-down', 'APIs y e-commerce', 'Mercado Libre · Shopify',
     'Ventas online, logística y servicios externos. Datos en tiempo real que hay que integrar con el resto.'),
]

STEPS_ES = [
    ('ingesta', 'inboxes', 'Ingesta', 'Conectamos y centralizamos',
     'Conectamos cada fuente de forma automática y segura, y centralizamos los datos en un único repositorio, con actualizaciones programadas.'),
    ('limpieza', 'eraser', 'Limpieza', 'Errores y faltantes',
     'Corregimos errores de carga, formatos inválidos y valores faltantes, y extraemos datos útiles de textos libres como mensajes y correos.'),
    ('dedup', 'intersect', 'Deduplicación', 'Un registro por entidad',
     'Unificamos clientes, productos y proveedores repetidos entre sistemas para que cada uno tenga un único registro.'),
    ('normalizacion', 'rulers', 'Normalización', 'Unidades, monedas, fechas',
     'Llevamos todo a las mismas unidades, monedas, fechas y códigos, para que los datos de distintas fuentes se puedan comparar.'),
    ('validacion', 'shield-check', 'Validación', 'Reglas de calidad',
     'Aplicamos reglas de calidad en cada actualización y generamos alertas cuando algo no cierra, antes de que llegue a una decisión.'),
    ('orden', 'sort-down', 'Ordenamiento', 'Modelo y catálogo',
     'Organizamos la información en un modelo de datos documentado, con permisos y trazabilidad: listo para tableros y para la IA.'),
]

AGENT_ES = ('agente', 'robot', 'Agente de IA', 'Consume datos confiables',
         'Un agente de inteligencia artificial conectado a datos curados responde con precisión, sin inventar números: '
         'consulta, cruza y analiza la información de toda la empresa en segundos.')

OUTPUTS_ES = [
    ('respuestas', 'chat-dots', 'Respuestas', 'En lenguaje natural',
     '«¿Cuánto vendimos en el norte este mes?» El agente responde al instante, con datos verificables.'),
    ('pronosticos', 'graph-up-arrow', 'Pronósticos', 'Ventas y demanda',
     'Proyecciones de ventas, demanda y stock para planificar compras y producción con anticipación.'),
    ('alertas', 'bell', 'Alertas', 'Proactivas y a tiempo',
     'Avisos automáticos cuando un cliente deja de comprar, un producto se queda sin stock o un indicador se desvía.'),
    ('automatizacion', 'lightning-charge', 'Automatización', 'Tareas repetitivas',
     'Carga de pedidos recibidos por WhatsApp o email, informes periódicos y respuestas a consultas frecuentes.'),
]

SOURCES_EN = [
    ('crm', 'person-lines-fill', 'CRM', 'Salesforce · HubSpot',
     'Customers, opportunities and contacts. Often full of duplicate records, incomplete fields and reps who enter data differently.'),
    ('erp', 'building-gear', 'ERP', 'SAP · Odoo · Dynamics',
     'Sales, purchasing, inventory and finance. The most reliable source, but with codes and structures built to operate, not to analyze.'),
    ('excel', 'file-earmark-spreadsheet', 'Excel and spreadsheets', 'Targets · prices · stock',
     'Sales targets, price lists and manual checks. Every team has its own version and formats change month to month.'),
    ('txt', 'file-earmark-text', '.txt and .csv files', 'Exports · logs',
     'System exports, distributor reports and logs. Different separators, encodings and dates in every file.'),
    ('whatsapp', 'whatsapp', 'WhatsApp', 'Orders · inquiries',
     'Customer orders, complaints and questions in free text. Valuable information that rarely reaches your systems.'),
    ('email', 'envelope', 'Email', 'Orders · attachments',
     'Purchase orders, confirmations and attachments processed by hand and left in each person’s inbox.'),
    ('db', 'database', 'Databases', 'SQL Server · Oracle',
     'In-house and legacy systems with years of history, undocumented tables and hidden business rules.'),
    ('api', 'cloud-arrow-down', 'APIs and e-commerce', 'Mercado Libre · Shopify',
     'Online sales, logistics and external services. Real-time data that has to be integrated with everything else.'),
]

STEPS_EN = [
    ('ingesta', 'inboxes', 'Ingestion', 'Connect and centralize',
     'We connect every source automatically and securely, and centralize the data in a single repository with scheduled updates.'),
    ('limpieza', 'eraser', 'Cleaning', 'Errors and gaps',
     'We fix data-entry errors, invalid formats and missing values, and extract useful data from free text such as messages and emails.'),
    ('dedup', 'intersect', 'Deduplication', 'One record per entity',
     'We merge duplicate customers, products and suppliers across systems so each one has a single record.'),
    ('normalizacion', 'rulers', 'Standardization', 'Units, currencies, dates',
     'We bring everything to the same units, currencies, dates and codes so data from different sources can be compared.'),
    ('validacion', 'shield-check', 'Validation', 'Quality rules',
     'We apply quality rules on every update and raise alerts when something doesn’t add up, before it reaches a decision.'),
    ('orden', 'sort-down', 'Organization', 'Model and catalog',
     'We organize the information into a documented data model with permissions and lineage: ready for dashboards and for AI.'),
]

AGENT_EN = ('agente', 'robot', 'AI agent', 'Runs on trusted data',
            'An artificial intelligence agent connected to curated data answers accurately, without making up numbers: '
            'it queries, cross-references and analyzes information from across the company in seconds.')

OUTPUTS_EN = [
    ('respuestas', 'chat-dots', 'Answers', 'In plain language',
     '“How much did we sell in the north this month?” The agent answers instantly, with verifiable data.'),
    ('pronosticos', 'graph-up-arrow', 'Forecasts', 'Sales and demand',
     'Sales, demand and inventory projections to plan purchasing and production ahead of time.'),
    ('alertas', 'bell', 'Alerts', 'Proactive and timely',
     'Automatic notices when a customer stops buying, a product runs out of stock or a KPI drifts off course.'),
    ('automatizacion', 'lightning-charge', 'Automation', 'Repetitive tasks',
     'Entering orders received by WhatsApp or email, periodic reports and answers to frequent questions.'),
]

# Contenido y rótulos de cada idioma
CONTENT = {
    'es': {
        'sources': SOURCES_ES, 'steps': STEPS_ES, 'agent': AGENT_ES, 'outputs': OUTPUTS_ES,
        'stage_source': 'Origen de datos', 'stage_step': 'Paso {i} de {n} · Curado',
        'stage_agent': 'Inteligencia artificial', 'stage_output': 'Resultado',
        'columns': ['Orígenes de datos', 'Curado y ordenamiento', 'Inteligencia artificial', 'Resultados'],
        'labels': {
            'curated': 'Datos curados', 'raw': 'Datos crudos',
            'cur_kicker': 'Etapa de curado', 'cur_title': 'Limpieza y ordenamiento',
            'journey': 'Recorrido de los datos',
            'stack_sources': 'Orígenes de datos', 'stack_curation': 'Curado, limpieza y ordenamiento',
            'stack_results': 'Resultados',
            'legend_raw': 'Datos crudos: dispersos, duplicados e inconsistentes',
            'legend_curated': 'Datos curados: limpios, unificados y documentados',
        },
    },
    'en': {
        'sources': SOURCES_EN, 'steps': STEPS_EN, 'agent': AGENT_EN, 'outputs': OUTPUTS_EN,
        'stage_source': 'Data source', 'stage_step': 'Step {i} of {n} · Curation',
        'stage_agent': 'Artificial intelligence', 'stage_output': 'Outcome',
        'columns': ['Data sources', 'Curation and organization', 'Artificial intelligence', 'Outcomes'],
        'labels': {
            'curated': 'Curated data', 'raw': 'Raw data',
            'cur_kicker': 'Curation stage', 'cur_title': 'Cleaning and organization',
            'journey': 'Data journey',
            'stack_sources': 'Data sources', 'stack_curation': 'Curation, cleaning and organization',
            'stack_results': 'Outcomes',
            'legend_raw': 'Raw data: scattered, duplicated and inconsistent',
            'legend_curated': 'Curated data: clean, unified and documented',
        },
    },
}

# Geometría (unidades del viewBox)
WIDTH, HEIGHT = 1120, 640
TOP = 56            # debajo de los títulos de columna
SRC_X, SRC_W, SRC_H, SRC_GAP = 0, 220, 56, 14
CUR_X, CUR_W = 310, 300
STEP_H, STEP_GAP = 58, 12
AGENT_R = 72
AGENT_CX = 770
OUT_X, OUT_W, OUT_H, OUT_GAP = 900, 220, 60, 20


def _node(item, x, y, w, h, kind, stage):
    key, icon_name, title, sub, text = item
    return {'id': f'{kind}-{key}', 'icon': icon_name, 'title': title, 'sub': sub, 'text': text,
            'x': x, 'y': y, 'w': w, 'h': h, 'cy': y + h / 2, 'kind': kind, 'stage': stage}


def _curve(x1, y1, x2, y2):
    mid = (x1 + x2) / 2
    return f'M{x1:.1f} {y1:.1f} C{mid:.1f} {y1:.1f} {mid:.1f} {y2:.1f} {x2:.1f} {y2:.1f}'


def pipeline(lang='es'):
    c = CONTENT[lang]
    SOURCES, STEPS, AGENT, OUTPUTS = c['sources'], c['steps'], c['agent'], c['outputs']
    area = HEIGHT - TOP
    mid_y = TOP + area / 2

    # Orígenes
    total = len(SOURCES) * SRC_H + (len(SOURCES) - 1) * SRC_GAP
    y0 = TOP + (area - total) / 2
    sources = [_node(s, SRC_X, y0 + i * (SRC_H + SRC_GAP), SRC_W, SRC_H, 'src', c['stage_source'])
               for i, s in enumerate(SOURCES)]

    # Etapa de curado: tarjeta con los pasos adentro
    head = 64
    steps_h = len(STEPS) * STEP_H + (len(STEPS) - 1) * STEP_GAP
    cur_h = head + steps_h + 20
    cur_y = mid_y - cur_h / 2
    steps = [_node(s, CUR_X + 16, cur_y + head + i * (STEP_H + STEP_GAP), CUR_W - 32, STEP_H, 'step',
                   c['stage_step'].format(i=i + 1, n=len(STEPS)))
             for i, s in enumerate(STEPS)]
    curation = {'x': CUR_X, 'y': cur_y, 'w': CUR_W, 'h': cur_h}

    # Las líneas de entrada llegan repartidas sobre el borde izquierdo de la tarjeta
    span = steps_h * 0.7
    entries = [mid_y - span / 2 + i * span / (len(sources) - 1) for i in range(len(sources))]
    for node, ey in zip(sources, entries):
        node['link'] = _curve(SRC_X + SRC_W, node['cy'], CUR_X, ey)

    # Conectores entre pasos
    step_links = [(steps[i]['x'] + 31, steps[i]['y'] + STEP_H, steps[i + 1]['y'])
                  for i in range(len(steps) - 1)]

    agent = _node(AGENT, AGENT_CX - AGENT_R, mid_y - AGENT_R, AGENT_R * 2, AGENT_R * 2, 'agent',
                  c['stage_agent'])
    agent.update(cx=AGENT_CX, r=AGENT_R)
    curated_link = f'M{CUR_X + CUR_W} {mid_y:.1f} H{AGENT_CX - AGENT_R}'

    total = len(OUTPUTS) * OUT_H + (len(OUTPUTS) - 1) * OUT_GAP
    y0 = mid_y - total / 2
    outputs = [_node(o, OUT_X, y0 + i * (OUT_H + OUT_GAP), OUT_W, OUT_H, 'out', c['stage_output'])
               for i, o in enumerate(OUTPUTS)]
    for node in outputs:
        node['link'] = _curve(AGENT_CX + AGENT_R, mid_y, OUT_X, node['cy'])

    # Qué se resalta al pasar por cada elemento: su recorrido completo
    downstream = ['cur'] + [s['id'] for s in steps] + ['curated', agent['id']]
    results = [o['id'] for o in outputs] + [o['id'] + '-link' for o in outputs]
    for node in sources:
        node['chain'] = [node['id'], node['id'] + '-link'] + downstream + results
    for node in steps:
        node['chain'] = [node['id'], 'cur']
    agent['chain'] = ['curated', agent['id']] + results
    for node in outputs:
        node['chain'] = [node['id'], node['id'] + '-link', agent['id'], 'curated']

    columns = [(x, str(i + 1), label) for i, (x, label) in
               enumerate(zip([SRC_X + SRC_W / 2, CUR_X + CUR_W / 2, AGENT_CX, OUT_X + OUT_W / 2], c['columns']))]

    return {
        'width': WIDTH, 'height': HEIGHT, 'mid_y': mid_y, 'columns': columns,
        'sources': sources, 'steps': steps, 'step_links': step_links, 'curation': curation,
        'agent': agent, 'curated_link': curated_link, 'curated_label_x': (CUR_X + CUR_W + AGENT_CX - AGENT_R) / 2,
        'outputs': outputs, 'labels': c['labels'],
    }
