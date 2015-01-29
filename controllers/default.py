# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index2():
    """
    This index appears when you go to bboard/default/index . 
    """
    # We want to generate an index of the posts. 
    posts = db().select(db.bboard.ALL)
    return dict(posts=posts)

@auth.requires_login()
def add():
    """Add a post."""
    form = SQLFORM(db.bboard)
    if form.process().accepted:
        # Successful processing.
        session.flash = T("inserted")
        redirect(URL('default', 'index'))
    return dict(form=form)
    
def view():
    """View a post."""
    # p = db(db.bboard.id == request.args(0)).select().first()
    p = db.bboard(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.bboard, record = p, readonly = True, upload = URL('download'))
    
    # p.name would contain the name of the poster.
    return dict(form=form)

@auth.requires_login()
def edit():
    """View a post."""
    # p = db(db.bboard.id == request.args(0)).select().first()
    p = db.bboard(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('Not authorized.')
        redirect(URL('default', 'index'))
    form = SQLFORM(db.bboard, record=p)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'view', args=[p.id]))
    # p.name would contain the name of the poster.
    return dict(form=form)

@auth.requires_login()
@auth.requires_signature()
def delete():
    """Deletes a post."""
    p = db.bboard(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('Not authorized')
        redirect(URL('default', 'index'))
    confirm = FORM.confirm('Delete listing')
    form = SQLFORM(db.bboard, record = p, readonly = True, upload = URL('download'))
    if confirm.accepted:
        db(db.bboard.id == p.id).delete()
        session.flash = T('Listing deleted')
        redirect(URL('default', 'index'))

    return dict(form=form, confirm=confirm)

@auth.requires_login()
@auth.requires_signature()
def toggle_sold():
     item = db.bboard(request.args(0)) or redirect(URL('default', 'index'))
     item.update_record(sold = not item.sold) 
     redirect(URL('default', 'index')) # Assuming this is where you want to go

def index():
    """Better index."""
    # Let's get all data. 
    show_all = request.args(0) == 'all'
    #q = db.bboard
    q = (db.bboard) if show_all else (db.bboard.sold == False)
    #image = db.bboard.image(request.args(0,cast=int)) or redirect(URL('index'))

    def generate_del_button(row):
        # If the record is ours, we can delete it.
        b = ''
        if auth.user_id == row.user_id:
            b = A('Delete', _class='btn', _href=URL('default', 'delete', args=[row.id], user_signature=True))
        return b
    
    def generate_edit_button(row):
        # If the record is ours, we can delete it.
        b = ''
        if auth.user_id == row.user_id:
            b = A('Edit', _class='btn', _href=URL('default', 'edit', args=[row.id]))
        return b
    
    def generate_sold_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Sold', _class='btn', _href=URL('default', 'toggle_sold', args=[row.id], user_signature=True))
        return b

    def shorten_post(row):
        return row.bbmessage[:10] + '...'
    
    # Creates extra buttons.
    
    links = [
        dict(header='', body = generate_del_button),
        dict(header='', body = generate_edit_button),
        dict(header='', body = generate_sold_button),
        ]

    if len(request.args) == 0:
        # We are in the main index.
        links.append(dict(header='Post', body = shorten_post))
        db.bboard.bbmessage.readable = False

    start_idx = 1 if show_all else 0
    form = SQLFORM.grid(q,
        args=request.args[:start_idx],
        fields=[db.bboard.category,
                db.bboard.title,
                db.bboard.sold,
                db.bboard.date_posted,
                db.bboard.user_id,        
                db.bboard.bbmessage, 
                ],
        links=links,
        editable=False,
        deletable=False,
        )

    if show_all:
        button = A('See unsold', _class='btn', _href=URL('default', 'index'))
    else:
        button = A('See all', _class='btn', _href=URL('default', 'index', args=['all']))

    return dict(form=form, button=button)

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


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
