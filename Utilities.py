import getpass
import json

import pymongo
from bson import DBRef
from pymongo import MongoClient
from datetime import datetime

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
            'required': ["employee_id", "name"],
            'additionalProperties': False,
            'properties': {
                '_id': {},
                'employee_id': {
                    'bsonType': "string",
                },
                'name': {
                    'bsonType': "string",
                },
            }
        }
    }
}
db.command('collMod', 'employees', **employees_validator)

db.buildings.create_index([
    ("name", pymongo.ASCENDING),
], unique=True)

db.employees.create_index([
    ("employee_id", pymongo.ASCENDING),
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
    ("loan", pymongo.ASCENDING),
], unique=True)

try:
    db.validate_collection("counters")
except pymongo.errors.OperationFailure:
    db.create_collection("counters")
    db.counters.insert_one({
        "_id": "key_number",
        "seq": 1
    })


def get_next_sequence(name):
    return db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}}
    )['seq']


def room_employee_can_enter(employee):
    requests = db.requests.find({
        'employee': DBRef('employees', employee['_id'])
    })
    res = []
    for request in requests:
        loan_id = db.loan.find_one({
            'request': DBRef('requests', request['_id'])
        })['_id']
        a = db.returns.find_one({
            'loan': DBRef('loan', loan_id),
        }, {"_id": 1})
        if not a:
            room = db.dereference(request['room'])
            # building = db.dereference(room['building'])
            res.append(room)
    return res


def find_hook(hook_number):
    try:
        hook = db.hooks.find_one({
            "number": hook_number,
        })
        hook_id = hook['_id']
    except TypeError:
        print('Hook does not exist')
        return None
    return hook


def find_building(building_name):
    try:
        building = db.buildings.find_one({
            "name": building_name,
        })
        building_id = building['_id']
    except TypeError:
        print('Building does not exist')
        return None
    return building


def find_room(building_name, room_number):
    building = find_building(building_name)
    if not building:
        return None
    try:
        room = db.rooms.find_one({
            "building": DBRef('buildings', building['_id']),
            'number': room_number,
        })
        room_id = room['_id']
    except TypeError:
        print('Room does not exist')
        return None
    return room


def find_door(building_name, room_number, door_name):
    room = find_room(building_name, room_number)
    if not room:
        return None
    try:
        door = db.doors.find_one({
            "room": DBRef('rooms', room['_id']),
            'name': door_name,
        })
        door_id = door['_id']
    except TypeError:
        print('Door does not exist')
        return None
    return door


def insert_building(name):
    try:
        db.buildings.insert_one({
            'name': name,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Building already exist')


def insert_room(building_name, number):
    building = find_building(building_name)
    if not building:
        return None
    try:
        db.rooms.insert_one({
            'building': DBRef('buildings', building['_id']),
            'number': number,
        })
    except pymongo.errors.DuplicateKeyError:
        print('Room already exist')


def insert_door(building_name, room_number, name):
    room = find_room(building_name, room_number)
    if not room:
        return
    try:
        db.doors.insert_one({
            'room': DBRef('rooms', room['_id']),
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
    hook = find_hook(hook_number)
    if not hook:
        return None
    door = find_door(building_name, room_number, door_name)
    if not door:
        return None
    try:
        db.hook_door.insert_one({
            'hook': DBRef('hooks', hook['_id']),
            'door': DBRef('doors', door['_id'])
        })
    except pymongo.errors.DuplicateKeyError:
        print('The hook already open the door')


def insert_key(hook_number, key_number):
    hook = find_hook(hook_number)
    if not hook:
        return None
    try:
        db.keys.insert_one({
            'hook': DBRef('hooks', hook['_id']),
            'number': key_number
        })
    except pymongo.errors.DuplicateKeyError:
        print('Key already exist')


def find_key(key_number):
    try:
        key = db.keys.find_one({
            'number': key_number
        })
        key_id = key['_id']
    except TypeError:
        print('Key does not exist')
        return None
    return key


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
        employee = db.employees.find_one({
            'employee_id': employee_id
        })
        eid = employee['_id']
    except TypeError:
        print('Employee does not exist')
        return None
    return employee


def insert_request(employee_id, building_name, room_number):
    request_time = datetime.now()

    employee = find_employee(employee_id)
    if not employee:
        return None
    room = find_room(building_name, room_number)
    if not room:
        return None
    if room in room_employee_can_enter(employee):
        print(employee['name'], 'already has access to the room')
        return

    doors = []
    for door in db.doors.find({'room': DBRef('rooms', room['_id'])}):
        doors.append(DBRef('doors', door['_id']))

    for key in db.keys.find():
        if db.hook_door.find_one({'hook': key['hook'], 'door': {'$in': doors}}):
            loans = list(db.loan.find({'key': DBRef('keys', key['_id'])}))
            if not loans:
                request = db.requests.insert_one({
                    'employee': DBRef('employees', employee['_id']),
                    'room': DBRef('rooms', room['_id']),
                    'request_time': request_time,
                })
                request_id = request.inserted_id
                loan = db.loan.insert_one({
                    'key': DBRef('keys', key['_id']),
                    'request': DBRef('requests', request_id)
                })
                return [request_id, loan.inserted_id]
            for lo in loans:
                if db.returns.find_one({
                    'loan': DBRef('loan', lo['_id']),
                    '$and': [
                        {'return_time': {'$gt': db.dereference(lo['request'])['request_time']}},
                        {'loss': False}
                    ]
                }) is None:
                    request = db.requests.insert_one({
                        'employee': DBRef('employees', employee['_id']),
                        'room': DBRef('rooms', room['_id']),
                        'request_time': request_time,
                    })
                    request_id = request.inserted_id
                    loan = db.loan.insert_one({
                        'key': DBRef('keys', key['_id']),
                        'request': DBRef('requests', request_id)
                    })
                    return [request_id, loan.inserted_id]

    print('There is no key available')
    return None


def key_employee_hold(employee):
    res = []
    for req in db.requests.find({'employee': DBRef('employees', employee['_id'])}):
        lo = db.loan.find_one({'request': DBRef('requests', req['_id'])})
        if db.returns.find_one({
            'loan': DBRef('loan', lo['_id']),
        }) is None:
            res.append(db.dereference(lo['key']))
    return res


def insert_return(employee_id, key_number, loss):
    employee = find_employee(employee_id)
    if not employee:
        return None
    key = find_key(key_number)
    if not key:
        return None
    for lo in db.loan.find({'key': DBRef('keys', key['_id'])}):
        if db.dereference(db.dereference(lo['request'])['employee']) == employee \
                and db.returns.find_one({'loan': DBRef('loan', lo['_id'])}, {"_id": 1}) is None:
            return db.returns.insert_one({
                'loan': DBRef('loan', lo['_id']),
                'loss': loss,
                'return_time': datetime.now()
            })
    print('Invalid key number')


def prompt_room():
    rooms = list(db.rooms.find())
    if not rooms:
        print('There is no room in database')
        return None
    print('Rooms in database: ',
          ', '.join([db.dereference(r['building'])['name'] + ' ' + str(r['number']) for r in rooms]))
    try:
        building_name, room_number = input('Enter building and room: ').split()
    except ValueError:
        print('Invalid input')
        return None
    try:
        room_number = int(room_number)
    except ValueError:
        print('Invalid room number')
        return None
    return find_room(building_name, room_number)


def prompt_employee():
    employees = list(db.employees.find())
    if not employees:
        print('There is no employee in database')
        return None
    print('Employees in database: ',
          ', '.join([str(e['name']) + '(' + e['employee_id'] + ')' for e in employees]))
    employee_id = input('Which employee (enter employee id): ')
    return find_employee(employee_id)


def prompt_hook():
    hooks = list(db.hooks.find())
    if not hooks:
        print('There is no hook available')
        return None
    print('Hooks in database: ', ', '.join([str(h['number']) for h in hooks]))
    try:
        hook_number = int(input('Which hook you will use to make the key (enter number): '))
    except ValueError:
        print('Invalid hook number')
        return None
    return find_hook(hook_number)


def prompt_door(room):
    building_name, room_number = db.dereference(room['building'])['name'], room['number']
    doors = list(db.doors.find({'room': DBRef('rooms', room['_id'])}))
    if not doors:
        print('There no door for the room in database')
        return None
    print('Doors of', building_name, str(room_number), 'in database: ', ', '.join([d['name'] for d in doors]))
    door_name = input('Which door: ')
    return find_door(building_name, room_number, door_name)


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
