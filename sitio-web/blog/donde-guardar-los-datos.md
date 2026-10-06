---
title: "Data warehouse, data lake o planillas: dónde guardar los datos de tu empresa"
description: Una guía sin tecnicismos para entender las opciones para centralizar los datos de una empresa mediana, cuándo conviene cada una y por dónde empezar.
date: 2026-09-29
tags: Ingeniería de datos
cta: diagnostico
---

Cuando una empresa decide ordenar sus datos, aparece una pregunta inevitable: ¿dónde los guardamos? Y con ella, una sopa de términos: data warehouse, data lake, lakehouse, base de datos, nube. Esta guía explica las opciones sin tecnicismos, pensando en empresas medianas.

## El punto de partida: los datos ya están en algún lado

Ninguna empresa empieza de cero. Los datos ya viven en:

- **Sistemas operativos**: el ERP, el CRM, el sistema de facturación, el e-commerce.
- **Planillas**: objetivos, presupuestos, controles manuales.
- **Archivos**: exportaciones, reportes de distribuidores, extractos bancarios.

Estos sistemas están pensados para operar (facturar, registrar un pedido, cargar un cliente), no para analizar. Consultarlos directamente para armar reportes suele ser lento, puede afectar su funcionamiento y obliga a cruzar fuentes a mano cada vez.

Por eso conviene tener un **lugar central para el análisis**, separado de los sistemas operativos.

## Opción 1: seguir con planillas

Es el punto de partida de casi todas las empresas. Funciona mientras los volúmenes son chicos, las fuentes son pocas y una o dos personas manejan los reportes.

**Cuándo deja de alcanzar:** cuando armar los reportes lleva días, cuando hay varias versiones del mismo número o cuando los archivos se vuelven lentos. Lo contamos en detalle en [Excel o Power BI: cuándo conviene dar el salto](/blog/excel-o-power-bi/).

## Opción 2: data warehouse

Un data warehouse (almacén de datos) es una base de datos diseñada para el análisis. Los datos de cada sistema se cargan de forma automática, se limpian, se unifican y se organizan en un modelo pensado para responder preguntas de negocio: ventas por cliente, producto y período, por ejemplo.

**Ventajas:**

- Una única fuente de verdad para todos los reportes.
- Datos limpios y con criterios comunes.
- Consultas rápidas, incluso con años de historia.
- Ideal para alimentar tableros como Power BI.

**Cuándo conviene:** es la opción adecuada para la mayoría de las empresas medianas cuyos datos son principalmente estructurados (ventas, stock, clientes, finanzas).

## Opción 3: data lake

Un data lake (lago de datos) guarda grandes volúmenes de datos en su formato original, sin necesidad de estructurarlos antes: archivos, documentos, imágenes, registros de sistemas, mensajes.

**Ventajas:**

- Acepta cualquier tipo de dato.
- Almacenamiento económico para volúmenes grandes.
- Útil para ciencia de datos y modelos de machine learning.

**Cuándo conviene:** cuando hay mucho dato no estructurado o volúmenes muy grandes. Para muchas empresas medianas es más de lo que necesitan para empezar.

## Opción 4: lakehouse

Es una combinación de las dos anteriores: el almacenamiento flexible de un data lake con la organización y el rendimiento de un data warehouse. Plataformas como Microsoft Fabric o Databricks siguen este enfoque.

**Cuándo conviene:** cuando se necesita combinar análisis tradicional con datos no estructurados o con proyectos de inteligencia artificial, y se quiere una sola plataforma para todo.

## Entonces, ¿por dónde empezar?

Más importante que la tecnología es el enfoque. Nuestra recomendación para una empresa mediana:

1. **Empezar por las preguntas de negocio**, no por la herramienta: ¿qué necesitás saber que hoy no sabés?
2. **Elegir las fuentes que responden esas preguntas** y empezar por ellas.
3. **Usar la nube** con servicios administrados, que evitan comprar y mantener servidores y crecen a medida que crece el uso.
4. **Diseñar para crecer**: empezar con un modelo simple que admita sumar fuentes y casos de uso, incluida la inteligencia artificial.

La mejor arquitectura no es la más sofisticada, sino la que resuelve los problemas de hoy sin cerrarle la puerta a los de mañana.
