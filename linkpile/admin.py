from django.contrib import admin

from linkpile.models import Link

class LinkAdmin( admin.ModelAdmin ):
    list_display = ['date', 'shared', 'public', 'friends', 'family', 'title',]
    list_display_links = ['title']
    ordering = ['-date']
    list_filter = ['public',]
    search_fields = ['title', 'description', 'url', 'tags',]

admin.site.register(Link, LinkAdmin)
