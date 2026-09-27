class HRMenu():
    def __init__(self):
        pass

    def main_menu(self):
        user_choice =-1
        while not(0<=user_choice<=9): 
            print("Here are your options:")
            print("1. See skills")
            print("2. See certifications")
            print("6. Participation Menu")
            print("7. Who's certification are about to expire")
            print("8. CRUD")
            print("9. Search Employee with certain skills")
            print("0. Leave")
            user_choice = int(input("Your choice: "))
        return user_choice


    def crud_menu(self):
        user_choice =-1
        while not(0<=user_choice):
            print("What do you want to do?")
            print("1. Create, update or delete Training") #should already link via provide Table 
            print("2. Create, update or delete Training Source")
            print("3. Create, update or delete Skill")
            print("4. Create, update or delete Diploma") #think about auto-skill
            print("5. Create, update or delete Certification")#think about auto-skill
            print("6. Create, update or delete Employee")
            print("0. Leave")


    
