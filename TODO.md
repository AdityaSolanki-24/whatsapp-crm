# TODO

## Bulk delete customers feature
- [ ] Add `CustomerService.delete_many(customer_ids)` in `services/customer_service.py`
- [ ] Add route `POST /customers/delete_selected` in `routes/customers.py`
- [ ] Update `templates/customers/customers.html` with checkbox selection UI + bulk delete form/button
- [x] Add/extend tests in `tests/test_customers.py` for bulk deletion

- [x] Run `pytest tests/test_customers.py -v` and ensure all tests pass


