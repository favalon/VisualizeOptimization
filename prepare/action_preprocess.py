
root_action_list = ["subjectOnly", "subjectStrong", "subjectProminent", "even", "objectProminent", "objectStrong", "objectOnly"]
actionSOImportance = {
                        "subjectOnly": [1, 0],
                        "subjectStrong": [0.8, 0.2],
                        "subjectProminent": [0.7, 0.3],
                        "even": [0.5, 0.5],
                        "objectProminent": [0.3, 0.7],
                        "objectStrong": [0.2, 0.8],
                        "objectOnly": [0, 1]}

charBodyImportanceList = ["facialProminent", "upperBodyProminent", "lowerBodyProminent", "wholeBodyProminent"]
charBodyImportance = {"facialProminent": [.8, 0., .2, 0., 0., 0.],
                        "upperBodyProminent": [0.5, 0, 0.5, 0, 0, 0],
                        "lowerBodyProminent": [0, 0, 0.2, 0, 0.8, 0],
                        "wholeBodyProminent": [0.3, 0.1, 0.3, 0.1, 0.1, 0.1]}


itemImportanceList = ["frontProminent", "backProminent"]
itemImportanceMap = {"frontProminent": [0.8, 0.2],
                    "backProminent": [0.2, 0.8]}

# TODO: art resource list should be read from database
# now keep it local

# categorize action animations
actionSOImporanceMap = {"idle": "subjectOnly",
                         "talk": "subjectProminent",
                         "walk": "subjectOnly",
                         "stand": "subjectOnly",
                         "sit": "subjectOnly",
                         "look": "even",
                         "run": "subjectOnly",
                         "swim": "subjectOnly",
                         "encourage": "subjectOnly",
                         "lie": "subjectOnly",
                         "selfie": "subjectOnly"}


actionBodyImportanceMap = {"idle": "wholeBodyProminent",
                         "talk": "facialProminent",
                         "walk": "wholeBodyProminent",
                         "stand": "wholeBodyProminent",
                         "sit": "wholeBodyProminent",
                         "look": "upperBodyProminent",
                         "run": "wholeBodyProminent",
                         "swim": "wholeBodyProminent",
                         "encourage": "upperBodyProminent",
                         "lie": "wholeBodyProminent",
                         "selfie": "upperBodyProminent"}

def getActionBodyImportance(action8Layers):
    # if user define some part of action, then this part can change the body prominent
    if action8Layers[2] != "NA":
        if action8Layers[1] != "NA":
            return charBodyImportance["facialProminent"]
        else:
            return charBodyImportance["upperBodyProminent"]

    return charBodyImportance[actionBodyImportanceMap[action8Layers[0].split("_")[0]]]

def getActionSOImportance(action8Layers):
    return actionSOImportance[actionSOImporanceMap[action8Layers[0].split("_")[0]]]

def getItemImportance():
    return itemImportanceMap["frontProminent"]

if __name__ == "__main__":
    pass
    # db_address = "mysql.minestoryboard.com"
    # db, cursor = db_update.db_connect(db_address, "minestory", "2870", "minestory")
    # script = load_data.loadScript(1, cursor)
    # for sequence in script:
    #     print(sequence["sequenceIndex"])
    #     for action in sequence["action"]:
    #         # print(getActionBodyImportance(action))
    #         print(action)
    #         print(getActionSOImportance(action))















