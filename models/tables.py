# -*- coding: utf-8 -*-
from datetime import datetime

def get_first_name():
    name = 'Nobody'
    if auth.user:
        name = auth.user.first_name
    return name

def get_email():
    email = ''
    if auth.user:
        email = auth.user.email
    return email
    
CATEGORY = ['Car',
            'Bike',
            'Books',
            'Music',
            'Outdoors',
            'For the House',
            'Misc.']

db.define_table('bboard',
                Field('name'),
                Field('user_id', db.auth_user),
                Field('phone'),
                Field('email'),
                Field('category'),
                Field('date_posted', 'datetime'),
                Field('title'),
                Field('price'),
                Field('sold', 'boolean'),
                Field('image', 'upload'),
                Field('bbmessage', 'text'),
                )


db.bboard.id.readable = False
db.bboard.bbmessage.label = 'Message'
db.bboard.name.default = get_first_name()
db.bboard.date_posted.default = datetime.utcnow()
db.bboard.name.writable = False
db.bboard.date_posted.writable = False
db.bboard.user_id.default = auth.user_id
db.bboard.user_id.writable = db.bboard.user_id.readable = False
db.bboard.email.default = get_email()
db.bboard.email.writable = False
db.bboard.category.requires = IS_IN_SET(CATEGORY, zero = None)
db.bboard.category.default = 'Misc.'
db.bboard.category.required = True
db.bboard.sold.default = False
db.bboard.phone.requires = IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',
                                    error_message='not a phone number')
#db.bboard.image.readable = False                     
