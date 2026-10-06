"""Contenido y geometría del gráfico «Del dato disperso al agente de IA».

El gráfico de escritorio es un SVG con coordenadas fijas (viewBox); en
pantallas chicas se muestra una versión apilada en HTML con el mismo
contenido. Para cambiar un texto, editalo acá y volvé a ejecutar build.py.
"""

SOURCES = [
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

STEPS = [
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

AGENT = ('agente', 'robot', 'Agente de IA', 'Consume datos confiables',
         'Un agente de inteligencia artificial conectado a datos curados responde con precisión, sin inventar números: '
         'consulta, cruza y analiza la información de toda la empresa en segundos.')

OUTPUTS = [
    ('respuestas', 'chat-dots', 'Respuestas', 'En lenguaje natural',
     '«¿Cuánto vendimos en el norte este mes?» El agente responde al instante, con datos verificables.'),
    ('pronosticos', 'graph-up-arrow', 'Pronósticos', 'Ventas y demanda',
     'Proyecciones de ventas, demanda y stock para planificar compras y producción con anticipación.'),
    ('alertas', 'bell', 'Alertas', 'Proactivas y a tiempo',
     'Avisos automáticos cuando un cliente deja de comprar, un producto se queda sin stock o un indicador se desvía.'),
    ('automatizacion', 'lightning-charge', 'Automatización', 'Tareas repetitivas',
     'Carga de pedidos recibidos por WhatsApp o email, informes periódicos y respuestas a consultas frecuentes.'),
]

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


def pipeline():
    area = HEIGHT - TOP
    mid_y = TOP + area / 2

    # Orígenes
    total = len(SOURCES) * SRC_H + (len(SOURCES) - 1) * SRC_GAP
    y0 = TOP + (area - total) / 2
    sources = [_node(s, SRC_X, y0 + i * (SRC_H + SRC_GAP), SRC_W, SRC_H, 'src', 'Origen de datos')
               for i, s in enumerate(SOURCES)]

    # Etapa de curado: tarjeta con los pasos adentro
    head = 64
    steps_h = len(STEPS) * STEP_H + (len(STEPS) - 1) * STEP_GAP
    cur_h = head + steps_h + 20
    cur_y = mid_y - cur_h / 2
    steps = [_node(s, CUR_X + 16, cur_y + head + i * (STEP_H + STEP_GAP), CUR_W - 32, STEP_H, 'step',
                   f'Paso {i + 1} de {len(STEPS)} · Curado')
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
                  'Inteligencia artificial')
    agent.update(cx=AGENT_CX, r=AGENT_R)
    curated_link = f'M{CUR_X + CUR_W} {mid_y:.1f} H{AGENT_CX - AGENT_R}'

    total = len(OUTPUTS) * OUT_H + (len(OUTPUTS) - 1) * OUT_GAP
    y0 = mid_y - total / 2
    outputs = [_node(o, OUT_X, y0 + i * (OUT_H + OUT_GAP), OUT_W, OUT_H, 'out', 'Resultado')
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

    columns = [
        (SRC_X + SRC_W / 2, '1', 'Orígenes de datos'),
        (CUR_X + CUR_W / 2, '2', 'Curado y ordenamiento'),
        (AGENT_CX, '3', 'Inteligencia artificial'),
        (OUT_X + OUT_W / 2, '4', 'Resultados'),
    ]

    return {
        'width': WIDTH, 'height': HEIGHT, 'mid_y': mid_y, 'columns': columns,
        'sources': sources, 'steps': steps, 'step_links': step_links, 'curation': curation,
        'agent': agent, 'curated_link': curated_link, 'curated_label_x': (CUR_X + CUR_W + AGENT_CX - AGENT_R) / 2,
        'outputs': outputs,
    }
