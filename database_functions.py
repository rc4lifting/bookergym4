import firebase_admin
import asyncio

from firebase_admin import db, credentials
from datetime import datetime

import caches

cred = credentials.Certificate(caches.firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': caches.firebase_database_url
})

## basic CRUD operations
def create_data(path, data, is_push=False):
    ref = db.reference(path)
    if is_push:
        ref.push(data)
    else:
        ref.set(data)

def read_data(path: str) -> dict:
    ref = db.reference(path)
    data = ref.get()

    return data

# update entire directory - dictionary
def update_data(path: str, data: dict):
    ref = db.reference(path)
    ref.update(data)

# update particular field 
def set_data(path: str, data):
    ref = db.reference(path)
    try:
        ref.set(data)
    except TypeError:
        print("data is not json-serializable")

def delete_data(path: str):
    ref = db.reference(path)
    ref.delete()    

## helper functions 
def data_exists(path: str):
    ref = db.reference(path)
    data = ref.get()
    return data is not None

## specific use case funcitons
# check if user exists
def user_exists(chat_id: str):
    path = f"/users/{chat_id}"
    return data_exists(path)

def get_slots_after_time(curr_time: datetime, chat_id: str):
    path = f"/slots"
    ref = db.reference(path)

    slots = ref.order_by_child('bookedUserId').equal_to(chat_id).get()

    return slots 
