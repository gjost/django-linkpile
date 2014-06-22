from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse

from linkpile.models import Link

class LinksFeed( Feed ):
    title = 'Linkpile Links'
    link = '/linkpile/'
    description = 'A pile of links from around the web'
    
    def items( self ):
        return Link.get_recent(10)
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.description
    
    def item_link(self, item):
        return reverse('linkpile-link', args=[item.id])
