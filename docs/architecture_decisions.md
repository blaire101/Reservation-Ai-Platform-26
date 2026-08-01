# Architecture Decisions

## ADR-001 — One agent, three tools
The MVP uses one LangGraph workflow with Knowledge, Analytics, and Quality routes. A supervisor multi-agent design would add coordination overhead without improving this small domain.

## ADR-002 — Final payment status in order
The MVP stores the final payment outcome in `fact_order`. This keeps the model small. A one-to-many payment-attempt table is the correct extension when retry analysis is required.

## ADR-003 — Product model rather than SKU
Reservation is made for a product model. Colour and storage are selected during ordering and are outside scope.

## ADR-004 — Governed query plan
The analytics tool only supports approved metrics and dimensions. It does not execute arbitrary LLM-generated SQL.

## ADR-005 — Cloud-portable implementation
Local mode is reproducible without a cloud account. AWS is documented as a reference deployment rather than being hard-coded into business logic.
