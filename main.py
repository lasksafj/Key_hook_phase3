import pymongo
from bson import DBRef
from pymongo import MongoClient

import Utilities as Util

if __name__ == '__main__':
    Util.insert_employee('222', 'Toan Truong')

    # Util.insert_building(name='CECS')
    # Util.insert_room('CECS', 123)
    # Util.insert_door('CECSs', 123, 'front')
    # Util.find_employee('111')
    # Util.insert_hook_door(1, 'CECS', 123, 'front')
    # Util.insert_return('111', 1, False)

    db = Util.db
    # db.employees.delete_one({'employee_id': '222'})
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
            hook = Util.prompt_hook()
            if not hook:
                continue
            Util.insert_key(hook['number'], Util.get_next_sequence('key_number'))

        elif choose == 'b':
            employee = Util.prompt_employee()
            if not employee:
                continue
            room = Util.prompt_room()
            if not room:
                continue
            Util.insert_request(employee['employee_id'], db.dereference(room['building'])['name'], room['number'])

        elif choose == 'c':
            try:
                key_number = int(input('Enter key number: '))
            except ValueError:
                print('Invalid key number')
                continue
            room = Util.prompt_room()
            if not room:
                continue
            building_name, room_number = db.dereference(room['building'])['name'], room['number']

            key = Util.find_key(key_number)
            if not key:
                aws = input('Key is not in the database. Do you want to create new one? (y/n) ')
                if aws == 'n':
                    continue
                door = Util.prompt_door(room)
                if not door:
                    continue
                hook = Util.prompt_hook()
                if not hook:
                    continue
                Util.insert_key(hook['number'], Util.get_next_sequence('key_number'))
                Util.insert_hook_door(hook['number'], building_name, room_number, door['name'])
            else:
                access = False
                for hd in db.hook_door.find({'hook': key['hook']}):
                    r = db.dereference(db.dereference(hd['door'])['room'])
                    bd = db.dereference(r['building'])
                    if bd['name'] == building_name and r['number'] == room_number:
                        access = True
                        break
                if access:
                    print('Key', str(key['number']), 'has access to', building_name, str(room_number))
                else:
                    print('Key', str(key['number']), 'does not have access to', building_name, str(room_number))

        elif choose == 'd':
            employee = Util.prompt_employee()
            if not employee:
                continue
            keys = Util.key_employee_hold(employee)
            print('Keys employee is holding: ', ', '.join([str(k['number']) for k in keys]))
            key_loss = input('Which one is lost: ')
            try:
                key_loss = int(key_loss)
            except ValueError:
                print('Invalid key number')
            Util.insert_return(employee['employee_id'], key_loss, True)

        elif choose == 'e':
            employee = Util.prompt_employee()
            if not employee:
                continue
            rooms = Util.room_employee_can_enter(employee)
            if not rooms:
                print('Employee', employee['name'], 'has no access to any room')
            else:
                br = set([db.dereference(r['building'])['name'] + ' ' + str(r['number']) for r in rooms])
                print('Employee', employee['name'], 'has access to rooms: ',
                      ', '.join(br))

        elif choose == 'f':
            keys = db.keys.find()
            if not keys:
                print('There no key in database')
                continue
            print('Keys in database: ', ', '.join([str(k['number']) for k in keys]))
            try:
                key_number = int(input('Enter key number: '))
            except ValueError:
                print('Invalid key number')
                continue
            key = Util.find_key(key_number)
            loans = list(db.loan.find({'key': DBRef('keys', key['_id'])}))
            if not loans:
                db.keys.delete_one({'_id': key['_id']})
            else:
                can_del = True
                for lo in loans:
                    if db.returns.find_one({'loan': DBRef('loan', lo['_id'])}) is None:
                        can_del = False
                        break
                if can_del:
                    for lo in loans:
                        req = db.dereference(lo['request'])
                        db.returns.delete_one({'loan': DBRef('loan', lo['_id'])})
                        db.requests.delete_one({'_id': req['_id']})
                        db.loan.delete_one({'_id': lo['_id']})
                    db.keys.delete_one({'_id': key['_id']})
                else:
                    print('Cannot delete. Key is in use by someone')

        elif choose == 'g':
            employee = Util.prompt_employee()
            if not employee:
                continue
            keys = Util.key_employee_hold(employee)
            if not keys:
                for req in db.requests.find({'employee': DBRef('employee', employee['_id'])}):
                    lo = db.loan.find_one({'request': DBRef('requests', req['_id'])})
                    db.returns.delete_one({'loan': DBRef('loan', lo['_id'])})
                    db.loan.delete_one({'request': DBRef('requests', req['_id'])})
                    db.requests.delete_one({'_id': req['_id']})
                db.employees.delete_one({'_id': employee['_id']})
            else:
                print('Cannot delete. Employee is holding some keys')

        elif choose == 'h':
            hook = Util.prompt_hook()
            if not hook:
                continue
            room = Util.prompt_room()
            if not room:
                continue
            door = Util.prompt_door(room)
            if not door:
                continue
            building_name, room_number = db.dereference(room['building'])['name'], room['number']
            Util.insert_hook_door(hook['number'], building_name, room_number, door['name'])

        elif choose == 'i':
            print('Please choose the old employee')
            old_emp = Util.prompt_employee()
            if not old_emp:
                continue
            rooms = Util.room_employee_can_enter(old_emp)
            if not rooms:
                print('Employee', old_emp['name'], 'has no access to any room')
                continue
            br = set([db.dereference(r['building'])['name'] + ' ' + str(r['number']) for r in rooms])
            print('Current building and room that', old_emp['name'], 'has access: ', ', '.join(br))
            try:
                building_name, room_number = input('Which building and room that you’re to move: ').split()
            except ValueError:
                print('Invalid input')
                continue
            try:
                room_number = int(room_number)
            except ValueError:
                print('Invalid room number')
                continue
            if building_name + ' ' + str(room_number) not in br:
                print('Room is not in the list')
                continue
            room = Util.find_room(building_name, room_number)
            print('Please choose the new employee')
            new_emp = Util.prompt_employee()
            if not new_emp:
                continue
            for req in db.requests.find({
                'employee': DBRef('employees', old_emp['_id']),
                'room': DBRef('rooms', room['_id'])
            }):
                lo = db.loan.find_one({'request': DBRef('requests', req['_id'])})
                if db.returns.find_one({'loan': DBRef('loan', lo['_id'])}) is None:
                    # req['employee'] = DBRef('employees', new_emp['_id'])
                    db.requests.update_one(
                        {'_id': req['_id']},
                        {'$set': {'employee': DBRef('employees', new_emp['_id'])}}
                    )
                    break

        elif choose == 'j':
            room = Util.prompt_room()
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
                emp = set([e['name'] for e in employees])
                print('Employees can enter the room: ', ', '.join(emp))
