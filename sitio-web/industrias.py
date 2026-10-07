"""Páginas por industria (src/pages/industria.html), en español e inglés.

Cada industria tiene su ruta en i18n.ROUTES ('ind-<id>') y estos textos:
desafíos, qué construimos (con enlaces a los tableros de ejemplo), los
indicadores que medimos, los casos y logos relacionados y preguntas
frecuentes. Los casos se toman de casos.py: solo se muestran los publicados.
No sumes resultados que no estén en un caso real.
"""

# Textos de la estructura de la página
LABELS = {
    'es': {
        'eyebrow': 'Industrias',
        'challenges': 'Los desafíos que vemos', 'challenges_title': 'Lo que frena a las empresas del sector',
        'build': 'Qué construimos', 'build_title': 'Soluciones pensadas para tu negocio',
        'see_example': 'Ver el tablero de ejemplo', 'see_ai': 'Ver soluciones de IA',
        'kpis': 'Indicadores', 'kpis_title': 'Lo que medimos',
        'kpis_text': 'Definimos con tu equipo los indicadores clave y los calculamos todos los días con las mismas reglas.',
        'cases': 'Casos', 'cases_title': 'Resultados en el sector', 'see_case': 'Leer el caso',
        'cases_text': 'Proyectos reales, contados con los números que importan a cada cliente.',
        'example_caption': 'Tablero ilustrativo con datos ficticios.',
        'faq': 'Preguntas frecuentes', 'faq_title': 'Lo que nos suelen preguntar',
        'faq_more': '¿Tenés otra duda?', 'faq_write': 'Escribinos', 'faq_tail': 'y lo conversamos.',
        'whatsapp': 'o escribinos por WhatsApp',
        'cta_call': 'Coordinar una llamada',
        'trust': 'Trabajamos con',
        'other': 'Otras industrias',
        'posts': 'Blog', 'posts_title': 'Para seguir leyendo', 'minutes': 'min de lectura',
    },
    'en': {
        'eyebrow': 'Industries',
        'challenges': 'The challenges we see', 'challenges_title': 'What holds companies in this sector back',
        'build': 'What we build', 'build_title': 'Solutions designed for your business',
        'see_example': 'See the sample dashboard', 'see_ai': 'See AI solutions',
        'kpis': 'KPIs', 'kpis_title': 'What we measure',
        'kpis_text': 'We define the key KPIs with your team and calculate them every day with the same rules.',
        'cases': 'Case studies', 'cases_title': 'Results in the sector', 'see_case': 'Read the case study',
        'cases_text': 'Real projects, told with the numbers that matter to each client.',
        'example_caption': 'Illustrative dashboard with sample data.',
        'faq': 'FAQ', 'faq_title': 'What we’re often asked',
        'faq_more': 'Have another question?', 'faq_write': 'Write to us', 'faq_tail': 'and let’s talk it through.',
        'whatsapp': 'or message us on WhatsApp',
        'cta_call': 'Book a call',
        'trust': 'We work with',
        'other': 'Other industries',
        'posts': 'Blog', 'posts_title': 'Further reading', 'minutes': 'min read',
    },
}

# Datos comunes a los dos idiomas
# (casos de casos.py, tablero de ejemplo de dashboards.py, logos de src/logos.html y
# notas del blog, que se muestran solo en español)
COMMON = {
    'consumo': {'icon': 'cart3', 'cases': ['distribuidores', 'cobertura'], 'example': 'cobertura',
                'logos': ['kelloggs', 'mccain', 'cafe-m'],
                'posts': ['unificar-ventas-de-distribuidores', 'cobertura-y-venta-cruzada', 'kpis-comerciales']},
    'distribucion': {'icon': 'truck', 'cases': ['pronostico'], 'example': 'pronostico',
                     'logos': ['romemi'],
                     'posts': ['quiebre-de-stock-y-pronostico', 'pedidos-por-whatsapp', 'integrar-erp-con-agente-de-ia']},
    'salud': {'icon': 'heart-pulse', 'cases': [], 'example': None,
              'logos': ['lilly'],
              'posts': ['kpis-comerciales', 'calidad-de-datos', 'donde-guardar-los-datos']},
}

TEXT = {
    'es': {
        'consumo': {
            'name': 'Consumo masivo',
            'title': 'Datos e IA para empresas de consumo masivo | DeepDatas',
            'description': 'Unificamos las ventas de tus distribuidores, medimos la cobertura de cada línea por punto de venta y anticipamos la demanda, con tableros y agentes de IA para el equipo comercial.',
            'h1': 'Datos e IA para consumo masivo: más ventas en cada', 'h1_em': 'punto de venta.',
            'lead': 'Unificamos las ventas de tus distribuidores, medimos la cobertura de cada línea y te mostramos dónde crecer, con tableros y agentes de IA que tu equipo comercial usa todos los días.',
            'card': 'Ventas de toda la red de distribuidores, cobertura por punto de venta y pronóstico de demanda.',
            'challenges': [
                ('Cada distribuidor informa a su manera', 'Las ventas llegan en planillas con formatos, códigos y criterios propios. Consolidarlas lleva días y el número final se discute.'),
                ('No sabés qué falta en cada punto de venta', 'Sabés cuánto vendés, pero no qué línea no compra cada cliente ni qué vendedor tiene más oportunidades de venta cruzada.'),
                ('Promociones difíciles de evaluar', 'Sin datos unificados es difícil saber qué promoción movió el volumen y cuánto margen costó.'),
                ('Quiebres en los picos y sobrestock después', 'La demanda estacional y las promociones complican la planificación de producción y reposición.'),
            ],
            'build': [
                ('bar-chart-line', 'Performance de la red de distribuidores', 'Ventas, volumen y cumplimiento del objetivo de cada distribuidor, con un tablero que se actualiza solo.', ('ejemplos', '#distribuidores')),
                ('people', 'Cobertura y venta cruzada por vendedor', 'Qué líneas compra cada punto de venta y listas de oportunidades para cada vendedor.', ('ejemplos', '#cobertura')),
                ('graph-up-arrow', 'Pronóstico de demanda', 'Modelos que anticipan la demanda por producto y zona para planificar producción y reposición.', ('ejemplos', '#pronostico')),
                ('robot', 'Agente de IA para el equipo comercial', 'Consultas en lenguaje natural sobre ventas, clientes y stock, desde el celular.', ('ia', '')),
            ],
            'kpis': ['Sell-in y sell-out por distribuidor', 'Cobertura numérica y ponderada', 'Venta cruzada por línea de producto',
                     'Cumplimiento de objetivos por zona y vendedor', 'Tamaño promedio de pedido', 'Frecuencia de compra y clientes perdidos',
                     'Quiebres de stock', 'Resultado de cada promoción', 'Margen por canal'],
            'faqs': [
                ('¿Los distribuidores tienen que cambiar cómo nos informan?', 'No. Automatizamos la recepción de los archivos tal como llegan hoy y unificamos formatos y códigos en el proceso.'),
                ('¿Podemos sumar datos de otras fuentes, como el CRM o las planillas de objetivos?', 'Sí. Integramos el ERP, el CRM, las planillas y los archivos de los distribuidores en un único modelo.'),
                ('¿Por dónde empezamos?', 'Por un diagnóstico de datos: en dos semanas sabés qué fuentes tenés y qué tablero o caso de IA conviene hacer primero.'),
            ],
            'cta_title': '¿Trabajás en consumo masivo? Empecemos por <em>tus datos.</em>',
        },
        'distribucion': {
            'name': 'Distribución y retail',
            'title': 'Datos e IA para distribuidoras y retail | DeepDatas',
            'description': 'Pronóstico de demanda, reposición, rentabilidad por cliente y producto, y carga automática de pedidos con IA para distribuidoras mayoristas y retail.',
            'h1': 'Datos e IA para distribuidoras y retail: el stock justo,', 'h1_em': 'en el momento justo.',
            'lead': 'Integramos ventas, compras y stock en un solo modelo, anticipamos la demanda y automatizamos tareas como la carga de pedidos, para que compres mejor y no pierdas ventas.',
            'card': 'Pronóstico de demanda, reposición, rentabilidad por cliente y pedidos automáticos.',
            'challenges': [
                ('Quiebres y sobrestock al mismo tiempo', 'Las compras se planifican con promedios: algunos productos faltan en los picos y otros se acumulan en el depósito.'),
                ('Pedidos que se cargan a mano', 'Los pedidos llegan por WhatsApp y email en texto libre y alguien los copia al sistema, con demoras y errores.'),
                ('Miles de productos y clientes, poca visibilidad', 'Es difícil saber qué clientes, productos o canales dejan margen y cuáles no.'),
                ('Información repartida', 'Ventas en el ERP, e-commerce aparte y controles en planillas: cada área mira un número distinto.'),
            ],
            'build': [
                ('graph-up-arrow', 'Pronóstico y reposición', 'Un modelo que anticipa la demanda semanal y sugiere qué reponer antes de que falte.', ('ejemplos', '#pronostico')),
                ('inboxes', 'Carga automática de pedidos con IA', 'Un agente lee los pedidos de WhatsApp o email, los carga en tu sistema y avisa si falta algún dato.', ('ia', '')),
                ('bar-chart-line', 'Rentabilidad por cliente, producto y canal', 'Tableros de margen y mezcla de venta para decidir precios, descuentos y surtido.', None),
                ('bell', 'Alertas de clientes y stock', 'Avisos cuando un cliente deja de comprar o un producto está por quedarse sin stock.', ('ia', '')),
            ],
            'kpis': ['Nivel de servicio (fill rate)', 'Quiebres de stock', 'Días de inventario y rotación', 'Sobrestock y productos sin movimiento',
                     'Precisión del pronóstico', 'Margen por cliente, producto y canal', 'Ticket promedio y frecuencia de compra',
                     'Clientes inactivos', 'Tiempos de entrega'],
            'faqs': [
                ('¿Necesitamos mucho historial para el pronóstico?', 'Cuanto más historial, mejor, pero lo evaluamos en el diagnóstico: revisamos qué datos hay y qué precisión es razonable esperar antes de construir el modelo.'),
                ('¿El agente puede cargar pedidos en nuestro sistema?', 'Sí, si el sistema lo permite (por API o integración). Siempre empezamos con un piloto acotado y con controles para revisar lo que carga.'),
                ('¿Por dónde empezamos?', 'Por un diagnóstico de datos: en dos semanas sabés qué fuentes tenés y qué solución conviene hacer primero.'),
            ],
            'cta_title': '¿Tenés una distribuidora o un retail? Empecemos por <em>tus datos.</em>',
        },
        'salud': {
            'name': 'Laboratorios y salud',
            'title': 'Datos e IA para laboratorios y distribución farmacéutica | DeepDatas',
            'description': 'Tableros comerciales, priorización de la fuerza de ventas y seguimiento del stock en la cadena para laboratorios y distribución farmacéutica, con datos protegidos y permisos por rol.',
            'h1': 'Datos e IA para laboratorios: decisiones comerciales', 'h1_em': 'con datos confiables.',
            'lead': 'Integramos ventas, fuerza de ventas y stock en la cadena para que tu equipo comercial sepa dónde enfocar cada visita, con datos protegidos y permisos por rol.',
            'card': 'Tableros comerciales, foco para la fuerza de ventas y stock en la cadena, con datos protegidos.',
            'challenges': [
                ('Ventas que pasan por muchos intermediarios', 'Droguerías, distribuidoras y farmacias informan en formatos distintos y la visión de la demanda final llega tarde.'),
                ('Visitas sin una prioridad clara', 'Los representantes tienen agendas largas y pocos datos para decidir a quién visitar primero.'),
                ('Stock y vencimientos en la cadena', 'Sin seguimiento del stock en los canales, aparecen faltantes en un lugar y productos por vencer en otro.'),
                ('Datos que requieren cuidado', 'La información comercial y de clientes necesita permisos estrictos y trazabilidad de quién ve qué.'),
            ],
            'build': [
                ('bar-chart-line', 'Tablero comercial por zona, canal y producto', 'Ventas, objetivos y tendencias en un solo lugar, para la dirección y para cada gerente regional.', None),
                ('people', 'Foco para la fuerza de ventas', 'Listas priorizadas para cada representante, según potencial, frecuencia de visita y oportunidades.', None),
                ('truck', 'Stock y vencimientos en la cadena', 'Seguimiento del stock en distribuidores y alertas de faltantes y productos próximos a vencer.', None),
                ('robot', 'Agente de IA con permisos por rol', 'Consultas en lenguaje natural sobre los indicadores, donde cada persona ve solo lo que le corresponde.', ('ia', '')),
            ],
            'kpis': ['Ventas por canal, droguería y zona', 'Participación de mercado, cuando hay datos de auditoría', 'Cobertura de farmacias',
                     'Frecuencia y efectividad de las visitas', 'Cumplimiento de objetivos por representante', 'Stock en la cadena y días de cobertura',
                     'Productos próximos a vencer'],
            'faqs': [
                ('¿Cómo protegen información sensible?', 'Trabajamos con accesos de solo lectura y permisos por rol, firmamos acuerdos de confidencialidad y, siempre que es posible, implementamos la solución en la nube de tu empresa.'),
                ('¿Pueden integrar datos de auditoría de mercado?', 'Sí. Integramos los archivos de auditoría que recibe tu empresa con las ventas internas y los datos de la fuerza de ventas.'),
                ('¿Por dónde empezamos?', 'Por un diagnóstico de datos: en dos semanas sabés qué fuentes tenés y qué tablero o caso de IA conviene hacer primero.'),
            ],
            'cta_title': '¿Trabajás en un laboratorio? Empecemos por <em>tus datos.</em>',
        },
    },
    'en': {
        'consumo': {
            'name': 'Consumer goods',
            'title': 'Data and AI for consumer goods companies | DeepDatas',
            'description': 'We bring your distributors’ sales together, measure each product line’s coverage by point of sale and anticipate demand, with dashboards and AI agents for your sales team.',
            'h1': 'Data and AI for consumer goods: more sales at every', 'h1_em': 'point of sale.',
            'lead': 'We bring your distributors’ sales together, measure the coverage of each product line and show you where to grow, with dashboards and AI agents your sales team uses every day.',
            'card': 'Sales across your distributor network, point-of-sale coverage and demand forecasting.',
            'challenges': [
                ('Every distributor reports its own way', 'Sales arrive in spreadsheets with their own formats, codes and criteria. Consolidating them takes days and the final number is up for debate.'),
                ('You don’t know what each point of sale is missing', 'You know how much you sell, but not which line each customer doesn’t buy or which sales rep has the most cross-selling opportunities.'),
                ('Promotions that are hard to evaluate', 'Without unified data, it’s hard to tell which promotion moved volume and how much margin it cost.'),
                ('Stockouts at peak times, overstock afterwards', 'Seasonal demand and promotions make production and replenishment planning difficult.'),
            ],
            'build': [
                ('bar-chart-line', 'Distributor network performance', 'Sales, volume and target attainment for every distributor, in a dashboard that updates itself.', ('ejemplos', '#distribuidores')),
                ('people', 'Coverage and cross-selling by sales rep', 'Which lines each point of sale buys, and opportunity lists for every sales rep.', ('ejemplos', '#cobertura')),
                ('graph-up-arrow', 'Demand forecasting', 'Models that anticipate demand by product and region to plan production and replenishment.', ('ejemplos', '#pronostico')),
                ('robot', 'An AI agent for your sales team', 'Plain-language questions about sales, customers and inventory, right from their phone.', ('ia', '')),
            ],
            'kpis': ['Sell-in and sell-out by distributor', 'Numeric and weighted distribution', 'Cross-selling by product line',
                     'Target attainment by region and sales rep', 'Average order size', 'Purchase frequency and lost customers',
                     'Stockouts', 'Results of each promotion', 'Margin by channel'],
            'faqs': [
                ('Do our distributors have to change how they report?', 'No. We automate receiving their files exactly as they arrive today and unify formats and codes along the way.'),
                ('Can we add other sources, like the CRM or target spreadsheets?', 'Yes. We integrate the ERP, the CRM, spreadsheets and distributor files into a single model.'),
                ('Where do we start?', 'With a data assessment: in two weeks you’ll know which sources you have and which dashboard or AI use case to build first.'),
            ],
            'cta_title': 'In consumer goods? Let’s start with <em>your data.</em>',
        },
        'distribucion': {
            'name': 'Distribution and retail',
            'title': 'Data and AI for distributors and retail | DeepDatas',
            'description': 'Demand forecasting, replenishment, profitability by customer and product, and AI-powered order entry for wholesale distributors and retailers.',
            'h1': 'Data and AI for distributors and retail: the right stock,', 'h1_em': 'at the right time.',
            'lead': 'We bring sales, purchasing and inventory into a single model, anticipate demand and automate tasks like order entry, so you buy smarter and stop losing sales.',
            'card': 'Demand forecasting, replenishment, customer profitability and automated order entry.',
            'challenges': [
                ('Stockouts and overstock at the same time', 'Purchasing is planned with averages: some products run out at peak times while others pile up in the warehouse.'),
                ('Orders entered by hand', 'Orders arrive by WhatsApp and email in free text and someone copies them into the system, with delays and errors.'),
                ('Thousands of products and customers, little visibility', 'It’s hard to know which customers, products or channels make money and which don’t.'),
                ('Scattered information', 'Sales in the ERP, e-commerce on its own and checks in spreadsheets: every department looks at a different number.'),
            ],
            'build': [
                ('graph-up-arrow', 'Forecasting and replenishment', 'A model that anticipates weekly demand and suggests what to restock before it runs out.', ('ejemplos', '#pronostico')),
                ('inboxes', 'AI-powered order entry', 'An agent reads WhatsApp or email orders, enters them into your system and flags anything that is missing.', ('ia', '')),
                ('bar-chart-line', 'Profitability by customer, product and channel', 'Margin and sales-mix dashboards to decide on prices, discounts and assortment.', None),
                ('bell', 'Customer and inventory alerts', 'Notifications when a customer stops buying or a product is about to run out of stock.', ('ia', '')),
            ],
            'kpis': ['Fill rate', 'Stockouts', 'Days of inventory and turnover', 'Overstock and slow-moving products',
                     'Forecast accuracy', 'Margin by customer, product and channel', 'Average ticket and purchase frequency',
                     'Inactive customers', 'Delivery times'],
            'faqs': [
                ('Do we need a lot of history for the forecast?', 'The more history, the better, but we evaluate it in the assessment: we review what data exists and what accuracy is reasonable to expect before building the model.'),
                ('Can the agent enter orders into our system?', 'Yes, if the system allows it (through an API or integration). We always start with a focused pilot and with checks to review what it enters.'),
                ('Where do we start?', 'With a data assessment: in two weeks you’ll know which sources you have and which solution to build first.'),
            ],
            'cta_title': 'Run a distribution or retail business? Let’s start with <em>your data.</em>',
        },
        'salud': {
            'name': 'Pharma and healthcare',
            'title': 'Data and AI for pharmaceutical companies and distribution | DeepDatas',
            'description': 'Sales dashboards, sales force prioritization and supply chain inventory tracking for pharmaceutical companies and distributors, with protected data and role-based permissions.',
            'h1': 'Data and AI for pharma: commercial decisions', 'h1_em': 'backed by reliable data.',
            'lead': 'We integrate sales, sales force and supply chain inventory data so your commercial team knows where to focus every visit, with protected data and role-based permissions.',
            'card': 'Sales dashboards, sales force focus and supply chain inventory, with protected data.',
            'challenges': [
                ('Sales that go through many intermediaries', 'Wholesalers, distributors and pharmacies report in different formats, and visibility into end demand arrives late.'),
                ('Visits without clear priorities', 'Sales reps have long call lists and little data to decide whom to visit first.'),
                ('Inventory and expiry dates across the chain', 'Without tracking inventory in the channel, you get shortages in one place and products about to expire in another.'),
                ('Data that needs care', 'Commercial and customer information requires strict permissions and a clear record of who sees what.'),
            ],
            'build': [
                ('bar-chart-line', 'Sales dashboard by region, channel and product', 'Sales, targets and trends in one place, for leadership and for every regional manager.', None),
                ('people', 'Focus for your sales force', 'Prioritized lists for every sales rep, based on potential, visit frequency and opportunities.', None),
                ('truck', 'Inventory and expiry dates across the chain', 'Tracking of inventory at distributors and alerts for shortages and products nearing expiry.', None),
                ('robot', 'An AI agent with role-based permissions', 'Plain-language questions about your KPIs, where everyone sees only what they should.', ('ia', '')),
            ],
            'kpis': ['Sales by channel, wholesaler and region', 'Market share, when audit data is available', 'Pharmacy coverage',
                     'Visit frequency and effectiveness', 'Target attainment by sales rep', 'Channel inventory and days of coverage',
                     'Products nearing expiry'],
            'faqs': [
                ('How do you protect sensitive information?', 'We work with read-only access and role-based permissions, sign confidentiality agreements and, whenever possible, deploy the solution in your company’s cloud.'),
                ('Can you integrate market audit data?', 'Yes. We integrate the audit files your company receives with internal sales and sales force data.'),
                ('Where do we start?', 'With a data assessment: in two weeks you’ll know which sources you have and which dashboard or AI use case to build first.'),
            ],
            'cta_title': 'In pharma? Let’s start with <em>your data.</em>',
        },
    },
}

ORDER = ['consumo', 'distribucion', 'salud']


def industries(lang):
    """Industrias en el orden del sitio, con los textos del idioma pedido."""
    return [{'id': key, **COMMON[key], **TEXT[lang][key]} for key in ORDER]
