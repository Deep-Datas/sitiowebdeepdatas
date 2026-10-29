---
title: "How an ERP connects to an AI agent: architecture, pipeline and refresh frequency"
seo_title: How to connect an ERP to an AI agent
description: The technical layers for connecting SAP, Tango or Odoo to an AI agent, how often to refresh the data and how to build it on Azure, AWS or Google Cloud.
date: 2026-10-07
tags: Artificial intelligence, Data engineering
cta: ia
es: integrar-erp-con-agente-de-ia
---

"We want to ask the ERP questions in plain language." It is one of the requests we hear most. The idea is simple: a manager types *"how much did the north territory invoice yesterday?"* and gets the answer in seconds, with the source and the timestamp of the data.

Behind that answer there is a concrete architecture. This article explains how it is put together, how often the data should be refreshed and why it can be built the same way on Azure, AWS or Google Cloud.

## Two ways to connect the agent to the ERP

Pointing the agent straight at the ERP database for everything looks like the fastest route, and it is almost never the best one. ERP tables have cryptic names, internal codes and thousands of relationships that a language model reads badly. On top of that, every query adds load to the system the whole company runs on.

So we combine two paths:

- **Analytical layer (indirect).** A pipeline copies the ERP data into an organized repository and the agent queries that model. It answers the analysis questions: sales, margins, rankings, trends, year-on-year comparisons.
- **Live tools (direct).** Specific functions that query the ERP on the spot through its API or a read-only replica. They answer what cannot wait: available stock, the status of an order, a customer's balance.

The analytical layer handles most questions. The live tools cover the few that need this minute's number.

## The layers of the architecture

### 1. Extraction

Only the **records that changed** are pulled from the ERP, by modification date, by change data capture (CDC) on the database log, or through the system's API. Extraction runs against a replica or at low-load hours so it does not affect operations.

Each ERP has its usual route:

- **SAP**: CDS views and OData services, BAPI/RFC, or SAP Datasphere as an intermediate layer.
- **Tango**: it usually runs on SQL Server, so you read from a replica or with read-only views, as well as through its APIs.
- **Odoo**: its JSON-RPC API, or reading the PostgreSQL database from a replica.

### 2. Modelling

The data goes through three stages:

1. **Bronze**: a faithful copy of what came out of the ERP.
2. **Silver**: clean, deduplicated data with consistent units and currencies.
3. **Gold**: tables built for the business, such as sales, stock, customers and products.

This is the stage that most affects the quality of the answers. If the data arrives messy, the agent gets things wrong with the same confidence it gets them right.

### 3. Semantic layer

This is where you define, **once**, what each indicator means: net sales, margin, active customer, coverage. The agent queries named indicators, not loose tables. That way the number it answers with is the same one the Power BI dashboard shows and the one finance uses.

### 4. Tools

The agent does not write free-form queries against any table. It uses functions with bounded parameters, such as *query indicators*, *current stock*, *order status* or *search documents*. These days the usual way to expose them is **MCP (Model Context Protocol)**, an open standard that lets you use the same tools with different models and in different clouds.

### 5. The agent

This is the language model plus the logic that runs the conversation. It reads the question, picks which tool to use, reads the result and answers **citing the source and the refresh time**. If it also has to know manuals, commercial policies or terms of sale, a search over those documents is added (what is known as RAG).

### 6. Channels

The answer arrives wherever the team already works: Teams, Slack, WhatsApp, an internal site or a dashboard.

## Security: the non-negotiables

- **Read-only.** The agent queries with a user that has no write permissions. If it creates an order, it stays a draft until a person approves it.
- **Everyone sees their own.** The user's identity travels with every query and row-level permissions apply: a rep sees their own book, a manager sees their region.
- **Protected credentials.** ERP keys live in a secrets store, never inside the model's instructions.
- **Auditing.** Every question, every query and every answer is logged.
- **Continuous evaluation.** A set of test questions with their correct answers is kept and checked before every change.

## How often is the data refreshed?

Not all data needs the same freshness, and going from a day's delay to a minute's multiplies cost and complexity. So we set the frequency **per type of data**:

| Frequency | Typical data | How it is solved |
| --- | --- | --- |
| On the spot (seconds) | Available stock, order status, account balance | Live tool against the API or the replica, with a 1 to 5 minute cache |
| Every 5 to 15 minutes | The day's orders and invoicing | Change data capture or frequent incremental extraction |
| Hourly | The day's sales by territory and rep, collections | Scheduled incremental extraction |
| Once a day (overnight) | Indicators, history, customers, products, price lists, forecasts | Daily load after the ERP's nightly close |
| Weekly, monthly or on change | Targets, budgets, documents | Scheduled load or triggered by the change |

What we recommend to start is a **daily load plus two or three live tools** for the critical questions, usually stock and order status. That covers the vast majority of queries at low cost. Then you measure which questions need fresher data and only those move to hourly or near real time.

Two rules we always apply:

- The agent **shows the time of the last refresh** in every answer, so nobody mistakes yesterday's number for today's.
- If a load fails, **the agent says so** instead of answering with stale data as though it were current.

## Azure, AWS or Google Cloud

The architecture is the same in all three clouds. What changes is the names of the services:

| Layer | Azure | AWS | Google Cloud |
| --- | --- | --- | --- |
| Extraction | Data Factory, Fabric | DMS, Glue | Datastream, Data Fusion |
| Storage | Data Lake Storage | S3 | Cloud Storage |
| Analytical repository | Fabric, Synapse, Azure SQL | Redshift, Athena | BigQuery |
| Language model | Microsoft Foundry, Azure OpenAI | Amazon Bedrock | Vertex AI |
| Document search | Azure AI Search | OpenSearch, Bedrock Knowledge Bases | Vertex AI Search |
| Running the agent | Container Apps, Functions | ECS Fargate, Lambda | Cloud Run, Cloud Functions |
| Secrets | Key Vault | Secrets Manager | Secret Manager |

To keep the solution from being tied to one provider, the logic goes into portable pieces:

- **dbt** for the transformations.
- **Airflow** or **Dagster** for orchestration.
- The agent and its MCP tools in **containers**.
- The infrastructure described with **Terraform**.

Choosing a model available in all three clouds, such as Claude (which is on Microsoft Foundry, Amazon Bedrock and Vertex AI), lets you change cloud without rewriting the agent.

In practice, we recommend building the solution **in the cloud the company already uses**: that is where its permissions, its billing and its security policies already are.

## In short

- The agent answers better over **modelled data** than over the ERP's raw tables.
- **Live tools** are reserved for the few numbers that have to be up to the minute.
- A **semantic layer** guarantees the agent, the dashboards and finance use the same numbers.
- Frequency is set **per type of data**: start with a daily load and speed up only where it is needed.
- The same architecture works on **Azure, AWS or Google Cloud**.

If your company wants to query its ERP in plain language, the first step is to pick two or three questions that take time to answer today and prepare the data those questions need.
