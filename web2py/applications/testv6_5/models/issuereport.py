# The following is a database for our issue-reporting tool/system that users
# can utilize to report bugs, issues, and other concerns.

# All possible status options.
STATUSES = ('Assigned', 'Accepted', 'Completed', 'Reassigned', 'Rejected')

# Table for assigning a task to a specific user. Assigning a task
# requires the title of the task, a description of it, what it is
# assigned to (Bug Fix, Questions or Concerns, Other Issues),
# and the status of the task which will be "Assigned" by default.
# The people behind "Bug Fix, Questions or Concerns, Other Issues"
# will be responsible for changing the status of the task based upon
# whether the task is accepted, completed, reassigned, or rejected.
# This will help the admins keep track of what the issues are,
# whether or not the issues are being fixed, and who is working
# on them. Logged in users can create/edit/delete their own tasks
# and assignees can change the status to reflect changes in the
# task progress.
db.define_table('task',
                Field('title', requires=IS_NOT_EMPTY()),
                Field('description', 'text', requires=IS_NOT_EMPTY()),
                Field('assigned_to', 'reference auth_user'),
                Field('status', requires=IS_IN_SET(STATUSES), default=STATUSES[0]),

                auth.signature)

# Adds a table db.task_archive which keeps track of all changes
# happening to a task. This db is located in the database
# administration section in appadmin. Every time changes are
# made in db.task, it is archived into db.task_archive.
auth.enable_record_versioning(db)

# Definition for fullname which is primarily being used in
# view_task. It is used to display a user's full name.
def fullname(user_id):
    if user_id is None:
        return "Unknown"
    return "%(first_name)s %(last_name)s (id:%(id)s)" % db.auth_user(user_id)

def show_status(status, row=None):
    return SPAN(status, _class=status)

db.task.status.represent = show_status

db.task.created_on.represent = lambda v, row: prettydate(v)

########################## EMAIL CONFIGURATION: IGNORE/EXPERIMENTAL ##########################

# def send_pending_emails():
#     rows = db(db.email.status=='pending').select()
#     for row in rows:
#         send_email_realtime()
#
# def send_email_deferred(to, subject, message, sender):
#     if not isinstance(to, list): to = [to]
#     db.email.insert(to=to, subject=subject, message=message, sender=sender, status='pending')
#
#
def send_email(to, subject, message, sender):
    if not isinstance(to, list): to= [to]
    #if auth.user: to=[email for email in to if not to == auth.user.email]
    mail.settings.sender = auth.user.email
    mail.send(to=to, subject=subject, message=message or '(No Message)')

    # if EMAIL_POLICY == 'realtime':
    #     send_email_realtime(to, subject, message, sender)
    # else:
    #     send_email_deferred(to, subject, message, sender)

