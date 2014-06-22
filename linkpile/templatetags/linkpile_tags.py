import datetime
from django import template

register = template.Library()

def linkpile_link( obj ):
    """list-view template for Link
    """
    t = template.loader.get_template('linkpile/linkpile-link.html')
    return t.render(template.Context({'link':obj}))

register.simple_tag(linkpile_link)
