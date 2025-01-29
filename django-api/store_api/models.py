import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


class BaseEntity(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated = models.DateTimeField(null=False, auto_now_add=True)
    deleted = models.DateTimeField(null=True)


# TODO apply FSM to a state field (active, not active - which should replace the custom validation function below)
class User(AbstractUser, BaseEntity):

    def save(self, **kwargs):
        self._validate_pre_save()
        super().save(**kwargs)

    def _validate_pre_save(self):
        if self.deleted and self.is_active:
            # TODO create a custom error for this
            raise RuntimeError("A deleted user cannot be active")


class Tag(BaseEntity):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, null=False)

    # TODO move this into the base class
    # TODO make this a state machine
    def delete(self):
        self.deleted = timezone.now()
        self.save()


class Product(BaseEntity):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="%(app_label)s_%(class)s_price_gt_zero",
            )
        ]

    STATE_DRAFT = "DRAFT"
    STATE_AVAILABLE = "AVAILABLE"
    STATE_SOLD_OUT = "SOLD_OUT"
    STATE_DELETED = "DELETED"
    STATES = {
        STATE_DRAFT: "Draft",
        STATE_AVAILABLE: "Available",
        STATE_SOLD_OUT: "Sold Out",
        STATE_DELETED: "Deleted",
    }

    title = models.CharField(null=False, max_length=100)
    description = models.CharField(null=False, max_length=1000)
    price = models.IntegerField(null=False)
    state = FSMField(null=False, choices=STATES, default=STATE_DRAFT)
    owner_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f"<Product id={self.id} title={self.title} state={self.state}>"

    @transition(field=state, source="+", target=STATE_DELETED)
    def delete(self):
        """
        Deletes a product, changing state to Deleted and adding timestamp to deleted field. The stock
        will also be deleted to save space.
        """
        # if an undelete operation is to be supported, it needs to restore the default variant in stock
        self.stock.all().delete()
        self.deleted = timezone.now()

        # TODO what would happen to a order (in each of its states) that has a product that is suddenly deleted


class ProductStock(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "product"],
                name="%(app_label)s_%(class)s_unique_per_product_and_variant",
            ),
            models.CheckConstraint(
                condition=models.Q(available__gte=0),
                name="%(app_label)s_%(class)s_available_gte_zero",
            ),
        ]

    VARIANT_DEFAULT = "default"

    # the default variant for products which only have 1 variant
    variant = models.CharField(default=VARIANT_DEFAULT)
    product = models.ForeignKey(
        Product, on_delete=models.DO_NOTHING, related_name="stock"
    )
    available = models.IntegerField(null=False)

    def __str__(self):
        return f"<ProductStock id={self.id} variant={self.variant} available={self.available}>"


class Order(BaseEntity):

    class States(models.TextChoices):
        PENDING = "PENDING", ("Pending")
        SHIPPED = "SHIPPED", ("Shipped")
        CANCELLED = "CANCELLED", ("Cancelled")

    state = FSMField(null=False, choices=States, default=States.PENDING)
    customer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    products = models.ManyToManyField(
        Product,
        through="OrderLineItem",
        through_fields=("order", "product"),
    )


class OrderLineItem(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="%(app_label)s_%(class)s_quantity_gt_zero",
            )
        ]

    pk = models.CompositePrimaryKey("order_id", "product_id")
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    variant = models.CharField(null=False)
    quantity = models.IntegerField(null=False)
