import Utilities as Util

# Util.insert_building(name)
Util.insert_building(name='ENGR')
Util.insert_building(name='BIOL')
Util.insert_building(name='CHEM')

# Util.insert_room(building_name, number)
Util.insert_room('ENGR', 123)
Util.insert_room('CHEM', 321)
Util.insert_room('BIOL', 123)

# Util.insert_door(building_name, room_number, name)
Util.insert_door('ENGR', 123, 'front')
Util.insert_door('ENGR', 123, 'back')
Util.insert_door('BIOL', 123, 'front')
Util.insert_door('CHEM', 321, 'front')

# Util.insert_hook(number)
Util.insert_hook(111)
Util.insert_hook(222)
Util.insert_hook(333)

# Util.insert_hook_door(hook_number, building_name, room_number, door_name)
Util.insert_hook_door(111, 'ENGR', 123, 'front')
Util.insert_hook_door(222, 'ENGR', 123, 'back')
Util.insert_hook_door(333, 'BIOL', 123, 'front')
Util.insert_hook_door(111, 'CHEM', 321, 'front')

# Util.insert_employee(employee_id, name)
Util.insert_employee('100', 'Davis Dao')
Util.insert_employee('200', 'Luis Tran')
Util.insert_employee('300', 'Daniel Nguyen')
Util.insert_employee('400', 'William Le')


# Util.insert_request(employee_id, building_name, room_number)
Util.insert_request('100', 'ENGR', 123)
Util.insert_request('200', 'CHEM', 321)
Util.insert_request('300', 'BIOL', 123)
Util.insert_request('100', 'BIOL', 123)
Util.insert_request('300', 'ENGR', 123)

# Util.insert_return(employee_id, key_number, loss)
# Util.insert_return(100, 123, False)
# Util.insert_return(300, 456, True)