# ===========================================================================
# Creates a database to store posts for student life
db.define_table('blog_post',
                Field('title', requires=IS_NOT_EMPTY()),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)

# Creates a database to store comments for posts in student life
db.define_table('blog_comment_sl',
                Field('blog_post', 'reference blog_post'),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)
# ===========================================================================


# ===========================================================================
# Creates a database to store posts for sports
db.define_table('blog_post_s',
                Field('title', requires=IS_NOT_EMPTY()),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)

# Creates a database to store comments for posts in sports
db.define_table('blog_comment_s',
                Field('blog_post_s', 'reference blog_post_s'),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)
# ===========================================================================


# ===========================================================================
# Creates a database to store posts for events
db.define_table('blog_post_e',
                Field('title', requires=IS_NOT_EMPTY()),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)

# Creates a database to store comments for posts in events
db.define_table('blog_comment_e',
                Field('blog_post_e', 'reference blog_post_e'),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)
# ===========================================================================