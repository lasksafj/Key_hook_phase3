import getpass
import pymongo
from bson import DBRef
from pymongo import MongoClient

cluster = 'mongodb+srv://cecs323:123qwe@cluster0.zk708nj.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cluster)
db = client.key_hook

buildings_validator = {
    'validator': {
        '$jsonSchema': {
            'bsonType': "object",
            'required': ["name"],
            'additionalProperties': False,
            'properties': {
                '_id': {},
                'name': {
                    'bsonType': "string",
                },
            }
        }
    }
}
db.command('collMod', 'buildings', **buildings_validator)

employees_validator = {
    'validator': {
        '$jsonSchema': {
            'bsonType': "object",
            'required': ["name"],
            'additionalProperties': False,
            'properties': {
                '_id': {},
                'name': {
                    'bsonType': "string",
                },
            }
        }
    }
}
db.command('collMod', 'employees', **buildings_validator)

db.buildings.create_index([
    ("name", pymongo.ASCENDING),
], unique=True)

db.rooms.create_index([
    ("building", pymongo.ASCENDING),
    ("number", pymongo.ASCENDING),
], unique=True)

db.doors.create_index([
    ("room", pymongo.ASCENDING),
    ("name", pymongo.ASCENDING),
], unique=True)

db.hook_door.create_index([
    ("hook", pymongo.ASCENDING),
    ("door", pymongo.ASCENDING),
], unique=True)

db.hooks.create_index([
    ("number", pymongo.ASCENDING),
], unique=True)

db.keys.create_index([
    ("number", pymongo.ASCENDING),
], unique=True)

db.requests.create_index([
    ("employee", pymongo.ASCENDING),
    ("room", pymongo.ASCENDING),
    ("request_time", pymongo.ASCENDING)
], unique=True)

db.loan.create_index([
    ("request", pymongo.ASCENDING),
], unique=True)

db.returns.create_index([
    ("request", pymongo.ASCENDING),
], unique=True)


def find_hook(hook_number):
    try:
        hook_id = db.hooks.find_one({
            "number": hook_number,
        })['_id']
    except TypeError:
        print('Hook does not exist')
        return None
    return hook_id


def find_building(building_name):
    try:
        building_id = db.buildings.find_one({
            "name": building_name,
        })['_id']
    except TypeError:
        print('Building does not exist')
        return None
    return building_id


def find_room(building_name, room_number):
    building_id = find_building(building_name)
    if not building_id:
        return None
    try:
        room_id = db.rooms.find_one({
            "building": DBRef('buildings', building_id),
            'number': room_number,
        })['_id']
    except TypeError:
        print('Room does not exist')
        return None
    return room_id


def find_door(building_name, room_number, door_name):
    room_id = find_room(building_name, room_number)
    if not room_id:
        return None
    try:
        door_id = db.doors.find_one({
            "room": DBRef('rooms', room_id),
            'name': door_name,
        })['_id']
    except TypeError:
        print('Door does not exist')
        return None
    return door_id


def insert_building(name):
    try:
        db.buildings.insert_one({
            'name': name,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Building already exist')


def insert_room(building_name, number):
    building_id = find_building(building_name)
    if not building_id:
        return None
    try:
        db.rooms.insert_one({
            'building': DBRef('buildings', building_id),
            'number': number,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Room already exist')


def insert_door(building_name, room_number, name):
    room_id = find_room(building_name, room_number)
    if not room_id:
        return
    try:
        db.doors.insert_one({
            'room': DBRef('rooms', room_id),
            'name': name,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Door already exist')


def insert_hook(number):
    try:
        db.hooks.insert_one({
            'number': number
        })
    except pymongo.errors.DuplicateKeyError:
        print('Hook already exist')


def insert_hook_door(hook_number, building_name, room_number, door_name):
    hook_id = find_hook(hook_number)
    if not hook_id:
        return None
    door_id = find_door(building_name, room_number, door_name)
    if not door_id:
        return None
    try:
        db.hook_door.insert_one({
            'hook': DBRef('hooks', hook_id),
            'door': DBRef('doors', door_id)
        })
    except pymongo.errors.DuplicateKeyError:
        print('The hook already open the door')


def insert_key(hook_number, key_number):
    hook_id = find_hook(hook_number)
    try:
        db.keys.insert_one({
            'hook': DBRef('hooks', hook_id),
            'number': key_number
        })
    except pymongo.errors.DuplicateKeyError:
        print('Key already exist')


def find_key(key_number):
    try:
        key_id = db.keys.find_one({
            'number': key_number
        })
    except TypeError:
        print('Key does not exist')
        return None
    return key_id


def insert_employee(employee_id, name):
    try:
        db.employees.insert_one({
            'employee_id': employee_id,
            'name': name,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Employee already exist')


def find_employee(employee_id):
    try:
        eid = db.employees.find_one({
            'employee_id': employee_id
        })
    except TypeError:
        print('Employee does not exist')
        return None
    return eid


def insert_request(employee_id, building_name, room_number, request_time):
    eid = find_employee(employee_id)
    if not eid:
        return None
    room_id = find_room(building_name, room_number)
    if not room_id:
        return None
    try:
        db.requests.insert_one({
            'employee': DBRef('employees,', eid),
            'room': DBRef('rooms', room_id),
            'request_time': request_time,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Request already exist')

# class Utilities:
#     """I have several variations on a theme in this project, and each one will need to start up
#     with the same MongoDB database.  So I'm putting any sort of random little utilities in here
#     as I need them.
#
#     startup - creates the connection and returns the database client."""
#
#     @staticmethod
#     def startup():
#         cluster = 'mongodb+srv://cecs323:123qwe@cluster0.zk708nj.mongodb.net/?retryWrites=true&w=majority'
#         client = MongoClient(cluster)
#         db = client.demo_database
#         return db
#
#     """Return the size document for the given name."""
#
#     @staticmethod
#     def get_section(db, department_name, course_name, section_number, semester, year):
#         result = db.sections.find_one({
#             "department_name": department_name,
#             "course_name": course_name,
#             "section_number": section_number,
#             "semester": semester,
#             "year": year
#         })['_id']
#         return result
#
#     @staticmethod
#     def enroll(db, section_id, student_id, grade):
#         db.enrollments.insert_one({
#             'section': DBRef('sections', section_id),
#             'student': DBRef('students', student_id),
#             'grade': grade
#         })
