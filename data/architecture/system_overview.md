# PayFlow Technologies – System Overview

PayFlow Technologies is a fictional online payment platform used solely for this
GraphRAG capstone. It contains services for payments, orders, customer profiles,
fraud checks, notifications, settlement, reporting, authentication, inventory and audit.

## Main request flow

1. Order Service creates an order and calls Inventory Service to reserve inventory.
2. Order Service calls Payment Service to authorize or capture payment.
3. Payment Service calls Customer Service for customer/payment preference information
   and Fraud Service for risk evaluation.
4. Payment and order events are published to Kafka topics.
5. Notification Service and Audit Service consume business events.
6. Settlement Service consumes payment events and stores settlement records.
7. Reporting Service consumes settlement events and reads settlement data.

## Data stores

- Customer Database: customer profile and related reference data.
- Fraud Database: risk rules and fraud decision metadata.
- Settlement Database: settlement batches, reporting and audit data.

## Teams

Payments, Customer Platform, Risk Engineering, Commerce and Data Platform.

## Synthetic-data warning

All names, records, timestamps, incidents and relationships are invented for education.
They do not describe a real company or production environment.
