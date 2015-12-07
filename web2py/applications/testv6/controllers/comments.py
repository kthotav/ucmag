#*- coding: utf-8 -*-
import json

def Widget():
    """ Returns Ractive comment widget
    """
    response.delimiters = ['{%', '%}']
    response.view = 'comments/comment_widget.html'
    return {
        'no_auth_link': A("login to comment", _href=URL('default', 'user', 'login', vars=dict(_next=URL(args=request.args))))
    }


def CommentsJson():
    """ Returns comments list into json format
        for selecting post
    """
    id = request.args(0, cast=int)
    # Display the post, but also display the comments associated with that post. If the
    # post doesn't exist, redirect to the home page.
    post = db.post(id) or redirect(URL('index'))
    comments = db(db.comm.post==post.id).select(
        db.auth_user.first_name,
        db.auth_user.last_name,
        *db.comm,
        join=db.comm.on(
            db.auth_user.id==db.comm.created_by
        ),
        orderby=db.comm.created_on
    )
    if auth.is_logged_in():
        auth.user.authorized = True
        user = auth.user.as_json()
    else:
        user = json.dumps({'authorized': False})
    return 'app.commentData=%s;app.user=%s' % (comments.as_json(), user)


@request.restful()
def api():
    """ Comments CRUD api
    """
    response.view = 'generic.json'
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.statusarser.error)

    def POST(table_name,**vars):
        comment = db[table_name].validate_and_insert(**vars)
        return comment.as_dict()

    def PUT(table_name,record_id,**vars):
        return db(db[table_name]._id==record_id).update(**vars)

    def DELETE(table_name,record_id):
        return db(db[table_name]._id==record_id).delete()

    return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)
