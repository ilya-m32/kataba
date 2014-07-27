from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.http import urlquote

try:
    from local_settings import MIN_TAG_LEN, MAX_TAG_LEN
except ImportError:
    MAX_TAG_LEN = 60
    MIN_TAG_LEN = 3

class Tag(models.Model):

    name = models.SlugField(max_length=MAX_TAG_LEN, blank=False)
    counter = models.PositiveIntegerField(default=0)

    @property
    def url(self):
        return urlquote(self.name)

    def _get_or_create_con(self, target):
        """Create's (with saving) and returns connection object between tag and, well, object."""
        link = TagToTarget(tag=self, content_object=target)
        try:
            link = TagToTarget.objects.get(tag=self, content_type=link.content_type, object_id=target.id)
        except ObjectDoesNotExist:
            link.save()
        return link

    @staticmethod
    def parse_tags(tags):
        """Parses tag from str into array."""
        size_check = lambda x: len(x) >= MIN_TAG_LEN and len(x) <= MAX_TAG_LEN
        return filter(size_check, [escape(i.strip().lower().capitalize()) for i in tags.split(',')])

    @classmethod
    def add_new_tags(cls, tags, target=None):
        """Recives raw tag list ("asd, qwerty, qqq") and connects tags from there with target."""
        tags = cls.parse_tags(tags)

        for tag_name in tags:
            tag = cls.objects.get_or_create(name=tag_name)[0]
            if target:
                tag._get_or_create_con(target)

    @classmethod
    def complete_tag_name(cls, tag, limit=6):
        tags = cls.objects.filter(name__istartswith=tag) \
            .values_list('name', flat=True).distinct()
        if limit:
            tags = tags[:limit]
        return tags

    def __str__(self):
        return self.name


class TagToTarget(models.Model):

    tag = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('content_type', 'tag', 'object_id'))

    def delete(self, *args, **kwargs):
        # -1 to tag counter 
        self.tag.counter -= 1
        self.tag.save()
        super(TagToTarget, self).delete(*args, **kwargs)

    @classmethod
    def get_popular_tags(cls, limit=6):
        """Just most popular tags by all targets"""
        tags = cls.objects.order_by(counter)
        if limit:
            tags = tags[:limit]
        return tags

    def __str__(self):
        return ' - '.join((str(self.tag), str(self.content_object)))

# Signals
# +1 to tag counter if there is new link
@receiver(post_save, sender=TagToTarget)
def post_save_callback(sender, instance, **kwargs):
    if kwargs['created']:
        instance.tag.counter += 1
        instance.tag.save()