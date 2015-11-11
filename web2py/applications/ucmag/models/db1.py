# This is a table called 'category' which defines a bunch of names for categories. We use this table to make
# categories such as Student Life, Sports, and Events. You won't be able to create a category that already
# exists. It can also not contain special characters (IS_SLUG). The URL cannot be lowercase.
db.define_table('category',
                Field('name', requires=(IS_SLUG(), IS_LOWER(), IS_NOT_IN_DB(db, 'category.name'))))

# This table called 'post' is responsible for defining what a post is. A post will belong to a specific
# category and it will reference that category. The category field for the post can't be readable or
# writable because we want the users to be able to make a post in a given category such as Student Life,
# Sports, or Events, but we don't want them to be able to change the name of that category. A post will
# also need to have a title and a body of text. We don't want either of these to be empty. If one or more
# of those fields is empty, the form will throw an error. A post will also have a number of votes. Users
# cannot see these votes when they are viewing a post and we don't want them to be able to edit the number
# of votes. Since we are also adding in an auth.signature, we are adding in 5 more fields that hold
# references to the logged in user who posted the specific post. These fields include created_by, modified_by,
# created_on, modified_on, and is_active. We do not use is_active.
db.define_table('post',
                Field('category', 'reference category', writable=False, readable=False),
                Field('title', 'string', requires=IS_NOT_EMPTY()),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                Field('votes', 'integer', default=0, writable=False, readable=False),
                Field('image', 'upload', autodelete=True,
                       requires=[IS_EMPTY_OR(IS_IMAGE(error_message="Please choose a valid image")),
                                 IS_LENGTH(5*1024*1024, error_message="Please upload an image within the 5 mb limit")] ),
                auth.signature)

# This table called 'vote' defines what a vote is. A vote references a specific post and carries a score
# that is defined as an integer. We need a table for votes because we want to prevent users from voting
# more than once. As such, we want to know which post a vote belongs to as well as keep track of who
# voted. In other words, when someone votes, the associated vote counter belonging to a specific post
# goes up by one and this vote is associated to the voter so it prevents them from voting more than once.
# It is important to keep track of a user's vote since a voter might want to change their mind.
db.define_table('vote',
                # Each vote references a specific post.
                Field('post', 'reference post'),
                # Score is represented as an int and increments by 1.
                Field('score', 'integer', default=+1),
                auth.signature)

# This table 'comm' defines what a comment is to a post. When a user comments, their comment will be
# associated to a particular post which explains the post reference. We don't want this post reference
# to be readable since there's no need. We also don't want it to be writable because it would not make
# sense to allow the user to change the name of the post to which they are commenting. This is a big
# security issue. The table has also been defined so that users are associated to the comments that they
# make. The field 'parent_comm' allows users to respond to another comment and it references 'post_com'
# since it is essentially a response to another comment. We have also associated votes to comments.
db.define_table('comm',
                # Each comment holds a reference to a specific post
                Field('post', 'reference post', writable=False, readable=False),
                Field('parent_comm', 'reference comm', writable=False, readable=False),
                Field('votes', 'integer', default=0, writable=False, readable=False),
                Field('body', 'text'),
                Field('image', 'upload', autodelete=True,
                       requires=[IS_EMPTY_OR(IS_IMAGE(error_message="Please choose a valid image")),
                                 IS_LENGTH(5*1024*1024, error_message="Please upload an image within the 5 mb limit")]),
                auth.signature)

db.define_table('temp_table',
                Field('title', 'string', requires=IS_NOT_EMPTY()),
                Field('image', 'upload', autodelete=True,
                       requires=[IS_EMPTY_OR(IS_IMAGE(error_message="Please choose a valid image")),
                                 IS_LENGTH(5*1024*1024, error_message="Please upload an image within the 5 mb limit")]),
               )


# This table 'comm_vote' will record the number of votes that are in each comment. As such, we will need
# to ensure that 'comm' is referenced. We must also keep track of who is voting to ensure that users
# do not vote more than once.
db.define_table('comm_vote',
                # Every comment vote will reference a specific comment to a post.
                Field('comm', 'reference comm'),
                # Score is represented as an int and increments by one.
                Field('score', 'integer', default=+1),
                auth.signature)

# Experimental. We made a function for identifying a user's name
# given the id. In the early stages of development, we populated
# the database through a script that flooded it with blank ids
# and when we attempted to access those posts, it would crash.
# This is why we implemented the "if id is None" loop to prevent
# internal errors. This is also in place so that if we decide to
# ban/delete users, their lack of existence in the database will
# not crash our system.
def author(id):
    if id is None:
        return "Unknown"
    else:
        user = db.auth_user(id)
        return A('%(first_name)s %(last_name)s' % user, args=user.id)

# This is the script we used to populate our users, posts, and comments
# to test out how a fully populated system might look like.

## Database population script
# from gluon.contrib.populate import populate
# if db(db.auth_user).count()<5:
#     populate(db.auth_user, 100)
#     db.commit()
#
# if db(db.post).count()<5:
#     populate(db.post, 500)
#     db.commit()
#
# if db(db.comm).count()<5:
#     populate(db.comm, 1000)
#     db.commit()
