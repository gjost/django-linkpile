import logging

from django import forms
from django.conf import settings

from tagging.forms import TagField

from linkpile.models import Link

class LinkNewForm( forms.Form ):
    """Initial form for creating a Link; gets the URL.
    """
    url = forms.URLField()

class LinkEditForm( forms.Form ):
    """User-facing form for Links.
    """
    url = forms.URLField()
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    tags = TagField(required=False)
    date = forms.DateTimeField()
    family = forms.BooleanField(required=False)
    friends = forms.BooleanField(required=False)
    public = forms.BooleanField(required=False)
    shared = forms.BooleanField(required=False)
