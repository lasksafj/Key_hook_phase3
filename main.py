import pymongo
from bson import DBRef
from pymongo import MongoClient

from Utilities import Utilities

if __name__ == '__main__':
    cluster = 'mongodb+srv://cecs323:123qwe@cluster0.zk708nj.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(cluster)
    db = client.intro_hw
    enrollments = db.enrollments
    sections = db.sections
    students = db.students
    enrollments.delete_many({})
    sections.delete_many({})
    students.delete_many({})

    section_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'required': ["department_name", "course_name", "section_number", "semester", "year"],
                'additionalProperties': False,
                'properties': {
                    '_id': {},
                    'department_name': {
                        'bsonType': "string",
                    },
                    'course_name': {
                        'bsonType': "string",
                    },
                    'section_number': {
                        'bsonType': "int",
                    },
                    'semester': {
                        'bsonType': "string",
                    },
                    'year': {
                        'bsonType': "int",
                    },
                }
            }
        }
    }
    db.command('collMod', 'sections', **section_validator)

    student_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'required': ["last_name", "first_name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {},
                    'last_name': {
                        'bsonType': "string",
                    },
                    'first_name': {
                        'bsonType': "string",
                    },
                }
            }
        }
    }
    db.command('collMod', 'students', **student_validator)

    enrollments.create_index([
        ("section", pymongo.ASCENDING),
        ("student", pymongo.ASCENDING)
    ], unique=True)
    # db.command('collMod', 'enrollments', validationLevel='off')

    sections.create_index([
        ("department_name", pymongo.ASCENDING),
        ("course_name", pymongo.ASCENDING),
        ("section_number", pymongo.ASCENDING),
        ("semester", pymongo.ASCENDING),
        ("year", pymongo.ASCENDING),
    ], unique=True)

    result_section1 = sections.insert_one({
        'department_name': 'CECS',
        'course_name': '323',
        'section_number': 3,
        'semester': 'Fall',
        'year': 2022,
    })
    result_section2 = sections.insert_one({
        'department_name': 'CECS',
        'course_name': '323',
        'section_number': 3,
        'semester': 'Fall',
        'year': 2021,
    })

    result_student = students.insert_many([
        {'last_name': 'Nguyen', 'first_name': 'Nhat', '_id': '1111'},
        {'last_name': 'Truong', 'first_name': 'Toan', '_id': '2222'},
        {'last_name': 'Tran', 'first_name': 'Quy', '_id': '3333'},
    ])

    Utilities.enroll(db,
                     section_id=Utilities.get_section(db, 'CECS', '323', 3, 'Fall', 2022),
                     student_id='1111', grade='3.5')
    Utilities.enroll(db,
                     section_id=Utilities.get_section(db, 'CECS', '323', 3, 'Fall', 2022),
                     student_id='2222', grade='3.5')
    Utilities.enroll(db,
                     section_id=Utilities.get_section(db, 'CECS', '323', 3, 'Fall', 2022),
                     student_id='3333', grade='3.5')


    def print_student(db, student):
        print("Name: ", student["first_name"], student["last_name"], 'enrolls in ')
        enrollments = db.enrollments.find({"student": DBRef("students", student["_id"])})
        for enrollment in enrollments:
            ref_section = db.dereference(enrollment["section"])
            print(ref_section['department_name'], ref_section['course_name'], ref_section['section_number'], end=', ')
        print()

    def print_section(db, section):
        print("Students enroll in ", section["department_name"], section["course_name"], section['section_number'])
        enrollments = db.enrollments.find({"section": DBRef("sections", section["_id"])})
        for enrollment in enrollments:
            ref_student = db.dereference(enrollment["student"])
            print(ref_student['first_name'], ref_student['last_name'], ref_student['_id'], end=', ')
        print()

    student1 = students.find_one({'first_name': 'Nhat', 'last_name': 'Nguyen'})
    print_student(db, student1)
    section1 = sections.find_one({
        'department_name': 'CECS',
        'course_name': '323',
        'section_number': 3,
        'semester': 'Fall',
        'year': 2022,
    })
    print_section(db, section1)
