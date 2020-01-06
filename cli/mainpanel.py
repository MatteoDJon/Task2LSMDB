import pymongo
import datetime
import getpass
from pprint import pprint


class Connect:

    def __init__(self):
        self.client = None
        self.dates = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
                      "oct": 10, "nov": 11, "dec": 12}

    def findReviewer(self):
        db = self.client["test_database"]
        while (True):
            name = input("Insert reviewer's ID or 'exit' to return to main menu: ")
            if name != "exit":
                doc_list = db.reviewer.find_one({"Name": name}, {"Reviews": 1, "_id": 0})  # find all data
                if doc_list != None:
                    rew_list = [int(item) for item in doc_list["Reviews"]]
                    for rew in rew_list:
                        coll = db.hotel.find_one({"Reviews._id": rew}, {"Reviews.Name": name})
                        print(coll)
                        return

                else:
                    print("Reviewer not found.\n")
            else:
                return

    def findHotel(self):
        db = self.client["test_database"]
        while (True):
            name = input("Insert hotel name or 'exit' to return to main menu: \n")
            if name == "exit":
                return name
            elif db.hotel.count_documents({"Name": name}) > 0:
                hotels = db.hotel.find({"Name": name})
                for doc in hotels:
                    print("Nome: " + doc["Name"])
                    print("Descrizione: " + doc["Description"])
                    print("ServiceRating: " + str(doc["ServiceRating"]))
                    print("PositionRating: " + str(doc["PositionRating"]))
                    print("AverageRating: " + str(doc["AverageRating"]))
                    print("CleanlinessRating: " + str(doc["CleanlinessRating"]))
                    print("City: " + doc["City"])
                    print("Nation: " + doc["Nation"])
                    print("Number of reviews: " + doc["NumberReview"])
                    for rew in doc["Reviews"]:
                        pprint(rew)
                return
            print("The selected hotel is not present in the database.\n")

    def adequate(self):
        db = self.client["test_database"]
        plt = input("Select nation or city:\n")
        if plt == "city":
            chosen_city = self.showCities(db)
            if chosen_city != "exit":
                result = db.hotel.aggregate(
                    {"$match": {"city": chosen_city}},
                    {"  $group": {"_id": "$id", "name": "$Name"}})
                for hotel in result:
                    print(hotel["Name"] + "\n")
                    for rew in hotel["reviews"]:
                        print(rew)
        elif plt == "nation":
            choice = self.showNation(db)
            if choice != "exit":
                chosen_city = self.showCities(db)
                if chosen_city != "exit":
                    result = db.hotel.aggregate(
                        {"$match": {"city": chosen_city}},
                        {"  $group": {"_id": "$id", "name": "$Name"}})
                    for hotel in result:
                        print(hotel["Name"] + "\n")
                        for rew in hotel["reviews"]:
                            print(rew)

    def showNation(self, db):
        coll = db.nation.distinct("Name")
        while (True):
            for item in coll:
                print(item)
            chosen = input("Select nation or enter 'exit' to return to main menu: \n")
            if chosen in coll or chosen == "exit":
                return chosen

    def showCities(self, db):
        coll = db.city.distinct("Name")
        while (True):
            for item in coll:
                print(item)
            chosen = input("Select city or enter 'exit' to return to main menu: \n")
            if chosen in coll or chosen == "exit":
                return chosen

    def getConnection(self):
        if self.client == None:
            self.client = pymongo.MongoClient('mongodb://localhost:27017/')

    def close(self):
        if self.client != "":
            self.client.close()

    def manageAnalytics(self):
        plt = input("Select city or nation:\n")

    def deleteNation(self, db):
        while (True):
            nations = db.hotel.distinct("Nation")
            for elem in nations:
                print(elem)
            choice = input("Select nation to be deleted or enter 'exit' to return to administrator menu: ")
            if choice in nations:
                nat_to_delete = db.nation.find_one(choice)  # cursor of nation to be deleted
                cit_to_delete = []
                for city in nat_to_delete["Cities"]:
                    cit_to_delete.append(city["cityName"])
                    hotel_to_delete = db.hotel.find({"City": city}, {"Reviews": 1, "_id": 0})
                    rew_num = []
                    for hot in hotel_to_delete:
                        for r in hot["Reviews"]:
                            rew_num.append(r["_id"])
                    if rew_num != []:
                        # db.hotel.update({}, {"$pull": {"Reviews._id": {"$in": rew_num}}}, {"multi": "true"})
                        db.reviewer.update({}, {"$pull": {"Reviews": {"$in": rew_num}}}, {"multi": "true"})
                db.hotel.remove({"Nation": choice})
                db.nation.remove({"Name": choice})
            elif choice == "exit":
                break
            else:
                print("Choice not valid.\n")

    def deleteCity(self, db):
        while (True):
            cities_in_system = db.nation.distinct("Cities.cityName")
            for city in cities_in_system:
                print(city)
            choice = input("Select city or enter 'exit' to return to admin main menu: ")
            if choice in cities_in_system:
                hotels_to_delete = db.hotel.find({"City": choice})
                rew_to_delete = []
                hot_num = []  # id list hotels to be deleted
                for hot in hotels_to_delete:
                    hot_num.append(hot["_id"])
                    for r in hot["Reviews"]:
                        rew_to_delete.append(r["_id"])
                db.nation.update({}, {"$pull": {"Cities.cityName": {"$in": cities_in_system}}}, {"multi": "true"})
                db.reviewer.update({}, {"$pull": {"Reviews": {"$in": rew_to_delete}}}, {"multi": "true"})
                break
            elif choice == "exit":
                return
            else:
                print("Choice not valid. \n")

    def deleteHotel(self, db):
        hotel_list_names = db.hotel.distinct("Name")
        while (True):
            choice = input(
                "Insert hotel name, 'list' to see the list of available hotels or 'exit' to return to admin main menu: ")
            if choice in hotel_list_names:
                rec_list = db.hotel.find({"Name": choice})
                rec_num = []
                for rec in rec_list:
                    rec_num.append(rec["_id"])
                if rec_num != []:  # an hotel may have no reviews?
                    db.reviewer.update({}, {"$pull": {"Reviews": {"$in": rec_num}}}, {"multi": "true"})
                db.nation.update({}, {"$pull": {"Cities.cityName": choice}}, {"multi": "true"})
                db.hotel.remove_one({"_id": rec_list["_id"]})
                break
            elif choice == "list":
                for hotel in hotel_list_names:
                    print(hotel)
            elif choice == "exit":
                break
            else:
                print("Choice not valid")

    def deleteReviewer(self, db):
        reviewers_list_names = db.reviewer.distinct("Name")
        while (True):
            choice = input(
                "Insert reviewer name, 'list' to see the list of available reviewers or 'exit' to return to admin main menu: ")
            if choice in reviewers_list_names:
                db.hotel.update({}, {"$pull": {"Reviews.Reviewer": choice}}, {"multi": "true"})  # elimina id
                db.reviewer.remove({"Name": choice})
                break
            elif choice == "list":
                for name in reviewers_list_names:
                    print(name)
            elif choice == "exit":
                break
            else:
                print("Choice not valid")

    def deleteReview(self, db):
        reviewers_list_names = db.reviewer.distinct("Name")
        while (True):
            choice = input("Insert reviewer ID:")
            if choice in reviewers_list_names:
                db.reviewer.update({"Name": choice}, {"$pull": {"Reviews.Reviewer": choice}})
    def updatePassword(self, db, user):
        while (True):
            print("Insert new password: ")
            new_pw = getpass.getpass()
            if new_pw != "" and new_pw != "exit":
                db.user.update({"Username": user}, {"Password": "new_pw"})
            elif new_pw == "exit":
                break
            else:
                print("Choice not valid.")
    def findUser(self, db):
        while (True):
            option = ["view scraper info", "view admin info", "update admin info", "update scraper info"]
            for opt in option:
                print(opt + "\n")
            choice = input("Select operation or enter 'exit' to return to admin menu: ")
            if choice in option:
                if choice == option[0]:
                    pprint(db.user.find({"Username": "admin"}))
                if choice == option[1]:
                    pprint(db.user.find({"Username": "scraper"}))
                if choice == option[2]:
                    self.updatePassword(db, "admin")
                if choice == option[2]:
                    self.updatePassword(db, "spider")
            elif choice=="exit":
                break
            else:
                print("Choice not valid.\n")

    def manageLogin(self):
        db = self.client["test_database"]
        username = input("Username: ")
        pw = getpass.getpass()
        res = db.user.count_documents({"Username": username, "Password": pw})
        if res > 0:
            option = ["logout", "delete nation", "delete city", "delete hotel", "delete reviewer",
                      "delete review" "find user"]
            while (True):
                chosen = input("Select option or enter 'help' to see command list: \n")
                if chosen == option[0]:  # logout
                    break
                if chosen == option[1]:  # delete nation
                    self.deleteNation(db)
                if chosen == option[2]:  # delete city
                    self.deleteCity(db)
                if chosen == option[3]:  # delete hotel
                    self.deleteHotel(db)
                if chosen == option[4]:  # delete reviewer
                    self.deleteReviewer(db)
                if chosen == option[5]:  # delete review
                    self.deleteReview(db)
                if chosen == option[6]:  # find user
                    self.findUser(db)

    def computeAnalysisNation(self, nation):
        print("Month per month:")
        pipeline = [
            {
                "$match": {"year": 2019, "nationID": nation}
            },
            {
                "$group":
                    {"_id": "$month",
                     "average": {"$avg": "$Vote"}}}
        ]
        result = self.client.hotel.aggregate(pipeline)
        print(result)
        pipeline1 = [
            {
                "$match": {"nationID": nation}
            },
            {
                "$group":
                    {"_id": "$month",
                     "averageRatings": {"$avgrat": "$averageRating", "$serRat": "$serviceRating",
                                        "$clrat": "cleanlinessRating", "$posRat": "$positionRating"}
                     }

            },
            {
                "$sort": {"averageRatings": -1}
            }
        ]
        result1 = self.client.hotel.aggregate(pipeline1)
        print(result1)

    def computeAnalysisCity(self, place):
        now = datetime.datetime.now()  # current date and time
        day = now.strftime("%d")
        month = now.strftime("%m")
        year = now.strftime("%Y")

        db = self.client.test_database
        hotel_list = db.hotels.find({"cityID": place})
        averall_avgs = {}
        hotel_names = []
        for hotel in hotel_list:
            averages = []
            for i in range(self.dates[month]):
                averages.append([])
            for id in hotel["reviewList"]:
                rew = db.findOne({"_id": id})
                # result = self.isAntecedent(rew["Day"], rew["Month"], rew[ "Year"])
                if len(rew) != 0 and rew["Year"] == int(year) and rew["Day"] >= int(day):
                    averages[self.dates[month] - 1].append(rew["Vote"])
                    for i in range(len(averages)):
                        temp = 0
                        count = len(averages[i])
                        for it in averages[i]:
                            temp += it
                        averages[i] = temp / count
                    averall_avgs[hotel["Name"]] = [averages]
        print("average rating vote from the reviews month by month of the current year:\n")
        for i in averall_avgs:
            print("The averages for current year for hotel " + i.key() + " are:\n")
            print(i)

    def scoreboard(self, place, type):
        place = "$" + place
        db = self.client.test_database

    # print(i, averall_avgs[i])  # stampa _id, avg

    def manageStatistics(self):
        db = self.client["test_database"]
        option = ["AverageRating", "ServiceRating", "CleanlinessRating", "PositionRating"]
        type = input("Select city or nation")
        place = ""
        while (True):
            if type == "City":
                list_available_cities = db.nation.distinct("Cities.cityName")
                for city in list_available_cities:
                    print(city + "\n")
                place = input("Select city or enter 'exit' to return to main menu: ")
                while (True):
                    if place == "exit":
                        type = "exit"
                        break
                    elif place in list_available_cities:
                        while (True):
                            for elem in option:
                                print(elem + "\n")
                            chosen = input("Select evaluation parameter or enter 'exit' to return to main menu: ")
                            if chosen in option:
                                result = self.computeAvg(chosen, place, type)
                                print("Positive: " + str(result[0]))
                                print("Neutral: " + str(result[2]))
                                print("Negative: " + str(result[1]))
                            elif chosen == "exit":
                                place = "exit"
                                break
                            else:
                                print("Choice not valid. \n")
                                print("Select city or enter 'exit' to return to main menu:")
                    else:
                        print("Choice not valid. \n")
                        for city in list_available_cities:
                            print(city + "\n")
                        place = input("Select city or enter 'exit' to return to main menu: ")
            elif type == "Nation":
                list_available_nations = db.nation.distinct("Name")
                for nat in list_available_nations:
                    print(nat + "\n")
                place = input("Select nation or enter 'exit' to return to main menu: ")
                while (True):
                    if place == "exit":
                        type = "exit"
                        break
                    elif place in list_available_nations:
                        while (True):
                            for elem in option:
                                print(elem + "\n")
                            chosen = input("Select evaluation parameter or enter 'exit' to return to main menu: ")
                            if chosen in option:
                                result = self.computeAvg(chosen, place, type)
                                print("Positive: " + str(result[0]))
                                print("Neutral: " + str(result[2]))
                                print("Negative: " + str(result[1]))
                            elif chosen == "exit":
                                place = "exit"
                                break
                            else:
                                print("Choice not valid. \n")
                                print("Select city or enter 'exit' to return to main menu:")
                    else:
                        print("Choice not valid. \n")
                        for nat in list_available_nations:
                            print(nat + "\n")
                        place = input("Select nation or enter 'exit' to return to main menu: ")
            elif type == "exit":
                break
            else:
                print("Choice not valid.\n")

    def computeAvg(self, chosen, place, type):
        db = self.client["test_database"]
        numPos = db.hotel.count_documents({"$and": [{chosen: {"$gt": 6}}, {type: place}]})
        numNeg = db.hotel.count_documents({"$and": [{chosen: {"$lt": 5}}, {type: place}]})
        numMed = db.hotel.count_documents({type: place}) - (numPos + numNeg)
        return [numPos, numNeg, numMed]


if __name__ == '__main__':

    options = ["login", "read analytics", "read statistics", "find hotel", "find reviewer"]

    print("Options:\n")
    for item in options:
        print(item + "\n")
    print("Select an option or enter exit to quit the application (enter 'help' for command explanation).\n")
    mongodb = Connect()
    while (True):
        chosen = input("Choice:")
        # pid = os.fork()
        # if pid == 0:  # child process
        if chosen == options[0]:  # login
            mongodb.getConnection()
            mongodb.manageLogin()
        if chosen == options[1]:  # analitycs
            mongodb.getConnection()
        # mongodb.manageAnalytics()
        if chosen == options[2]:  # statistics
            mongodb.getConnection()
            # mongodb.manageStatistics()
        if chosen == options[3]:  # "find hotel"
            mongodb.getConnection()
            mongodb.findHotel()
        if chosen == options[4]:  # "find reviewer"
            mongodb.getConnection()
            mongodb.findReviewer()
        if chosen == "help":
            print(options[0] + " - log in the application\n")
            print(options[1] + " - show available analytics about hotels in specific city or nation\n")
            print(options[2] + " - show available statistics about hotels in a specific city or nation\n")
            print(options[3] + " - find hotel in the system\n")
            print(options[4] + " - find all the reviews by a specific reviewer\n")
        if chosen == "exit":
            break
        print("Select an option or enter exit to quit the application (enter 'help' for command explanation).\n")

    mongodb.close()
