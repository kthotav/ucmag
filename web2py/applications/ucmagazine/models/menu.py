# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

# response.logo = A( XML('&nbsp'), B('UC Magazine'), XML('&nbsp'),
#                   _class="brand-logo",_href=URL('default', 'index'))

response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Student Life'), False, URL('default', 'list_posts_by_votes', args='student-life'), []),
    (T('Sports'), False, URL('default', 'list_posts_by_votes', args='sports'), []),
    (T('Events'), False, URL('default', 'list_posts_by_votes', args='events'), []),
]

if auth.user:
    response.menu.append ( (T('My Stories'), False, URL('default', 'mystories'), [])  )

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller

if DEVELOPMENT_MENU: _()

# If a manager signs in, have a Manage tab appear on the navbar. When
# it is clicked, the manager is taken to the manage page.
if auth.has_membership('managers'):
    response.menu.append((T('Manage'), False, URL('default', 'manage')))

if "auth" in locals(): auth.wikimenu()
