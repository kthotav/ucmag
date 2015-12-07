# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    # response.flash = T("Hello World")
    return dict(message=T('Welcome to UC Magazine!'))

@auth.requires_login()
def student_life():
    # return dict(message="Student Life Page")
        # db.blog_post.created_on.default = request.now
        # db.blog_post.created_on.writable = False
        # db.blog_post.created_on.readable = False
    form = SQLFORM(db.blog_post).process()
    if form.accepted:
        session.flash = "Posted!"
        redirect(URL('student_life'))
    rows = db(db.blog_post).select(orderby=db.blog_post.title.upper())
    return locals()

def show():
    post = db.blog_post(request.args(0, cast=int))
    db.blog_comment_sl.blog_post.default = post.id

    # Prevent commenter from overriding which post to comment on.
    db.blog_comment_sl.blog_post.readable = False
    db.blog_comment_sl.blog_post.writable = False

    # Process what was posted
    form = SQLFORM(db.blog_comment_sl).process()
    # Comment on what was posted
    comment_sl = db(db.blog_comment_sl.blog_post==post.id).select()

    return locals()

@auth.requires_login()
def sports():
    form = SQLFORM(db.blog_post_s).process()
    if form.accepted:
        session.flash = "Posted!"
        redirect(URL('sports'))
    rows = db(db.blog_post_s).select(orderby=db.blog_post_s.title.upper())
    return locals()

def show_s():
    post_s = db.blog_post_s(request.args(0, cast=int))
    db.blog_comment_s.blog_post_s.default = post_s.id

    # Prevent commenter from overriding which post to comment on.
    db.blog_comment_s.blog_post_s.readable = False
    db.blog_comment_s.blog_post_s.writable = False

    # Process what was posted
    form = SQLFORM(db.blog_comment_s).process()
    # Comment on what was posted
    comment_s = db(db.blog_comment_s.blog_post_s==post_s.id).select()

    return locals()

def events():
    form = SQLFORM(db.blog_post_e).process()
    if form.accepted:
        session.flash = "Posted!"
        redirect(URL('events'))
    rows = db(db.blog_post_e).select(orderby=db.blog_post_e.title.upper())
    return locals()

def show_e():
    post_e = db.blog_post_e(request.args(0, cast=int))
    db.blog_comment_e.blog_post_e.default = post_e.id

    # Prevent commenter from overriding which post to comment on.
    db.blog_comment_e.blog_post_e.readable = False
    db.blog_comment_e.blog_post_e.writable = False

    # Process what was posted
    form = SQLFORM(db.blog_comment_e).process()
    # Comment on what was posted
    comment_e = db(db.blog_comment_e.blog_post_e==post_e.id).select()

    return locals()

# def create():
#     form = SQLFORM(db.blog_post).process()
#     return locals()

# def show_s():
#     post = db.blog_post_s(request.args(0, cast=int))
#     db.blog_comment_s.blog_post.default = post_s.id
#
#     # Prevent commenter from overriding which post to comment on.
#     db.blog_comment_s.blog_post.readable = False
#     db.blog_comment_s.blog_post.writable = False
#
#     # Process what was posted
#     form = SQLFORM(db.blog_comment_s).process()
#     # Comment on what was posted
#     comment_s = db(db.blog_comment_s.blog_post==post_s.id).select()
#
#     return locals()

# Defines the grid for the managers page.
@auth.requires_membership('managers')
def manage():
    grid = SQLFORM.grid(db.blog_post)
    return locals()

def log_in():
    return dict(message="Log in Page")

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()