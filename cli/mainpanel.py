import os
import pymongo
import datetime
import getpass


class Connect:

    def __init__(self):
        self.client = None
        self.cities = {"Firenze" :3456, "Bologna": 1, "Terni":2}
        self.nations ={"Italia": 0,  "Iran":2000, "USA":1}
        self.logged=False
        self.dates = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
                      "oct": 10, "nov": 11, "dec": 12}
        self.dictionary = {}  # contiene i codici corrispondenti a città e nazione
        self.logged_user=""
        self.users = {}


    def getConnection(self):
        if self.client==None:
            self.client= pymongo.MongoClient('mongodb://localhost:27017/')

        return self.client
    def isLogged(self):
        if self.logged and self.logged_user=="admin":
            return True, True
        elif self.logged and self.logged_user!="admin":
            return True, False
        else:
            return False, False
    def updateDict(self, name, code):
        if name not in self.dictionary.keys():
            self.dictionary[name] = code

    def close(self):
        if self.client!="":
            self.client.close()

    def manageAnalytics(self):
        plt = input("Select city or nation:\n")
        if plt == "city":
            for item in self.cities:
                print(item)
            city = input("Select city:\n")
            if city in self.dictionary.keys():
                self.computeAnalysis(self.dictionary[city], "CityID")
        elif plt == "nation":
            for item in self.nations:
                print(item)
            nation = input("Select nation:\n")
            if nation in self.dictionary.keys():
                self.computeAnalysis(self.dictionary[nation], "NationID")

    def manageLogin(self):
        if(self.logged==False):
            while (True):
                print("Enter your credentials")
                user = input("username:")
                p = getpass.getpass()
                for elem in self.users:
                    print(elem)
                if user in self.users.keys():
                    self.logged = True
                    print("Welcome " + user)
                    break

                else:
                    if input(
                            "Login not valid, press any key to continue or type exit to return to main menu!\n") == "exit":
                        print("\n")
                        break

    def manageRegister(self):

        while(True):

            #get unique id with datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            db = self.client["test_database"]

            user=input("Username: ")
            pw=getpass.getpass()
            coll=db.eco.insert_one({"user": user, "pw":pw })

            break

    def computeAnalysis(self, place, type):
        now = datetime.datetime.now()  # current date and time
        day = now.strftime("%d")
        month = now.strftime("%m")
        year = now.strftime("%Y")

        db = self.client.test_database
        hotel_list = db.hotels.find({type: place})
        averall_avgs = {}
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
                    averall_avgs[hotel["_id"]] = [hotel["Name"], averages]
        print("average rating vote from the reviews month by month of the current year:\n")
        for i in averall_avgs:
            print("TODO: show averall_avg")

    def scoreboard(self, place, type):
        place = "$" + place
        db=self.client.test_database

    # print(i, averall_avgs[i])  # stampa _id, avg

    def manageStatistics(self):
        opt = ["averageRating", "serviceRating", "cleanlinessRating", "positionRating"]
        for item in opt:
            print(item + "\n")
        chosen = input("Select evaluation attribute:\n")
        if chosen in opt:
            plt = input("Select city or nation:\n")
            if plt == "city":
                for item in self.cities:
                    print(item)
                city = input("Select city:\n")
                if city in self.cities.keys():
                    self.computeAvg(chosen, self.cities[city], "cityID")
                else:
                    print("The option is not valid.\n")
                    return
            elif plt == "nation":
                for item in self.nations:
                    print(item)
                nation = input("Select nation:\n")
                if nation in self.nations.keys():
                    self.computeAvg(chosen, self.nations[nation], "nationID")
                else:
                    print("The option is not valid.\n")
                    return
            else:
                print("The option is not valid.\n")
                return

    def computeAvg(self, chosen, place, type):
        db = self.client.test_database
        numPos = db.hotel.count_documents({"$and": [{chosen: {"$gt": 6}}, {type: place}]})
        numNeg = db.hotel.count_documents({"$and": [{chosen: {"$lt": 5}}, {type: place}]})
        numMed = db.hotel.count_documents({type: place}) - (numPos + numNeg)
        print(numPos, numNeg, numMed)
        # plot?


if __name__ == '__main__':

    options = ["login", "register", "read analytics", "read statistics"]

    print("Options:\n")
    for item in options:
        print(item + "\n")
    print("Select an option or enter exit to quit the application (enter 'help' for command explanation).\n")
    mongodb=Connect()
    while (True):
        chosen = input("Choice:")
        # pid = os.fork()
        # if pid == 0:  # child process
        if chosen == "login":  # login
            mongodb.getConnection()
            mongodb.manageLogin()
            res=mongodb.isLogged()
            if res[0] and res[1]=="admin":
                print("option - admin")
            elif res[0] and res[1]!="admin":
                print("option - user")
        if chosen == "register":  # register
            mongodb.getConnection()
            mongodb.manageRegister()
        if chosen == "read analytics":  # analitycs
            mongodb.getConnection()
            mongodb.manageAnalytics()
        if chosen == "read statistics":  # statistics
            mongodb.getConnection()
            mongodb.manageStatistics()
        if chosen== "help":
            print(options[0]+ " - log in the application\n")
            print(options[1]+ " - sign up in the application\n")
            print(options[2]+ " - show available analytics about hotels in specific city or nation\n")
            print(options[3]+ " - show available statistics about hotels in a specific city or nation\n")
        if chosen=="exit":
            break
        print("Select an option or enter exit to quit the application (enter 'help' for command explanation).\n")

    mongodb.close()





