# Django-API
API with a collection of experiments/features with Django and DRF

## Design
This API mimics a store

Features:
- store has:
    - [x] products that are owned by users
    - [x] products can be associated with tags
- users can (via the API):
    - [x] register
    - [x] authenticate and get a access token for the API
    - [x] change applicable own user details
        - password
    - [x] view their own profile
    - [x] view public information about other users
    - [x] manage their own products, but not of other users
        - edit product core information
            - name
            - description
            - stock
        - [x] dissociate/associate tags
    - [x] see other users store (any user products)
    - [x] - search for products (via title, description and tags) - newest first
    - [x] can buy products/place an order (from any user)
    - [ ] orders follow state: `PENDING_CONFIRMATION` (requires the client to confirm the order within a set time frame (e.g. 1-5 min) with payment details. Otherwise it is reverted to `NOT_CONFIRMED` state) -> `CONFIRMED`(the order is confirmed and (pseudo)payment should be processed) -> `ACCEPTED`
    - [ ] put products into a bag
    - [ ] create order from a bag
    - [x] search for existing tags (this would be for auto-complete/suggestion of tags in a frontend)
- staff can:
    - [x] manage tags (name, description)


Technical features:
- [x] backing postgres DB
- [x] all entities should have UUID for ids
- [ ] expired user API tokens should be removed (check if this automated with `django-oauth-toolkit`)
- [x] static analysis of code - isort, black, ...
- [x] for adequate DB entities -  have `created`, `updated`, `deleted` timestamps. all dates/timestamps should be in UTC timezone
- [x] authentication should be based on "blackbox" tokens and acquired via oauth2 password flow
- [WIP] source events from the DB to simplify complexity (psql -> debezium server -> redis -> ?celery? worker/tasks) - https://debezium.io/documentation/reference/3.0/architecture.html#_debezium_server
- [ ] APIs documented and have "contract" testing
- [ ] separate test runs for unit and integration/api tests. The latter are slower and should be run separately
- [x] DB entities should not be hard deleted from the DB, instead the `deleted` timestamps should be set
- [ ] products, bags and orders are implemented as state machines with appropriate states
    - https://pypi.org/project/python-statemachine/ seems like a good candidate to explore for this (it has django integration) and diagrams can be generated


Optional features:
- run the app in a docker-compose env
- run type analysis - https://www.mypy-lang.org/. Would likely be better to upgrade to python 3.11 beforehand because it supports better typing
- transition code to async where applicable
- place product information (name, description, stock and tags) in an elasticsearch index and use it to list & search
- social features such as "follow user"


## Running

### Environment
start necessary dependencies (including for tests) with:

`docker-compose up -d --remove-orphans`

### Tests
Run tests with:

`pytest [-vv]`
