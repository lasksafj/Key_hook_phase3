import pymongo
from bson import DBRef
from pymongo import MongoClient

import Utilities as Util

if __name__ == '__main__':
    # Util.insert_employee('111', 'Nhat Nguyen')
    # Util.insert_building(name='CECS')
    # Util.insert_room('CECS', 123)
    # Util.insert_door('CECSs', 123, 'front')
    # Util.find_employee('111')
    # Util.insert_hook_door(1, 'CECS', 123, 'front')
    # Util.insert_return('111', 1, False)

    db = Util.db

    # a = db.rooms.find_one({
    #     'building': DBRef('buildings', db.buildings.find_one({'name': 'CECS'})['_id']),
    #     'number': {'$gt': 150}
    # }, {"_id": 1})
    # print(a)

    while 1:
        print('-----------------------------------------------------------------')
        if input('Enter \'1\' to continue, else to exist ') != '1':
            break
        print('Menu: choose one')
        print('a. Create a new Key.\n'
              'b. Request access to a given room by a given employee.\n'
              'c. Capture the issue of a key to an employee\n'
              'd. Capture losing a key\n'
              'e. Report out all the rooms that an employee can enter, given the keys that he/she already has.\n'
              'f. Delete a key.\n'
              'g. Delete an employee.\n'
              'h. Add a new door that can be opened by an existing hook.\n'
              'i. Update an access request to move it to a new employee.\n'
              'j. Report out all the employees who can get into a room.')

        choose = input()

        if choose == 'a':
            hooks = list(db.hooks.find())
            if not hooks:
                print('There is no hook available')
                continue
            print('Hooks in database: ', ', '.join([str(h['number']) for h in hooks]))
            print('Which hook you will use to make the key (enter number): ')
            while True:
                hook_number = input()
                try:
                    hook_number = int(hook_number)
                except ValueError:
                    print('Invalid number, choose again')
                    continue
                break
            Util.insert_key(hook_number, Util.get_next_sequence('key_number'))

        elif choose == 'b':
            employees = list(db.employees.find())
            if not employees:
                print('There is no employee in database')
                continue
            rooms = list(db.rooms.find())
            if not rooms:
                print('There is no room in database')
                continue

            print('Employees in database: ',
                  ', '.join([str(e['name']) + '(' + e['employee_id'] + ')' for e in employees]))
            employee_id = input('Which employee (enter employee id): ')

            print('Rooms in database: ',
                  ', '.join([db.dereference(r['building'])['name'] + ' ' + str(r['number']) for r in rooms]))
            building_name, room_number = input('Enter building and room: ').split()
            try:
                room_number = int(room_number)
            except ValueError:
                print('Invalid room number')

            Util.insert_request(employee_id, building_name, room_number)

        elif choose == 'c':
            pass

        elif choose == 'd':
            employees = list(db.employees.find())
            print('Employees in database: ',
                  ', '.join([e['name'] + '(' + e['employee_id'] + ')' for e in employees]))
            employee_id = input('Which employee (enter employee id): ')
            employee = Util.find_employee(employee_id)
            if not employee:
                continue
            keys = Util.key_employee_hold(employee)
            print('Keys employee is holding: ', ', '.join([str(k['number']) for k in keys]))
            key_loss = input('Which one is lost: ')
            try:
                key_loss = int(key_loss)
            except ValueError:
                print('Invalid key number')
            Util.insert_return(employee_id, key_loss, True)

        elif choose == 'e':
            employees = list(db.employees.find())
            print('Employees in database: ',
                  ', '.join([str(e['name']) + '(' + e['employee_id'] + ')' for e in employees]))
            employee_id = input('Which employee (enter employee id): ')
            employee = Util.find_employee(employee_id)
            if not employee:
                continue
            rooms = Util.room_employee_can_enter(employee)
            if not rooms:
                print('Employee', employee['name'], 'has no access to any room')
            else:
                print('Employee', employee['name'], 'has access to rooms: ',
                      ', '.join([db.dereference(r['building'])['name'] + ' ' + str(r['number']) for r in rooms]))

        elif choose == 'j':
            rooms = list(db.rooms.find())
            if not rooms:
                print('There is no room in database')
                continue
            print('Rooms in database: ',
                  ', '.join([db.dereference(r['building'])['name'] + ' ' + str(r['number']) for r in rooms]))
            building_name, room_number = input('Enter building and room: ').split()
            try:
                room_number = int(room_number)
            except ValueError:
                print('Invalid room number')
            room = Util.find_room(building_name, room_number)
            if not room:
                continue
            employees = []
            for req in db.requests.find({'room': DBRef('rooms', room['_id'])}):
                lo = db.loan.find_one({'request': DBRef('requests', req['_id'])})
                ret = db.returns.find_one({'loan': DBRef('loan', lo['_id'])}, {'_id': 1})
                if not ret:
                    employees.append(db.dereference(req['employee']))
            if not employees:
                print('No one get access to the room')
            else:
                print('Employees can enter the room: ', ', '.join([e['name'] for e in employees]))
