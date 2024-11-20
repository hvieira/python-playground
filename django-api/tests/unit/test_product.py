import pytest

from store_api.models import Product

DUMMY_TITLE = "test"
DUMMY_DESCRIPTION = "test description"
DUMMY_PRICE = 12300


@pytest.mark.django_db
class TestProductStateTransitions:

    @pytest.mark.parametrize(
        "initial_state",
        [
            Product.STATE_DRAFT,
            Product.STATE_AVAILABLE,
            Product.STATE_SOLD_OUT,
        ],
    )
    def test_delete(self, initial_state):
        product = Product(
            state=initial_state,
            title=DUMMY_TITLE,
            description=DUMMY_DESCRIPTION,
            price=DUMMY_PRICE,
        )
        assert product.deleted is None

        product.delete()

        assert product.state == Product.STATE_DELETED
        assert product.deleted is not None
