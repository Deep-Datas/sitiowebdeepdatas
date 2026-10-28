---
title: "Data warehouse, data lake or spreadsheets: where to store your company's data"
seo_title: Data warehouse, data lake or spreadsheets
description: A jargon-free guide to the options for centralizing a midsize company's data, when each one makes sense and where to start.
date: 2026-09-29
tags: Data engineering
cta: diagnostico
es: donde-guardar-los-datos
---

When a company decides to put its data in order, one question is unavoidable: where do we keep it? And with it comes an alphabet soup: data warehouse, data lake, lakehouse, database, cloud. This guide explains the options without jargon, with midsize companies in mind.

## The starting point: the data is already somewhere

No company starts from scratch. The data already lives in:

- **Operational systems**: the ERP, the CRM, the invoicing system, the online store.
- **Spreadsheets**: targets, budgets, manual checks.
- **Files**: exports, distributor reports, bank statements.

These systems are built to operate — to invoice, record an order, add a customer — not to analyse. Querying them directly to build reports tends to be slow, can affect how they run, and forces you to cross-reference sources by hand every time.

That is why it pays to have a **central place for analysis**, separate from the operational systems.

## Option 1: stay with spreadsheets

This is where almost every company starts. It works while volumes are small, sources are few and one or two people handle the reports.

**When it stops being enough:** when building the reports takes days, when there are several versions of the same number, or when the files get slow. We go into it in [Excel or Power BI: when it is worth making the jump](/en/blog/excel-or-power-bi/).

## Option 2: data warehouse

A data warehouse is a database designed for analysis. Data from each system is loaded automatically, cleaned, unified and organized into a model built to answer business questions: sales by customer, product and period, for instance.

**Advantages:**

- A single source of truth for every report.
- Clean data with common criteria.
- Fast queries, even across years of history.
- Ideal for feeding dashboards like Power BI.

**When it makes sense:** it is the right option for most midsize companies whose data is mainly structured — sales, stock, customers, finance.

## Option 3: data lake

A data lake stores large volumes of data in its original format, with no need to structure it first: files, documents, images, system logs, messages.

**Advantages:**

- Accepts any kind of data.
- Cheap storage for large volumes.
- Useful for data science and machine learning models.

**When it makes sense:** when there is a lot of unstructured data or very large volumes. For many midsize companies it is more than they need to get started.

## Option 4: lakehouse

A combination of the two: the flexible storage of a data lake with the organization and performance of a data warehouse. Platforms like Microsoft Fabric and Databricks follow this approach.

**When it makes sense:** when you need to combine traditional analysis with unstructured data or AI projects, and you want a single platform for everything.

## So where should you start?

The approach matters more than the technology. What we recommend for a midsize company:

1. **Start from the business questions**, not the tool: what do you need to know that you do not know today?
2. **Pick the sources that answer those questions** and start there.
3. **Use the cloud** with managed services, which save you buying and maintaining servers and grow as usage grows.
4. **Design to grow**: start with a simple model that can take on more sources and use cases, artificial intelligence included.

The best architecture is not the most sophisticated one, but the one that solves today's problems without closing the door on tomorrow's.
