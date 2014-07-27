# Small mixin for any model class, which adds few useful methods
from models import Tag, TagToTarget

class TagMixin(object):

    def _get_tags_links(self):
        """Inner function for finding Tag-To-Target objects"""
        tag_links = TagToTarget.objects.filter(object_id=self.id) \
            .filter(content_type__model=self.__class__.__name__.lower())
        return tag_links

    def get_tags(self):
        """Get all tags for object"""
        return [i.tag for i in self._get_tags_links()]

    def add_tags(self, tags):
        """Just adding new tags"""
        Tag.add_new_tags(tags, self)

    def delete_all_tags(self):

        old_tags_links = _get_tags_links()
        old_tags.links.delete()

    def replace_tags(self, tags):
        """Removing all tag links from the object and creating new one"""
        
        # Removing links to old tags
        self.delete_all_tags()

        # Adding new
        self.add_tags(tags)