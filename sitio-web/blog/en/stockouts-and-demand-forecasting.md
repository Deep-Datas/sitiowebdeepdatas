---
title: How to reduce stockouts with a demand forecast
seo_title: Reducing stockouts with a demand forecast
description: Running out of stock costs sales; holding too much ties up capital. How to measure it and how a demand forecast helps you plan purchasing.
date: 2026-09-22
tags: Analytics, Predictive models
cta: casos
es: quiebre-de-stock-y-pronostico
---

Few things frustrate a sales team more than having the customer, having the order and not having the product. A stockout does not just lose that sale: often the customer buys another brand and does not come back.

The opposite costs too: products piling up in the warehouse, capital tied up and, with perishables, stock that expires.

Both problems usually have the same root: **purchasing is planned by looking at the past, not at what is going to happen**.

## How to measure stockouts

Before reducing it you have to measure it. Two simple indicators:

**Stockout rate:** the percentage of products out of stock at a given moment, or the percentage of days each product spent out of stock.

**Fill rate:** units delivered ÷ units ordered. It measures how much of what customers asked for you were able to deliver.

It pays to track them by product, category and warehouse, and to prioritize the products that sell most: a stockout on the star product costs far more than one on a slow mover.

## Why averages are not enough

The most common way to plan purchasing is to look at the average of the last few months and replenish from that. It works for products with steady sales, and it fails exactly when it matters most:

- **Seasonality:** summer sales look nothing like winter sales.
- **Promotions:** a promotion can double a product's sales for two weeks.
- **Trends:** a product that grows every month will always be short if you plan on the average.
- **Events:** holidays, special dates, price changes.

## What a demand forecast does

A demand forecasting model learns from sales history, but it does not just average it. It accounts for seasonality, trend, the effect of promotions and other factors, and projects how much of each product will sell over the coming weeks.

With that forecast, current stock and each supplier's lead time, you can calculate:

- **Days of cover:** how many days current stock lasts at the expected demand.
- **Stockout risk:** which products will run out before the next delivery arrives.
- **Suggested purchase:** how much to order of each product to cover demand without over-stocking.

## How to tell whether the forecast is any good

A forecast is never perfect, but it has to beat the alternative. A common measure is the **mean absolute percentage error (MAPE)**: the average gap between what was forecast and what was sold, as a percentage. What matters is comparing that error against the current method's — the average of the last three months, say.

## How to start

1. **Check the quality of the history.** Sales lost to stockouts do not show up in sales: if a product was out of stock for two weeks, its history understates real demand. Those periods have to be identified.
2. **Start with the most important categories**, not the whole catalogue.
3. **Build the forecast into the purchasing routine**, with a weekly replenishment dashboard the team actually uses to decide.
4. **Measure the results** with the same stockout and fill rate indicators, before and after.

In one of our projects with a distributor, demand forecasting cut **stockouts by 12%**. You can see what a dashboard like that looks like in our [demand forecasting example](/en/dashboard-examples/#pronostico), with sample data.
