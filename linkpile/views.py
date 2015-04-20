from datetime import datetime

import pytz

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.db.models import Q
from django.shortcuts import Http404, get_object_or_404, render_to_response
from django.template import RequestContext

from tagging.models import Tag, TaggedItem

from linkpile.models import Link
from linkpile.forms import LinkNewForm, LinkEditForm

TIMEZONE = pytz.timezone(settings.TIME_ZONE)

def app_context( request ):
    """Context processor that handles variables used in many views.
    """
    context = {
        'request': request,
        'settings': settings,
    }
    return context

# views -----------------------------------------------------------------------

def index( request ):
    """
    """
    links = Link.objects.all().order_by('-date')
    if request.GET.get('keywords', None):
        words = request.GET.get('keywords').split(' ')
        for word in words:
            links = links.filter(title__icontains = word) \
                    | links.filter(description__icontains = word) \
                    | links.filter(url__icontains = word) \
                    | links.filter(tags__icontains = word)
    # filter by user
    show_perms = False
    if request.user:
        if request.user.is_staff:
            show_perms = True
        else:
            links = links.filter(Q(public=1) | Q(friends=1) | Q(family=1))
    else:
        links = links.filter(public=1)
    # can_edit
    for link in links:
        if link.can_edit(request.user):
            link.can_edit = True
    return render_to_response(
        'linkpile/index.html',
        {
            'links': links,
            'random': Link.get_random(),
            'show_perms': show_perms,
            'newlinkform': LinkNewForm({}),
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

def tags( request, tags=None ):
    """
    """
    if tags:
        tags = tags.split('+')
        links = TaggedItem.objects.get_by_model(Link, tags)
    # filter by user
    show_perms = False
    if request.user:
        if request.user.is_staff:
            show_perms = True
        else:
            links = links.filter(Q(public=1) | Q(friends=1) | Q(family=1))
    else:
        links = links.filter(public=1)
    return render_to_response(
        'linkpile/index.html',
        {
            'links': links,
            'show_perms': show_perms,
            'tags': tags,
            'newlinkform': LinkNewForm({}),
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

def detail( request, link_id ):
    """
    """
    link = get_object_or_404(Link, pk=link_id)
    if link.can_edit(request.user):
        link.can_edit = True
    return render_to_response(
        'linkpile/detail.html',
        {
            'link': link,
            'newlinkform': LinkNewForm({}),
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

@login_required
def new( request ):
    """
    """
    if not request.user.is_staff:
        raise Http404
    link = None
    if request.method == 'POST':
        form = LinkNewForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            # link exists already?
            try:
                existing = Link.objects.get(url=url)
                if existing:
                    return HttpResponseRedirect(reverse('linkpile-edit', {'link_id':existing.id}))
            except:
                pass
            # if not, make new one
            if not link:
                link = Link(url=url)
            link.user = request.user
            link.save()
            return HttpResponseRedirect(reverse('linkpile-edit', kwargs={'link_id':link.id}))
    else:
        show_errors = False
        data = {}
        fields = ['url',]
        form = LinkNewForm(data)
    return render_to_response(
        'linkpile/new.html',
        {
            'link': link,
            'form': form,
            'show_errors': show_errors,
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

@login_required
def edit( request, link_id ):
    """
    """
    link = get_object_or_404(Link, pk=link_id)
    if not link.can_edit(request.user):
        raise Http404
    show_errors = False
    # edit the link
    if request.method == 'POST':
        form = LinkEditForm(request.POST)
        show_errors = True
        if form.is_valid():
            if not link:
                link = Link()
            link.url = form.cleaned_data['url']
            link.title = form.cleaned_data['title']
            link.description = form.cleaned_data['description']
            link.tags = form.cleaned_data['tags']
            link.date = form.cleaned_data['date']
            link.family = form.cleaned_data['family']
            link.friends = form.cleaned_data['friends']
            link.public = form.cleaned_data['public']
            link.shared = form.cleaned_data['shared']
            link.save()
            # done
            return HttpResponseRedirect(link.absolute_url())
    else:
        data = {}
        fields = ['url',
                  'title',
                  'description',
                  'tags',
                  'date',
                  'family',
                  'friends',
                  'public',
                  'shared',]
        # now insert actual data
        if link:
            data['url'] = link.url
            data['title'] = link.title
            data['description'] = link.description
            data['tags'] = link.tags
            data['date'] = link.date
            data['family'] = link.family
            data['friends'] = link.friends
            data['public'] = link.public
            data['shared'] = link.shared
        form = LinkEditForm(data)
    return render_to_response(
        'linkpile/edit.html',
        {
            'link': link,
            'form': form,
            'show_errors': show_errors,
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

@login_required
def export( request ):
    """Export links in format required by 
    """
    if not request.user.is_authenticated():
        raise Http404
    links = Link.objects.all().order_by('date')[:10]
    return render_to_response(
        'linkpile/export.html',
        {
            'links': links,
            'today': datetime.now(tz=TIMEZONE),
        },
        context_instance=RequestContext(request, processors=[app_context])
    )
