# Service Dependency Reference

- Order Service depends on Payment Service and Inventory Service.
- Payment Service depends on Customer Service and Fraud Service.
- Authentication Service depends on Customer Service.
- Settlement Service depends on Payment Service.
- Reporting Service depends on Settlement Service.
- Customer Service uses Customer Database.
- Inventory Service uses Customer Database in this simplified sample.
- Fraud Service uses Fraud Database.
- Settlement Service, Reporting Service and Audit Service use Settlement Database.
- Fraud Service consumes customer-events.
- Notification Service consumes payment-events and order-events.
- Settlement Service consumes payment-events.
- Reporting Service consumes settlement-events.
- Inventory Service consumes order-events.
- Audit Service consumes payment-events, order-events and settlement-events.

The graph loader should treat these as authoritative catalogue relationships.
Incident documents add operational observations; they should not silently overwrite
the service catalogue.
