---
title: What data quality is and how to measure it in your company
seo_title: What data quality is and how to measure it
description: Duplicate, incomplete or outdated data costs money. The six dimensions of data quality and how to start measuring them.
date: 2026-07-14
tags: Data quality
cta: diagnostico
es: calidad-de-datos
---

"The numbers don't add up." It is one of the phrases we hear most in a first meeting with a company. There is almost never an arithmetic error behind it: there is a **data quality** problem.

Data quality measures how reliable information is for the use you want to give it. There is no such thing as "perfect" data in the abstract: a customer list can be good enough to send a newsletter and, at the same time, not good enough to calculate profitability per customer.

## Why it matters

Data quality problems rarely show up as a line in the accounts, but they cost money every day:

- Hours spent fixing spreadsheets before every meeting.
- Orders delivered to old addresses.
- Customers who get the same offer twice because they are loaded twice.
- Decisions made late because nobody trusts the first number.

And with AI in the picture the problem multiplies: a model trained or queried on poor data gives poor answers, very confidently.

## The six dimensions of data quality

To measure quality it helps to break it into dimensions. These are the ones most used:

### 1. Completeness

Is every piece of data that should be there actually there? For example, what percentage of customers has a tax ID, an address or an assigned sales rep.

### 2. Uniqueness

Does each customer, product or supplier exist only once? Duplicates are the most frequent problem when systems are cross-referenced or when several people enter data.

### 3. Validity

Does the data follow the expected format and rules? An email with no @, an impossible date or a product code that does not exist are invalid data.

### 4. Consistency

Does the same piece of data match across systems? If a customer is active in the CRM and inactive in the ERP, at least one of the two is wrong.

### 5. Accuracy

Does the data reflect reality? This is the hardest dimension to measure, because it means comparing against a reliable source: for example, the stock in the system against a physical count.

### 6. Timeliness

Is the data up to date? A price from three months ago can be valid and complete and still be useless for a quote.

## How to start measuring it

You do not need a huge project or expensive tools. A good starting point:

1. **Pick one critical entity** — customers or products, say — and one or two sources where it lives.
2. **Write concrete rules** for each dimension: "every active customer must have an assigned rep", "no two customers can share a tax ID".
3. **Measure the percentage of records that meet each rule.** That percentage is your quality indicator.
4. **Automate the measurement** so it repeats with every data refresh and warns you when an indicator gets worse.
5. **Fix it at the source.** Cleaning the data in the report treats the symptom; fixing the data entry process treats the cause.

## An indicator that gets watched gets better

The most valuable thing about measuring data quality is that it makes it visible. When the sales team sees that 30% of their customers have no assigned territory, the problem stops being abstract and starts getting fixed.

That is why we recommend adding a small data quality dashboard to any integration project: a handful of rules, measured every day, each one with an owner.
