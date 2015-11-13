# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from datetime import datetime, timedelta


def index():
    """ This controller returns a dictionary rendered by the view.
    It lists all the boards """
    print "REQUEST:"
    print request.args
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=7
    limitby=(page*items_per_page,(page+1)*items_per_page+1)

    boards = db(db.board).select(orderby=~db.board.created_on, limitby=limitby)

    today_start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for board in boards:
        board['posts'] = db((db.board_posts.board_id == board.id) & (db.board_posts.created_on > today_start_time)).count()

    return dict(boards=boards, page=page, items_per_page=items_per_page)

@auth.requires_login()
def create_board():
    """ creates a new board """
    form = SQLFORM(db.board).process(next=URL('index'))
    return dict(form=form)


def show_board():
    """ displays a board's page with the posts"""

    print "show_board REQUEST:"
    print request.args

    this_board = db.board(request.args(0,cast=int)) or redirect(URL('index'))
    print this_board.id
    db.board_posts.board_id.default = this_board.id
    form = SQLFORM(db.board_posts).process()
    posts = db(db.board_posts.board_id==this_board.id).select(orderby=~db.board_posts.created_on)
    return dict(board=this_board, posts=posts, form=form)

@auth.requires_login()
def create_post():
    this_board = db.board(request.args(0,cast=int))
    db.board_posts.board_id.default = this_board.id
    form = SQLFORM(db.board_posts)
    if form.process().accepted:
        redirect(URL('default', 'show_board', args=[this_board.id]))
    return dict(form=form)


@auth.requires_login()
def edit_board():
    """edit an existing board"""
    this_board = db.board(request.args(0,cast=int)) or redirect(URL('index'))
    if auth.user and this_board and auth.user.id == this_board.created_by:
        form = SQLFORM(db.board, this_board).process(next = URL('show_board',args=request.args))
    else:
        session.flash = "Not Authorized"
        redirect(URL('default', 'show_board', args=request.args))
    return dict(form=form)

@auth.requires_login()
def edit_posts():
    """edit an existing board"""
    this_board_posts = db.board_posts(request.args(0,cast=int)) or redirect(URL('show_board'))
    if auth.user and this_board_posts and auth.user.id == this_board_posts.created_by:
        form = SQLFORM(db.board_posts, this_board_posts)
        if form.process().accepted:
            redirect(URL('default', 'show_board', args=[this_board_posts.board_id]))
    else:
        session.flash = "Not Authorized"
        redirect(URL('default', 'show_board', args=[this_board_posts.board_id]))
    return dict(form=form)

@auth.requires_login()
def delete_post():
    this_board_posts = db.board_posts(request.args(0,cast=int)) or redirect(URL('show_board'))
    if auth.user and this_board_posts and auth.user.id == this_board_posts.created_by:
        db(db.board_posts.id == int(request.args(0))).delete()
        session.flash = "Deleted"
    else:
        session.flash = "Not Authorized"

    return redirect(URL('default', 'show_board', args=[this_board_posts.board_id]))

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
