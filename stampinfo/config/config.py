import os


def initGlobalVariables():

    # debug ############
    global uasDebug

    # wkip better code: uasDebug = os.environ.get("UasDebug", "0") == "1"
    if "UasDebug" in os.environ.keys():
        uasDebug = bool(int(os.environ["UasDebug"]))
    else:
        uasDebug = True

    uasDebug = False

    global uasDebug_keepVSEContent
    uasDebug_keepVSEContent = True and uasDebug

    if uasDebug:
        print("UAS debug: ", uasDebug)


def releaseGlobalVariables():

    pass
