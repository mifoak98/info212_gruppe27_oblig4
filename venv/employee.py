import random

employees = {}
def new_employee():
    address = input("input address: ")
    branch = input("input branch: ")
    name = input("input name: ")
    employees[name] = {"Address":address, "Branch":branch, "Name":name}
    print(employees[name])
new_employee()

def modify_employee(name):
    if name in employees:
        new_address = input("input new address: ")
        new_branch = input("input new branch: ")
        if new_address:
            employees[name]["Address"] = new_address
        if new_branch:
            employees[name]["Branch"] = new_branch

            print("employee", name, "has been updated")
        else:
            print("no changes were made")
        print(employees[name])
    else:
        print("Name", name, "does not exist in the database")
modify_employee("simen")

def read_employee():
    fetch_info = input("input the name you want to find: ")
    if fetch_info in employees:
        print(employees[fetch_info])
read_employee()

def delete_employee():
    delete_instance = input("input instance you want deleted: ")
    deleted_instance = employees.pop(delete_instance)
    print("instance deleted", deleted_instance)
delete_employee()