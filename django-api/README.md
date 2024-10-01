# Django-API
API with a collection of experiments/features with Django and DRF

## Design
This API mimics a store

Features:
- store has:
    - products that are owned by users
    - products can be associated with tags
- users can (via the API):
    - [x] register
    - [x] authenticate and get a access token for the API
    - [x] change applicable own user details
        - password
    - [WIP] view their own profile
    - [WIP] view public information about other users
    - manage their own products, but not of other users
        - edit product core information
            - name
            - description
            - stock
        - dissociate/associate tags
    - can buy products (from any user)
        - list all products (ordered by newest creation date)
        - search for products
        - put products into a bag
        - create order from a bag
    - add new tags
    - search for existing tags (this would be for auto-complete/suggestion of tags in a frontend)

Technical features:
- [x] backing postgres DB
- all entities should have UUID for ids
- expired user API tokens should be removed
- [x] static analysis of code - isort, black, ...
- all dates/timestamps should be in UTC timezone
- all DB entities should have `created`, `updated`, `deleted` timestamps
- DB entities should not be hard deleted from the DB, instead the `deleted` timestamps should be set
- products, bags and orders should be implemented as state machines with appropriate states
    - https://pypi.org/project/python-statemachine/ seems like a good candidate to explore for this (it has django integration) and diagrams can be generated
- authentication should be based on "blackbox" tokens and acquired via oauth2 password flow
- tags can be searched and managed on their own API domain - `/api/tags` - but also listed, associated and dissociated as a nested representation of products - `/api/product/<id>/tags`

Optional features:
- run the app in a docker-compose env
- run type analysis - https://www.mypy-lang.org/. Would likely be better to upgrade to python 3.11 beforehand because it supports better typing
- transition code to async where applicable
- the change in the DB caused by placing an order should emit an event to a message/event stream (e.g. kafka)
- place product information (name, description, stock and tags) in an elasticsearch index and use it to list & search
- social features such as "follow user"
