db.define_table('board',
    Field('title', 'string', required=True),
    Field('created_on', 'datetime', default=request.now),
    Field('created_by', 'reference auth_user', default=auth.user_id)

)

db.define_table('board_posts',
    Field('board_id', 'reference board', readable=False, writable=False),
    Field('title', 'string', required=True),
    Field('body', 'text', required=True),
    Field('created_on', 'datetime', default=request.now),
    Field('created_by', 'reference auth_user', default=auth.user_id)
)

db.board.title.requires = IS_NOT_IN_DB(db, 'board.title')
db.board.created_by.readable = db.board.created_by.writable = False
db.board.created_on.readable = db.board.created_on.writable = False
db.board.id.readable = db.board.id.writable = False



db.board_posts.title.requires = IS_NOT_IN_DB(db, 'board_posts.title')
db.board_posts.title.requires = IS_NOT_EMPTY()
db.board_posts.body.requires = IS_NOT_EMPTY()
db.board_posts.created_by.readable = db.board_posts.created_by.writable = False
db.board_posts.created_on.readable = db.board_posts.created_on.writable = False
db.board_posts.id.readable = db.board_posts.id.writable = False
