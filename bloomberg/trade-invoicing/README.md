# Trade Invoicing Service

Produces end-of-day invoices for customers' trades, lets compliance
cross-check them, and feeds the billing system.

## Layout

```
app/
  config.py                 fee rate, business timezone offset, page size
  models/                   Customer, Trade, Invoice dataclasses
  storage/                  in-memory repositories (one module per entity)
    customers_repo.py  trades_repo.py  invoices_repo.py  rates_repo.py
  services/
    pricing.py              notional and per-trade fee
    fx.py                   currency conversion with a rate cache
    invoicing.py            generate_invoice(customer_id, business_date)
    reconciliation.py       independent check of an invoice's fees
    export.py               JSON export for the billing system
    listing.py              paginated invoice listing for the customer portal
  util/                     clock, date helpers, id generator
tests/                      pytest; fixture resets all state per test
```

## Rules

1. **Business day:** a trade belongs to the business day in the exchange's
   timezone (UTC-5, see `config.BUSINESS_TZ_OFFSET_HOURS`). A trade executed
   at 23:00 local time on Tuesday belongs to Tuesday.
2. **Fees:** `notional * FEE_RATE` for each trade, in the trade's currency,
   rounded to cents using **round half up** (0.125 becomes 0.13).
3. **Currency:** each line is converted to the customer's base currency using
   the rate current at invoice time, rounded half up to cents after conversion.
4. **Totals:** invoice totals are the sum of the line values.
5. **Rates** can be updated at any time during the day through `rates_repo`.
6. **Listing:** pages start at 1, hold `PAGE_SIZE` invoices each, oldest first.
   Concatenating all pages must give every invoice exactly once.
7. **Reconciliation** recomputes the expected fees from raw trades and flags an
   invoice if the fees differ by more than the tolerance.
8. **Export:** invoices are serialised to JSON for the billing system, with
   money fields as JSON numbers.

## Notes from the team

- The billing system and reconciliation job both consume the output of this
  service, so their behaviour must keep working after any change here.
- Money amounts must be exact: finance audits every cent.
- Rates are refreshed several times a day.

## Running

```
pip install pytest
pytest -q tests
```
