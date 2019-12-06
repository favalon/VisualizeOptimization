import mysql.connector
import json
import ast


class DataBase:
    def __init__(self, db_address, user_name, passwd, database):
        # basic setting
        self.db_address = db_address
        self.user_name = user_name
        self.passwd = passwd
        self.database = database

        self.db = None
        self.cursor = None

    def db_connect(self):
        if self.db is None:
            mydb = mysql.connector.connect(
                host=self.db_address,
                user=self.user_name,
                passwd=self.passwd,
                database=self.database,
                port=3306
            )
            cursor = mydb.cursor(buffered=True)
            self.db = mydb
        else:
            print("{db_address} is already connected".format(db_address=self.db_address))

        if self.cursor is None:
            self.cursor = cursor
        else:
            print("cursor is already exist, please close current cursor first")

    def db_disconnect(self):
        self.cursor.close()
        self.db.close()
        self.cursor = None
        self.db = None

    def download_data(self, project_id, data_name):
        sql = "SELECT content FROM cam_optimize_data_test WHERE project_id=%s and data_name=%s;"
        self.cursor.execute(sql, (project_id, data_name))
        result = self.cursor.fetchone()[0]
        print(result)
        # TODO: save to data format used in c sharp
        return result


class DBLoader:
    def __init__(self, db, project_id):
        super().__init__()
        self.project_id = project_id
        self.db = db

    def loadScript(self):
        script = self.db.download_data(self.project_id, "script")
        script = json.loads(script)
        # print(script)
        # print(type(script))
        script = sorted(script["actions"], key=lambda i:i["sequenceIndex"])
        startIndex = script[0]["sequenceIndex"]
        for i in script:
            i["sequenceIndex"] -= startIndex
        print(script)
        return script

    def load_defaultCameras(self):
        defaultCams =  self.db.download_data(self.project_id, "defaultCams")
        defaultCams = json.loads(defaultCams)

        defaultCams = {i["camIndex"]: i for i in defaultCams["defaultCams"]}
        return defaultCams

    def loadCharacters(self):
        characters = self.db.download_data(self.project_id, "characters")
        characters = json.loads(characters)["characters"]
        print(type(characters))
        #
        #
        # characters = {i["name"]: i["charIndex"] for i in characters["characters"]}
        # print(characters)
        # print(type(characters))
        return characters

    def loadObjects(self):
        objects = self.db.download_data(self.project_id, "objects")
        objects = json.loads(objects)

        objects = {i["label"]: i["objIndex"] for i in objects["objects"]}
        print(objects)
        print(type(objects))
        return objects

    def loadDistMap(self):
        distMap = {"CU": 0.7, "MS": 1.0, "LS": 3.0}
        return distMap

    def loadCharVisibility(self, total_time, num_chars):
        charVisibility = self.db.download_data(self.project_id, "charVisibility")
        charVisibility = ast.literal_eval(charVisibility)
        if len(charVisibility) != total_time:
            print("character visibility time and animation total time unmatched")
        if len(charVisibility[0]) != num_chars * 21:
            print("number of character visibility cameras and default number of cameras unmatched")
        if len(charVisibility[0][0]) != num_chars:
            print("number of characters for character visibility and total number of characters unmatched")
        if len(charVisibility[0][0][0]) != 6:
            print("character visibility bodyparts is not 6")

        charVisibility = [[[[int(x) for x in i] for i in j] for j in r] for r in charVisibility]
        return charVisibility

    def loadEyePos(self, total_time, num_chars):
        eyePos = self.db.download_data(self.project_id, "eyePos")
        eyePos = ast.literal_eval(eyePos)
        if len(eyePos) != total_time:
            print("eye position time and animation total time unmatched")
        if len(eyePos[0]) != num_chars * 21:
            print("number of eye position cameras and default number of cameras unmatched")
        if len(eyePos[0][0]) != num_chars:
            print("number of characters for eye position and total number of characters unmatched")

        eyePos = [[[[int(x) if x != "NA" else "NA" for x in i] for i in j] for j in r] for r in eyePos]
        return eyePos

    def loadHeadRoom(self, total_time, num_chars):
        headroom = self.db.download_data(self.project_id, "headroom")
        headroom = ast.literal_eval(headroom)
        if len(headroom) != total_time:
            print("headroom time and animation total time unmatched")
        if len(headroom[0]) != num_chars * 21:
            print("number of headroom cameras and default number of cameras unmatched")
        if len(headroom[0][0]) != num_chars:
            print("number of characters for headroom and total number of characters unmatched")
        headroom = [[[int(x) if x != "NA" else "NA" for x in j] for j in r] for r in headroom]
        return headroom

    def loadLeftRight(self,  total_time, num_chars):
        leftRightOrder = self.db.download_data(self.project_id, "headroom")
        leftRightOrder = ast.literal_eval(leftRightOrder)
        if len(leftRightOrder) != total_time:
            print("leftRightOrder time and animation total time unmatched")
        if len(leftRightOrder[0]) != num_chars * 21:
            print("number of leftRightOrder cameras and default number of cameras unmatched")
        if len(leftRightOrder[0][0]) != num_chars:
            print("number of characters for leftRightOrder and total number of characters unmatched")
        return leftRightOrder

    def loadObjVisibility(self, total_time, num_chars, num_objects):
        objVisibility = self.db.download_data(self.project_id, "objVisibility")
        objVisibility = ast.literal_eval(objVisibility)
        if len(objVisibility) != total_time:
            print("object visibility time and animation total time unmatched")
        if len(objVisibility[0]) != num_chars * 21:
            print("number of object visibility cameras and default number of cameras unmatched")
        if len(objVisibility[0][0]) != num_objects:
            print("number of characters for object visibility and total number of characters unmatched")
        if len(objVisibility[0][0][0]) != 2:
            print("object visibility bodyparts is not 2")

        objVisibility = [[[[int(x) for x in i] for i in j] for j in r] for r in objVisibility]
        return objVisibility

    def loadUserCamData(self):
        userCamData = self.db.download_data(self.project_id, "userCamData")
        userCamData = json.loads(userCamData)
        # userCamDataNew = dict()
        # for i in userCamData["userCamData"]:
        #     userCamDataNew[i["startTime"]] = i

        # print(userCamDataNew)
        return userCamData

    def loadDefaultVelocity(self):
        defaultVelocity = self.db.download_data(self.project_id, "charProVelocity")
        defaultVelocity = ast.literal_eval(defaultVelocity)
        defaultVelocity = [[[float(x) for x in i] for i in j] for j in defaultVelocity]
        return defaultVelocity

    def loadDefaultCharCamDist(self):
        defaultDist = self.db.download_data(self.project_id, "charCamDist")
        defaultDist = ast.literal_eval(defaultDist)
        defaultDist = [[[float(x) for x in i] for i in j] for j in defaultDist]
        return defaultDist



if __name__ == "__main__":
    db_address = "mysql.minestoryboard.com"
    database = DataBase(db_address, "minestory", "2870", "minestory")
    database.db_connect()
    dl = DBLoader(database, 39)
    characters = dl.loadCharacters()
    database.db_disconnect()
    database.db_connect()
    database.db_connect()
    pass

