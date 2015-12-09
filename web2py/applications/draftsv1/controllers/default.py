#*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

POSTS_PER_PAGE = 12

def get_category():
    category_name = request.args(0)
    category = db.category(name=category_name)
    if not category:
        session.flash = 'page not found'
        redirect(URL('index'))
    return category

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    # response.flash = T("Hello World")
    # return dict(message=T('Welcome to web2py!'))
    #if auth.user: redirect('tasks')
    rows = db(db.category).select()
    return locals()

#############################################################################################
# TASKS PAGE: issue-reporting tool/system
me = auth.user_id
def tasks():
    db.task.created_on.readable=True
    db.task.created_by.readable=True

    db.task.title.represent = lambda title, row:\
        A(title, _href=URL('view_task', args=row.id))

    # query = (db.task.assigned_to==me)|(db.task.created_by==me)
    query = (db.task)
    grid = SQLFORM.grid(query, orderby=~db.task.modified_on,
                        create=False, details=False, editable=False, csv=False,
                        deletable=lambda row: (row.created_by==me),
                        fields=[
                            db.task.status,
                            db.task.title,
                            db.task.created_on,
                            db.task.created_by,
                            db.task.assigned_to
                        ])

    return locals()
#############################################################################################

#############################################################################################
# TASKS PAGE FOR CREATING TASKS: issue-reporting tool/system
@auth.requires_login()
def create_task():
    # task creators should not be
    # allowed to set the status of
    # the task since it will default
    # to "Assigned"
    db.task.status.writable=False
    db.task.status.readable=False

    # Make it so only manager accounts are selectable when creating a task.
    query = (db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'managers')
    db.task.assigned_to.requires = IS_IN_DB(db(query), 'auth_user.id', '%(first_name)s %(last_name)s (%(id)s)')


    # Display the form for creating
    # and processing a task.
    form = SQLFORM(db.task).process()

    if form.accepted:
        # send_email(to=db.auth_user(form.vars.assigned_to).email,
        #                sender=auth.user.email,
        #                subject="New Task Assigned: %s" % form.vars.title,
        #                message=form.vars.description)

        # PROTOCOL 1: IGNORE/EXPERIMENTAL
        send_email(to=db.auth_user(form.vars.assigned_to).email,
                   sender=auth.user.email,
                   subject="New Task Assigned: %s" % form.vars.title,
                   message=form.vars.description)
        redirect(URL('tasks'))
    return locals()
#############################################################################################




#############################################################################################
def error(message="not authorized"):
    session.flash = message
    redirect(URL('tasks'))
#############################################################################################




#############################################################################################
# VIEW_TASK PAGE FOR VIEWING TASKS: issue-reporting tool/system
# Takes a task <id> argument
def view_task():
    task_id = request.args(0, cast=int)
    task = db.task(task_id) or error()
    #if not task.created_by==me and not task.assigned_to==me: error()

    return locals()


#############################################################################################


#############################################################################################
# EDIT_TASKS PAGE FOR EDITING TASKS: issue-reporting tool/system
# Takes a task <id> argument
@auth.requires_login()
def edit_task():
    task_id = request.args(0, cast=int)
    task = db.task(task_id) or error()
    #if not task.created_by==me or not task.assigned_to==me: error()
    if task.assigned_to!=me: error()

    # Creators of a task can only change what issue they're assigning the
    # task to.
    if task.created_by==me:
        task.assigned_to.writable=True
    else:
        task.assigned_to.writable=False
        #task.status.requires=IS_IN_SET(('accepted', 'rejected', 'completed'))

    # Make it so only manager accounts are selectable when creating a task.
    query = (db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'managers')
    db.task.assigned_to.requires = IS_IN_DB(db(query), 'auth_user.id', '%(first_name)s %(last_name)s (%(id)s)')

    form = SQLFORM(db.task, task,
                   showid=False,
                   deletable=(task.created_by==me)).process()
    if form.accepted:
        # PROTOCOL 2: IGNORE/EXPERIMENTAL
        if task.created_by==me:
            email_to = db.auth_user(form.vars.assigned_to).email
        else:
            email_to = db.auth_user(task.created_by).email

        send_email(to=email_to, sender=auth.user.email,
                   subject= "Task Changed (%(status)s): %(title)s" % form.vars,
                   message=form.vars.description)


        # email_to = db.auth_user(
        #         form.vars.assigned_to if task.created_by==me else task.created_by).email
        #
        # send_email(to=email_to, sender=auth.user.email,
        #            subject= "Task Changed (%(status)s): %(title)s" % form.vars,
        #            message=form.vars.description)

        redirect(URL('view_task', args=task.id))
    return locals()
#############################################################################################

# We need a page for users to create a post. To create a post, we simply need to
# specify which category we wish to create a post in. This will be done by going
# to the specific category and pushing a create button on that category's page.
@auth.requires_login()
def create_post():
    category = get_category()
    # Creates a form. You need to process a form in order for it to submit.
    db.post.category.default = category.id
    form = SQLFORM(db.post).process(next='view_post/[id]')
    return locals()

# We need a page for users to edit a post. To edit a post, we need to know
# what the post ID is. In order to edit a post, it is important to determine which
# post will undergo editing. To do this, we pass the request.args(0, cast=int)
# argument which indicates the post to be edited.
@auth.requires_login()
def edit_post():
    id = request.args(0,cast=int)
    # Creates a form for editing given the id.
    form = SQLFORM(db.post, id, showid=False).process(next='view_post/[id]')
    return locals()

# To order posts by time (newest on top), we must know the post's category and
# page.
def list_posts_by_datetime():
    response.view = 'default/list_posts_by_votes.html'
    category = get_category()
    page = request.args(1,cast=int, default=0)
    if auth.user:
        l =  db((db.post.created_by==auth.user.id) & (db.post.draft > 0) & (db.post.category==category.id)).select(db.post.id).as_list()
        auth_user_posts_ids =  map(lambda d: d['id'], l)
        query = ( (db.post.category==category.id) & ((db.post.draft==0) | (db.post.draft==None)) ) | (db.post.id.belongs(auth_user_posts_ids))
    else:
        query = (db.post.category==category.id) & ((db.post.draft==0) | (db.post.draft==None))


    if request.vars and 'uc' in request.vars and request.vars.uc in UCS:
        uc = request.vars.uc
        query &= db.post.uc==uc

    # Display the rows of posts where the category of the posts matches the
    # category IDs of the post and then display them in reverse chronological
    # order in terms of the time in which they were created. We will also limit
    # the number of posts by 10 per page. Start basically mean that if we are on
    # page 0, we should see the 0th post. If we're on page 1, we should start with
    # the 10th post. If we are on page 2, it should start at the 2nd post. With
    # stop, it basically represents how many posts we are going to show.
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db( query ).select(orderby=~db.post.created_on,
                                                    limitby=(start,stop))

    if auth.user:
        db.post.category.default = category.id
        db.post.uc.requires=IS_IN_SET( UCS )
        form_new_post = SQLFORM(db.post, submit_button='Create').process()
        draft_button = TAG.INPUT(_name='Draft', _value='Draft', _type="submit", _class="btn btn-default active")
        form_new_post[0][-1][1].append (draft_button)
        if form_new_post.accepted:
            if 'Draft' in request.vars:
                db(db.post.id == form_new_post.vars.id).update(draft=1)
            response.flash = "Post Created"
            return redirect( URL(args=request.args) )

    else:
        form_new_post = A("Please login to create a story", _href=URL('user/login', vars=dict(_next=URL(args=request.args))))


    return locals()


def list_posts_by_votes():
    category = get_category()
    page = request.args(1,cast=int, default=0)

    if auth.user:
        l =  db((db.post.created_by==auth.user.id) & (db.post.draft > 0) & (db.post.category==category.id)).select(db.post.id).as_list()
        auth_user_posts_ids =  map(lambda d: d['id'], l)
        query = ( (db.post.category==category.id) & ((db.post.draft==0) | (db.post.draft==None)) ) | (db.post.id.belongs(auth_user_posts_ids))
    else:
        query = (db.post.category==category.id) & ((db.post.draft==0) | (db.post.draft==None))

    if request.vars and 'uc' in request.vars and request.vars.uc in UCS:
        uc = request.vars.uc
        query &= db.post.uc==uc

    # Display the rows of posts where the category of the posts matches the
    # category IDs of the post and then display them in reverse chronological
    # order in terms of the number of votes received. We will also limit
    # the number of posts by 10 per page. Start basically mean that if we are on
    # page 0, we should see the 0th post. If we're on page 1, we should start with
    # the 1st post. If we are on page 2, it should start at the 2nd post. With
    # stop, it basically represents how many posts we are going to show.
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db(query).select(orderby=~db.post.votes,
                                                    limitby=(start,stop))

    if auth.user:
        db.post.category.default = category.id
        db.post.uc.requires=IS_IN_SET( UCS )
        form_new_post = SQLFORM(db.post, submit_button='Create').process()
        draft_button = TAG.INPUT(_name='Draft', _value='Draft', _type="submit", _class="btn btn-default active")
        form_new_post[0][-1][1].append (draft_button)
        if form_new_post.accepted:
            if 'Draft' in request.vars:
                db(db.post.id == form_new_post.vars.id).update(draft=1)
            response.flash = "Post Created"
            return redirect( URL(args=request.args) )
    else:
        form_new_post = A("Please login to create a story", _href=URL('user/login', vars=dict(_next=URL(args=request.args))))

    return locals()

# This allows users to view posts by a particular author. In other words, if you
# click on a particular user's name, it will take you to a view that lists all of
# that person's posts. To view posts by an author, we need to know who the user's
# user_id as well as the page.

################## EXPERIMENTAL: NOT BEING USED
def list_posts_by_author0():
    response.view = 'default/list_posts_by_votes.html'
    user_id = request.args(0,cast=int)
    # Page number; page defaults to 0.
    page = request.args(1,cast=int, default=0)
    # Display the rows of posts where the posts that are "created_by" match the
    # user's ID of the post and then display them in reverse chronological
    # order in terms of most recent posts that the user made. We will also limit
    # the number of posts by 10 per page. Start basically means that if we are on
    # page 0, we should see the 0th post. If we're on page 1, we should start with
    # the 10th post. If we are on page 2, it should start at the 20th post. With
    # stop, it basically represents how many posts we are going to show per page.
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db(db.post.created_by==user_id).select(orderby=~db.post.created_on,
                                                    limitby=(start,stop))
    return locals()


def list_posts_by_author():
    response.view = 'default/list_posts_by_votes.html'
    response.title = ''
    page = request.args(0,cast=int, default=0)
    if request.vars and request.vars.author:
        author_id = int(request.vars.author)
        author = db.auth_user(author_id)
    else:
        author_id = 0

    query = db.post.created_by==author_id

    # Display the rows of posts where the category of the posts matches the
    # category IDs of the post and then display them in reverse chronological
    # order in terms of the time in which they were created. We will also limit
    # the number of posts by 10 per page. Start basically mean that if we are on
    # page 0, we should see the 0th post. If we're on page 1, we should start with
    # the 10th post. If we are on page 2, it should start at the 2nd post. With
    # stop, it basically represents how many posts we are going to show.
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db( query ).select(db.post.ALL, orderby=~db.post.created_on,
                                                    limitby=(start,stop))
    if len(rows)>0:
        response.title = author.first_name + " " + author.last_name + "'s Stories"
    else:
        response.title = "No stories to show!"

    for row in rows:
        row['fav_icon'] = ''

    return locals()


def mystories():
    response.view = 'default/list_posts_by_votes.html'
    response.title = 'My Stories'
    page = request.args(0,cast=int, default=0)
    if request.vars and request.vars.author:
        author_id = int(request.vars.author)
    elif auth.user:
        author_id = auth.user.id
    else:
        author_id = 0

    l =  db((db.post.id==db.fav_post.post) & (db.fav_post.created_by==author_id) & (db.fav_post.is_favourited==1)).select(db.post.id).as_list()
    fav_posts_ids =  map(lambda d: d['id'], l)

    query = (db.post.created_by==author_id) | (db.post.id.belongs(fav_posts_ids))

    # Display the rows of posts where the category of the posts matches the
    # category IDs of the post and then display them in reverse chronological
    # order in terms of the time in which they were created. We will also limit
    # the number of posts by 10 per page. Start basically mean that if we are on
    # page 0, we should see the 0th post. If we're on page 1, we should start with
    # the 10th post. If we are on page 2, it should start at the 2nd post. With
    # stop, it basically represents how many posts we are going to show.
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db( query ).select(db.post.ALL, orderby=~db.post.created_on,
                                                    limitby=(start,stop))

    if len(rows)==0:
        response.title = "You have no stories!"

    for row in rows:
        row['fav_icon'] = get_fav_icon(auth.user.id, row['id'], True)

    return locals()

def myprofile():
    myinfo = db().select(db.myinfo)
    return locals()

def search():
    response.view = 'default/list_posts_by_votes.html'
    search_input = request.vars.search_input or ''
    page = request.args(0,cast=int, default=0)

    query = (db.post.title.ilike('%'+search_input+'%')) | (db.post.body.ilike('%'+search_input+'%'))

    # Display the rows of posts where the category of the posts matches the
    # category IDs of the post and then display them in reverse chronological
    # order in terms of the time in which they were created. We will also limit
    # the number of posts by 10 per page. Start basically mean that if we are on
    # page 0, we should see the 0th post. If we're on page 1, we should start with
    # the 10th post. If we are on page 2, it should start at the 2nd post. With
    # stop, it basically represents how many posts we are going to show.
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db( query ).select(db.post.ALL, orderby=~db.post.created_on,
                                                    limitby=(start,stop))

    if len(rows)==0:
        response.title = "No posts matched your search!"
    else:
        response.title = "You were looking for '" + search_input + "'"

    for row in rows:
        row['fav_icon'] = ''

    return locals()


# We need a page for users to view a post. To view a post, we should obtain the ID of
# the post and the display the post.
def view_post():
    id = request.args(0, cast=int)
    # Display the post, but also display the comments associated with that post. If the
    # post doesn't exist, redirect to the home page.
    post = db.post(id) or redirect(URL('index'))
    comment = db(db.comm.post==post.id).select(orderby=~db.comm.created_on, limitby=(0,1)).first()

    if auth.user and post.created_by != auth.user.id:
       user_id = auth.user.id
    else:
       user_id = 0

    fav_icon = get_fav_icon (user_id, post.id)
    vote_icon = get_vote_icon (user_id, post.id)

    if auth.user:
        # Creates a form for editing given the id.

        db.post.uc.requires=IS_IN_SET(['UC Berkeley', 'UC Davis', 'UC Irvine', 'UC Los Angeles', 'UC Merced',
                                       'UC Riverside', 'UC San Diego', 'UC Santa Barbara', 'UC Santa Cruz'])
        db.post.category.writable = True
        db.post.category.requires = IS_IN_DB(db,'category.id','%(name)s')
        form_edit_post = SQLFORM(db.post, id, showid=False, fields=['uc', 'category', 'title', 'body', 'image'],
                                 submit_button='Update').process(formname='edit_body_form')
#                                 submit_button='Update').process(formname='edit_body_form', next='view_post/[id]')

        if post.image:
            image_element = TR(LABEL(''),
                               IMG(_src=URL(r=request, f='download', args=post.image), _class="img-responsive", _height="16px", _alt='image'),
                               A('delete', _class='material-icons btndel', _title='Delete Image',
                                           _href=URL('default', 'delete_post_image', args=post.id) ) )
            form_edit_post[0].insert(-2, image_element)

        if post.draft > 0:
            make_live_button = TAG.INPUT(_name='Make Live', _value='Make Live', _type="submit",
                                         _class="btn btn-default active")
            form_edit_post[0][-1][1].append (make_live_button)

        cancel_button = TAG.INPUT(_value='Cancel', _type="button",
                                    _class="btn btn-default active", _onclick="cancel_edit_body()")

        form_edit_post[0][-1][1].append(cancel_button)

        if form_edit_post.accepted:
            if 'Make Live' in request.vars:
                db(db.post.id == form_edit_post.vars.id).update(draft=0)
            response.flash = "Post Updated"
            return redirect( URL(args=request.args) )

        db.comm.post.default = id
        db.comm.parent_comm.default = comment.id if comment else None
        form_comments = SQLFORM(db.comm, submit_button='Add comment').process()

        for label in form_comments.elements('label'): label["_style"] = "display:none;"
        no_auth_link=''
    else:
        no_auth_link = A("login to comment", _href=URL('user/login', vars=dict(_next=URL(args=request.args))))
    comments = db(db.comm.post==post.id).select(orderby=db.comm.created_on)
    return locals()

#-#-#------------------------------ VOTING LOGIC ----------------------------------#-#-#

def get_vote_icon (user_id, post_id):

    votes = db( (db.vote.post==post_id) & (db.vote.created_by==user_id) & (db.vote.score==1) ).count()

    # icons
    if user_id == 0 or post_id == 0:
        vote_icon = ''
    elif votes == 0:
        vote_icon = A('', _class="fa fa-thumbs-o-up fa-fw vote-link", _style='color:#86a8a8;', callback=URL('vote', vars={"post_id":post_id}), target='spanVote')
    else:
        vote_icon = A('', _class="fa fa-thumbs-up fa-fw vote-link", _style='color:#86a8a8;', callback=URL('vote', vars={"post_id":post_id}), target='spanVote')

    return vote_icon


def vote():
    user_id = auth.user.id if auth.user else 0
    if request.vars and 'post_id' in request.vars:
        post_id = request.vars.post_id
        post = db.post(post_id)
    else:
        post_id = 0

    if auth.user and post.created_by != auth.user.id:
        query = (db.vote.post==post_id) & (db.vote.created_by==auth.user.id)
        row = db(query).select().last()
        if not row:
            db.vote.insert (post=post_id, score=1)
            db(db.post.id==post_id).update(votes=post.votes+1)
        else:
            vote_id = row['id']
            score = row['score']
            if score == 0:
                db(db.post.id==post_id).update(votes=post.votes+1)
                db(db.vote.id==vote_id).update(score=1)
            else:
                db(db.post.id==post_id).update(votes=post.votes-1)
                db(db.vote.id==vote_id).update(score=0)

    return (get_vote_icon (user_id, post_id))


def favourite():
    user_id = auth.user.id if auth.user else 0
    if request.vars and 'post_id' in request.vars:
        post_id = request.vars.post_id
        post = db.post(post_id)
    else:
        post_id = 0

    if request.vars and request.vars.is_ms:
        is_ms = request.vars.is_ms
    else:
        is_ms = False

    if auth.user and post.created_by != auth.user.id:
        query = (db.fav_post.post==post_id) & (db.fav_post.created_by==auth.user.id)
        row = db(query).select().last()
        if not row:
            db.fav_post.insert (post=post_id, is_favourited=1)
        else:
            fav_id = row['id']
            is_favourited = row['is_favourited']
            if is_favourited == 0:
                db(db.fav_post.id==fav_id).update(is_favourited=1)
            else:
                db(db.fav_post.id==fav_id).update(is_favourited=0)

    if is_ms:
        return redirect(URL('default', 'mystories'))
    else:
        return (get_fav_icon (user_id, post_id))


def get_fav_icon (user_id, post_id, is_ms=False):

    likes = db( (db.fav_post.post==post_id) & (db.fav_post.created_by==user_id) & (db.fav_post.is_favourited==1) ).count()

    # icons
    if user_id == 0 or post_id == 0:
        fav_icon = ''
    elif likes == 0 and is_ms:
        fav_icon = A('', _class="fa fa-star-o fa-fw fav-link", _style="color: #ff8f00 ", _href=URL('favourite', vars={"post_id":post_id, "is_ms":is_ms}) )
    elif likes == 0 and not is_ms:
        fav_icon = A('', _class="fa fa-star-o fa-fw fav-link", _style="color: #ff8f00 ", callback=URL('favourite', vars={"post_id":post_id}), target='spanFav')
    elif likes > 0 and is_ms:
        fav_icon = A('', _class="fa fa-star fa-fw fav-link",  _style="color: #ff8f00 ", _href=URL('favourite', vars={"post_id":post_id, "is_ms":is_ms}) )
    else:
        fav_icon = A('', _class="fa fa-star fa-fw fav-link", _style="color: #ff8f00 ", callback=URL('favourite', vars={"post_id":post_id}), target='spanFav')

    return fav_icon



############# OLD VOTING SYSTEM ##############
# Voting buttons
# We need a callback function to be utilize for clickability. We will make use of
# jQuery and Ajax to accomplish this. Callback is essentially a function that is
# called once an effect is completed. In this case, it's the act of clicking. We
# learned about this here:
# http://www.web2py.com/books/default/chapter/29/11/jquery-and-ajax
# We will implement this feature for post votes (vote_callback) as well as comment
# votes (comm_vote_callback)
def vote_callback():
    vars = request.post_vars
    if vars and auth.user:
        id = vars.id
        direction = +1 if vars.direction == 'up' else -1
        post = db.post(id)
        if post:
            vote = db.vote(post=id, created_by=auth.user.id)
            if not vote:
                post.update_record(votes=post.votes+direction)
                db.vote.insert(post=id, score=direction)
            elif vote.score!=direction:
                post.update_record(votes=post.votes+direction*2)
                vote.update_record(score=direction)
            else:
                pass
        return str(post.votes)
    elif vars and vars.id:
        session.flash="You must be logged in to register your vote"
    post = db.post(vars.id)
    return str(post.votes)

######## OLD VOTING SYSTEM FOR COMMENTS #########
def comm_vote_callback():
    vars = request.post_vars
    if vars and auth.user:
        id = vars.id
        direction = +1 if vars.direction == 'up' else -1
        comm = db.comm(id)
        if comm:
            vote = db.comm_vote(comm=id, created_by=auth.user.id)
            if not vote:
                comm.update_record(votes=comm.votes+direction)
                db.comm_vote.insert(comm=id, score=direction)
            elif vote.score!=direction:
                comm.update_record(votes=comm.votes+direction*2)
                vote.update_record(score=direction)
            else:
                pass
    elif vars and vars.id:
        session.flash="You must be logged in to register your vote"
    comm = db.comm(vars.id)
    return str(comm.votes)



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


# Defines the grid for the managers page.
@auth.requires_membership('managers')
def manage():
    gridposts = SQLFORM.grid(db.post)
    gridcomments = SQLFORM.grid(db.comm)
    gridauth = SQLFORM.grid(db.auth_user)
    gridtasks = SQLFORM.grid(db.task)
    return locals()

@auth.requires_login()
def delete_post():
    post_id = request.args(0,cast=int)
    post = db.post(post_id)
    if post:
         post_category_name = db(db.category.id == post.category).select().first()["category.name"]
         session.post_category_name = post_category_name
    else:
         return ( redirect(URL('list_posts_by_votes', args=session.post_category_name)))

    if auth.user and post and auth.user.id == post.created_by:
        deleted = db(db.post.id == post_id).delete()
        session.flash = 'Post Deleted'
        if request.env.HTTP_REFERER and request.env.HTTP_REFERER.find('stories')!=-1:
            return ( redirect(request.env.HTTP_REFERER) )
        else:
            return ( redirect(URL('list_posts_by_votes', args=post_category_name)))

    session.flash = 'Authorization Failed'
    return (redirect(URL('view_post', args=post.id-1)))

@auth.requires_login()
def delete_post_image():
    post_id = request.args(0,cast=int)
    post = db.post(post_id)
    if auth.user.id==post.created_by and post.image:
        result = delete_file(post, 'image')
        if result:
            session.flash = 'Image removed'
    elif not post.image:
        session.flash = 'Image already removed'
    else:
        session.flash = 'Authorization Failed'
    return (redirect(URL('view_post', args=post.id)))


@auth.requires_login()
def delete_comment_image():
    comment_id = request.args(0,cast=int)
    comment = db.comm(comment_id)
    if auth.user.id==comment.created_by:
        result = delete_file(comment, 'image')
        if result:
            session.flash = 'Image removed'
    else:
        session.flash = 'Authorization Failed'
    return (redirect(URL('view_post', args=comment.post)))


@auth.requires_login()
def delete_comment():
    comment_id = request.args(0,cast=int)
    comment = db.comm(comment_id)
    if auth.user and comment and auth.user.id == comment.created_by:
        deleted = db(db.comm.id == comment_id).delete()
        session.flash = 'Comment Deleted'
    else:
        session.flash = 'Authorization Failed'
    return (redirect(URL('view_post', args=comment.post)))

# @auth.requires_login()
# def deletec():
#     comm_id = request.args(0,cast=int)
#     comm = db.comm(comm_id)
#     if auth.user and comm and auth.user.id == comm.created_by:
#         deleted = db(db.comm.id == comm_id).delete()
#         if deleted:
#             session.flash = 'Post Deleted'
#             return (redirect(URL('view_post', args=comm.id-1)))
#         else:
#             session.flash = 'Unable to delete the post'
#
#     session.flash = 'Authorization Failed'
#     return (redirect(URL('view_post', args=comm.id-1)))


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


def delete_file(row, uploadfield):
    import os
    UPLOADSFOLDER='uploads'
    file = row[uploadfield]
    os.remove(os.path.join(request.folder, UPLOADSFOLDER, file))
    result = row.update_record(**{uploadfield: None})
    if type(row)==type(result):
        return 1
    else:
        return 0

def test_form():
    form = SQLFORM(db.temp_table).process()
    return locals()
