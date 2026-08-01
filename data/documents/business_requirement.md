# Reservation Conversion Business Requirement

## Business objective
The company runs product-model reservation campaigns before official launch. The platform must measure how many users reserve, place an order, and complete payment, and must identify users who reserved but did not successfully pay.

## Business journey
Campaign → Product Reservation → Order → Final Payment Status → CRM follow-up.

## Grain
The reservation conversion mart uses User × Campaign × Product × Site grain.

## Scope
Reservation is captured at product-model level. Colour, storage, and other SKU attributes are selected during ordering and are outside the MVP scope.
