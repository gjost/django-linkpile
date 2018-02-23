# -*- coding: utf-8 -*-

from datetime import datetime
import random
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from dateutil import parser
import pytz
import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import utc

from tagging.fields import TagField


class Link( models.Model ):
    """
    """
    user = models.ForeignKey(User)
    family = models.BooleanField(default=False)
    friends = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    shared = models.BooleanField(default=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=400)
    date = models.DateTimeField('Date published')
    tags = TagField(blank=True, null=True)
    
    class Meta:
        ordering = ('-date',)
        get_latest_by = 'date'
    
    def __repr__( self ):
        return u'<Link %s %s>' % (self.id, self.title)
    
    def __unicode__( self ):
        return u'%s' %(self.title)
    
    def absolute_url( self ):
        return reverse('linkpile-link', args=[self.id])
    
    def edit_url( self ):
        return reverse('linkpile-edit', args=[self.id])
    
    def archive_url( self ):
        """Link URL at archive.org
        """
        return 'https://web.archive.org/web/*/%s' % self.url

    @staticmethod
    def from_dict(data):
        dt = pytz.timezone(settings.TIME_ZONE).localize(
            parser.parse(data['date'])
        )
        link = Link(
            user = User.objects.get(username=data['user']),
            family = data['family'],
            friends = data['friends'],
            public = data['public'],
            shared = data['shared'],
            title = data['title'],
            description = data['description'],
            url = data['url'],
            date = dt,
            tags = data['tags'], # TODO tag objects
        )
        return link

    def to_dict(self):
        return {
            'user': self.user.username,
            'family': self.family,
            'friends': self.friends,
            'public': self.public,
            'shared': self.shared,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'date': self.date.isoformat(),
            'tags': self.tags,
        }

    def save( self, *args, **kwargs ):
        if not self.date:
            self.date = datetime.utcnow().replace(tzinfo=utc)
        if self.url and not self.title:
            self.title = Link.scrape(self.url)
        super(Link, self).save(*args, **kwargs)
    
    def can_edit( self, user ):
        """
        TODO refactor
        """
        if user and user.is_staff:
            return True
        return False
    
    def can_view( self, user, family, friends ):
        """
        TODO refactor
        """
        if not family and friends:
            return False
        if self.public: return True
        if (self.friends and self.family) and ((user in friends) or (user in family)):
            return True
        if (self.friends and not self.family) and (user in friends) and (user not in family):
            return True
        if (self.family and not self.friends) and (user in family) and (user not in friends):
            return True
        if user.is_staff:
            return True
        return False

    def private( self ):
        """
        TODO refactor
        """
        if not self.public:
            return 0
        return 1
    
    @staticmethod
    def get_recent( num_items=10 ):
        """Gets the N most recent Links
        """
        return Link.objects.filter(public=True)[:num_items]
    
    @staticmethod
    def get_random():
        """Gets a random Link; sometimes returns None
        """
        link = None
        objects_by_id = Link.objects.order_by('-id')
        if objects_by_id:
            max_id = objects_by_id[0].id
            random_id = random.randint(1, max_id + 1)
            attempts = 0
            while( (not link) and (attempts < 10) ):
                try:
                    link = Link.objects.get(id=random_id)
                except:
                    pass
                finally:
                    attempts = attempts + 1
        return link
    
    @staticmethod
    def scrape( url ):
        """Scrapes the link URL and try to get title.
        
        >>> Link.scrape('http://ymarkov.livejournal.com/270570.html')
        u'ymarkov: The Last Ring-bearer'
        """
        title = '[scrape failed]'
        check = urlparse(url)
        if check and check.scheme and (check.scheme in ['http', 'https']):
            r = requests.get(url, allow_redirects=True)
            if r.status_code in [200, 301, 302]:
                soup = BeautifulSoup(r.text)
                if soup.find('title') and soup.find('title').contents:
                    title = soup.find('title').contents[0]
        return title
    
    def others_in_domain( self ):
        """Gets other links from the same domain.
        """
        try:
            check = urlparse(self.url)
            if check and check.netloc:
                links = Link.objects.exclude(id=self.id)
                links = links.filter(url__contains=check.netloc)
                return links
        except:
            pass
        return []

def get_links( owner, user ):
    """Show only links that the user is allowed to see.
    """
    family = [] # user.get_profile().family
    friends = [] # user.get_profile().friends
    links = Link.objects.all()
    if user == owner:
        return links
    links = links.filter(public=True)
    return links
