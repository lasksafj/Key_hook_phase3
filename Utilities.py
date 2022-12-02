import getpass
import pymongo
from bson import DBRef
from pymongo import MongoClient

cluster = 'mongodb+srv://cecs323:123qwe@cluster0.zk708nj.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cluster)
db = client.demo_database

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




class Utilities:
    """I have several variations on a theme in this project, and each one will need to start up
    with the same MongoDB database.  So I'm putting any sort of random little utilities in here
    as I need them.

    startup - creates the connection and returns the database client."""

    @staticmethod
    def startup():
        cluster = 'mongodb+srv://cecs323:123qwe@cluster0.zk708nj.mongodb.net/?retryWrites=true&w=majority'
        client = MongoClient(cluster)
        db = client.demo_database
        return db

    """Return the size document for the given name."""

    @staticmethod
    def get_section(db, department_name, course_name, section_number, semester, year):
        result = db.sections.find_one({
            "department_name": department_name,
            "course_name": course_name,
            "section_number": section_number,
            "semester": semester,
            "year": year
        })['_id']
        return result

    @staticmethod
    def enroll(db, section_id, student_id, grade):
        db.enrollments.insert_one({
            'section': DBRef('sections', section_id),
            'student': DBRef('students', student_id),
            'grade': grade
        })
