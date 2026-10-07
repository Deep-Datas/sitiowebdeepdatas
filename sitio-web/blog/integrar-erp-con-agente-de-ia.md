---
title: Cómo se integra un ERP con un agente de IA: arquitectura, pipeline y frecuencia de actualización
description: Las capas técnicas para conectar SAP, Tango u Odoo con un agente de IA, cada cuánto actualizar los datos y cómo implementarlo en Azure, AWS o Google Cloud.
date: 2026-10-07
tags: Inteligencia artificial, Ingeniería de datos
cta: ia
---

"Queremos preguntarle al ERP en lenguaje natural." Es uno de los pedidos que más escuchamos. La idea es simple: que un gerente escriba *"¿cuánto facturó la zona norte ayer?"* y reciba la respuesta en segundos, con la fuente y la hora del dato.

Detrás de esa respuesta hay una arquitectura concreta. En esta nota explicamos cómo se arma, cada cuánto conviene actualizar los datos y por qué se puede implementar igual en Azure, AWS o Google Cloud.

## Dos formas de conectar el agente al ERP

Conectar el agente directo a la base del ERP para todo parece lo más rápido, pero casi nunca es lo mejor. Las tablas de un ERP tienen nombres crípticos, códigos internos y miles de relaciones que un modelo de lenguaje interpreta mal. Además, cada consulta suma carga sobre el sistema que usa toda la empresa.

Por eso combinamos dos caminos:

- **Capa analítica (indirecta).** Un pipeline copia los datos del ERP a un repositorio ordenado y el agente consulta ese modelo. Responde las preguntas de análisis: ventas, márgenes, rankings, tendencias, comparaciones contra el año anterior.
- **Herramientas en vivo (directas).** Funciones puntuales que consultan el ERP en el momento a través de su API o de una réplica de solo lectura. Responden lo que no puede esperar: stock disponible, estado de un pedido, saldo de un cliente.

La capa analítica resuelve la mayoría de las preguntas. Las herramientas en vivo cubren las pocas que necesitan el dato de este minuto.

## Las capas de la arquitectura

### 1. Extracción

Se traen del ERP **solo los registros que cambiaron**, por fecha de modificación, por captura de cambios (CDC) sobre el registro de la base o a través de la API del sistema. La extracción corre contra una réplica o en horarios de baja carga, para no afectar la operación.

Cada ERP tiene su vía habitual:

- **SAP**: vistas CDS y servicios OData, BAPI/RFC o SAP Datasphere como capa intermedia.
- **Tango**: suele funcionar sobre SQL Server, así que se lee desde una réplica o con vistas de solo lectura, además de sus APIs.
- **Odoo**: su API JSON-RPC o lectura de la base PostgreSQL desde una réplica.

### 2. Modelado

Los datos pasan por tres etapas:

1. **Bronce**: una copia fiel de lo que vino del ERP.
2. **Plata**: los datos limpios y sin duplicados, con unidades y monedas homogéneas.
3. **Oro**: tablas pensadas para el negocio, como ventas, stock, clientes y productos.

Es la etapa que más influye en la calidad de las respuestas. Si los datos llegan desordenados, el agente se equivoca con la misma seguridad con la que acierta.

### 3. Capa semántica

Acá se define **una sola vez** qué significa cada indicador: venta neta, margen, cliente activo, cobertura. El agente consulta indicadores con nombre propio, no tablas sueltas. Así, el número que responde es el mismo que muestra el tablero de Power BI y el que usa el área de finanzas.

### 4. Herramientas

El agente no escribe consultas libres contra cualquier tabla. Usa funciones con parámetros acotados, como *consultar indicadores*, *stock actual*, *estado de pedido* o *buscar en documentos*. Hoy lo habitual es exponerlas con **MCP (Model Context Protocol)**, un estándar abierto que permite usar las mismas herramientas con distintos modelos y en distintas nubes.

### 5. El agente

Es el modelo de lenguaje junto con la lógica que coordina la conversación. Interpreta la pregunta, elige qué herramienta usar, lee el resultado y responde **indicando la fuente y la hora de actualización**. Si además tiene que conocer manuales, políticas comerciales o condiciones de venta, se suma una búsqueda sobre esos documentos (lo que se conoce como RAG).

### 6. Canales

La respuesta llega por donde ya trabaja el equipo: Teams, Slack, WhatsApp, una web interna o un tablero.

## Seguridad: lo que no se negocia

- **Solo lectura.** El agente consulta con un usuario sin permisos de escritura. Si genera un pedido, queda como borrador hasta que lo aprueba una persona.
- **Cada uno ve lo suyo.** La identidad del usuario viaja con cada consulta y se aplican permisos por fila: un vendedor ve su cartera, un gerente ve su región.
- **Credenciales protegidas.** Las claves del ERP quedan en un almacén de secretos, nunca dentro de las instrucciones del modelo.
- **Auditoría.** Cada pregunta, cada consulta y cada respuesta quedan registradas.
- **Evaluación continua.** Se mantiene un conjunto de preguntas de prueba con sus respuestas correctas y se verifica antes de cada cambio.

## ¿Cada cuánto se actualizan los datos?

No todos los datos necesitan la misma frescura, y bajar la demora de un día a un minuto multiplica el costo y la complejidad. Por eso definimos la frecuencia **por tipo de dato**:

| Frecuencia | Datos típicos | Cómo se resuelve |
| --- | --- | --- |
| En el momento (segundos) | Stock disponible, estado de pedido, saldo de cuenta corriente | Herramienta en vivo contra la API o la réplica, con una caché de 1 a 5 minutos |
| Cada 5 a 15 minutos | Pedidos y facturación del día | Captura de cambios o extracción incremental frecuente |
| Cada hora | Ventas del día por zona y vendedor, cobranzas | Extracción incremental programada |
| Una vez por día (de madrugada) | Indicadores, historial, clientes, productos, listas de precios, pronósticos | Carga diaria después del cierre nocturno del ERP |
| Semanal, mensual o cuando cambia | Objetivos, presupuestos, documentos | Carga programada o disparada por el cambio |

Nuestra recomendación para empezar es una **carga diaria más dos o tres herramientas en vivo** para las preguntas críticas, normalmente stock y estado de pedidos. Con eso se cubre la gran mayoría de las consultas a bajo costo. Después se mide qué preguntas necesitan datos más frescos y solo esas pasan a una frecuencia horaria o casi en tiempo real.

Dos reglas que aplicamos siempre:

- El agente **muestra la hora de la última actualización** en cada respuesta, para que nadie confunda el dato de ayer con el de hoy.
- Si una carga falla, **el agente lo avisa** en lugar de responder con datos viejos como si fueran actuales.

## Azure, AWS o Google Cloud

La arquitectura es la misma en las tres nubes. Cambian los nombres de los servicios:

| Capa | Azure | AWS | Google Cloud |
| --- | --- | --- | --- |
| Extracción | Data Factory, Fabric | DMS, Glue | Datastream, Data Fusion |
| Almacenamiento | Data Lake Storage | S3 | Cloud Storage |
| Repositorio analítico | Fabric, Synapse, Azure SQL | Redshift, Athena | BigQuery |
| Modelo de lenguaje | Microsoft Foundry, Azure OpenAI | Amazon Bedrock | Vertex AI |
| Búsqueda en documentos | Azure AI Search | OpenSearch, Bedrock Knowledge Bases | Vertex AI Search |
| Ejecución del agente | Container Apps, Functions | ECS Fargate, Lambda | Cloud Run, Cloud Functions |
| Secretos | Key Vault | Secrets Manager | Secret Manager |

Para que la solución no quede atada a un proveedor, la lógica va en piezas portables:

- **dbt** para las transformaciones.
- **Airflow** o **Dagster** para la orquestación.
- El agente y sus herramientas MCP en **contenedores**.
- La infraestructura descrita con **Terraform**.

Elegir un modelo disponible en las tres nubes, como Claude (que está en Microsoft Foundry, Amazon Bedrock y Vertex AI), permite cambiar de nube sin reescribir el agente.

En la práctica, recomendamos implementar la solución **en la nube que la empresa ya usa**: ahí están sus permisos, su facturación y sus políticas de seguridad.

## En resumen

- El agente responde mejor sobre **datos modelados** que sobre las tablas crudas del ERP.
- Las **herramientas en vivo** se reservan para los pocos datos que necesitan estar al minuto.
- Una **capa semántica** garantiza que el agente, los tableros y finanzas usen los mismos números.
- La frecuencia se define **por tipo de dato**: arrancar con carga diaria y acelerar solo donde hace falta.
- La misma arquitectura funciona en **Azure, AWS o Google Cloud**.

Si tu empresa quiere consultar su ERP en lenguaje natural, el primer paso es elegir dos o tres preguntas que hoy cuestan tiempo responder y preparar los datos que esas preguntas necesitan.
