from frontEnd import frontEnd

if __name__ == '__main__':

    print("Welcome to the HotelMonitoring Appliction; here are a list of all the command available: \n")
    frontEnd=frontEnd()
    frontEnd.showCommands()
    while (True):
        if not frontEnd.executeFirstLevelCommand():
            break
     
