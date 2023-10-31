from django.conf import settings
from server.apps.users.models import CustomUser
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from .managers import FundraiserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File
import random
import uuid

CATEGORY_NAMES = (
    ("help", "Help Needed"),
    ("trending", "Trending"),
    ("urgent", "Urgent"),
)


class CategoryEnum(object):
    OTHERS = "others"
    TRENDING = "trending"
    URGENT = "urgent"

def compress(image):
    im = Image.open(image)
    im_io = BytesIO() 
    im.save(im_io, 'JPEG', quality=60) 
    new_image = File(im_io, name=image.name)
    return new_image

class Category(models.Model):
    name = models.CharField(
        max_length=20,
        choices=CATEGORY_NAMES,
        default=CategoryEnum.OTHERS,
        primary_key=True,
    )
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse("catalogue:category_detail", args=[self.slug])

    @classmethod
    def get_default(cls):
        category, created = cls.objects.get_or_create(
            name=CategoryEnum.OTHERS, defaults=dict(slug="others")
        )
        return category.pk

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


def upload_to(instance, filename):
    return f"images/{filename}"


class Fundraiser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        related_name="fundraiser",
        on_delete=models.SET_DEFAULT,
        default=Category.get_default,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="fundraiser_creator",
        default=CustomUser.get_default,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to, default="images/default.png")
    slug = models.SlugField(max_length=255, unique=True, null=True)
    tags = models.CharField(max_length=30, default="newest")
    total_amount = models.DecimalField(
        max_digits=1000,
        decimal_places=2,
    )
    remaining_amount = models.DecimalField(max_digits=1000, decimal_places=2, null=True)
    total_backers = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    fundraisers = FundraiserManager()

    class Meta:
        verbose_name_plural = "fundraisers"
        ordering = ("-created",)

    def get_absolute_url(self):
        return reverse("catalogue:fundraiser_detail", args=[self.slug])
    
#    def save(self, *args, **kwargs):
#        new_image = compress(self.image)
#        self.image = new_image
#        return super().save(*args, **kwargs)


    def __str__(self):
        return self.title


def update_fundraiser(sender, instance, created, *args, **kwargs):

    from server.apps.catalogue.serializers import FundraiserSerializer

    fr = Fundraiser.objects.get(id=instance.fundraiser.id)
    data = dict()
    data["total_backers"] = fr.total_backers + 1
    data["remaining_amount"] = fr.remaining_amount - instance.value
    s = FundraiserSerializer(fr, data=data, partial=True)
    s.is_valid(raise_exception=True)
    s.save()


from server.apps.checkout.models import Payment

post_save.connect(update_fundraiser, sender=Payment)
