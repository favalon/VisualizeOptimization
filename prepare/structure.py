import os
import numpy as np
import json
from utils import utils
from sklearn.preprocessing import normalize


class Project:

    camera = None
    character = None

    def __init__(self, db_loader, project_id, full_time=None, protagonist=None, add_object=None, add_user_cams=None):
        self.project_id = project_id

        self.script = db_loader.loadScript()  # list of dict
        # script reorder only for temp
        self.script_reorder()

        # if startTime and endTime:
        #     self.startTime = startTime
        #     self.endTime = endTime
        # else:
        self.startTime = 0
        self.endTime = max([int(x) for x in self.script[-1]["startTime"]]) + max([int(x) for x in self.script[-1]["duration"]])-1
        self.totalTime = utils.getTotalTime(self.script)

        # self.totalDuration = total_duration
        # if not self.totalDuration:
        #     self.totalDuration = self.totalTime

        self.distMap = db_loader.loadDistMap() # dict {<distName>:<distValue>}
        self.characters = db_loader.loadCharacters() # dict {<charName>:<charIndex>}
        self.numCharacters = len(self.characters.keys())
        if protagonist:
            self.protagonist = protagonist
        else:
            self.protagonist = utils.getProtagonist(self.script)
        self.addObjects = add_object
        self.addUserCams = add_user_cams

        # default character surrounding cameras data
        self.defaultCameras = db_loader.loadDefaultCameras()
        self.numDefaultCameras = len(self.defaultCameras.keys())
        self.charVisibility = db_loader.loadCharVisibility(self.totalTime, self.numCharacters) # 4D list of shape [66,63,3,6]
        self.eyePos = db_loader.loadEyePos(self.totalTime, self.numCharacters) # 4D list of shape [66,63,3,2], "NA" if no eye present
        self.headRoom = db_loader.loadHeadRoom(self.totalTime, self.numCharacters) # 3D list of shape [66,63,2], "NA" if head top is out
        self.leftRightOrder = db_loader.loadLeftRight(self.totalTime, self.numCharacters) # 3D list of shape [66,63,3], "NA" if character eye not present
        self.userCamData = None

        # user objects are added to be considered
        self.objects = None
        self.objVisibility = None
        if self.addObjects:
            self.objects = db_loader.loadObjects() #
            self.objVisibility = db_loader.loadObjVisibility(self.totalTime, self.numDefaultCameras, self.numCharacters) # 4D list of shape [66, 63, <number of user added objects>, 2]

        # user defined cameras are added to be considered
        self.userCamData = None
        # if self.addUserCams:
        #     self.userCamData = db_loader.loadUserCamData() # dict {startTime: <user cam data>}
        #     self.userCamData, self.parallelUserCam = user_cam_preprocess.preprocess_user_cam(self.userCamData)
        #     print(self.userCamData)
        #     print(self.parallelUserCam)

        # conflict detector
        self.defaultVelocity = db_loader.loadDefaultVelocity()
        self.defaultDist = db_loader.loadDefaultCharCamDist()

        # extra part
        self.char2camera_id = None
        self.color_abs_coverage = None
        self.color_code = None
        self.color_diff_coverage = None
        self.action_data = None
        self.animation_dict = None
        self.animation_score_dict = None
        self.talking_char_t = None

        # optimized path
        self.camera_optimized_path = None
        self.minimum_cost_map = None
        self.initial_minimum_cost_map()

    def script_reorder(self):
        self.script = sorted(self.script, key = lambda i: i['startTime'][0])

        for i, seq_data in enumerate(self.script):
            if max(seq_data['duration']) == 0:
                self.script.remove(seq_data)


    def init_char2camera_id(self):
        char2camera_id = {}
        for key in self.defaultCameras.keys():
            charIndex = self.defaultCameras[key]['charIndex']
            if charIndex not in char2camera_id.keys():
                char2camera_id[charIndex] = []
                x = self.defaultCameras[key]['camIndex']
                char2camera_id[charIndex].append(self.defaultCameras[key]['camIndex'])
            else:
                char2camera_id[charIndex].append(self.defaultCameras[key]['camIndex'])

        self.char2camera_id = char2camera_id

    def initial_talking_char_t(self, talking_char_t):
        self.talking_char_t = talking_char_t

    def initial_minimum_cost_map(self):
        self.minimum_cost_map = np.full((self.totalTime, self.numDefaultCameras), 9999)

    def initial_animation_score_dict(self, path):
        with open(path, "r") as f:
            self.animation_score_dict = json.load(f)

    def load_color_abs_coverage(self, color_abs_coverage):
        self.color_abs_coverage = color_abs_coverage

    def load_color_code(self, color_code):
        self.color_code = color_code

    def load_color_diff_coverage(self, color_diff_coverage):
        self.color_diff_coverage = color_diff_coverage

    def load_action_data(self, action_data):
        self.action_data = action_data

    def load_animation_dict(self, animation_dict):
        self.animation_dict = animation_dict

    def set_camera_optimized_path(self, camera_optimized_path):
        self.camera_optimized_path = camera_optimized_path

    def get_camera_optimized_path(self):
        return self.camera_optimized_path


class Sequence:

    def __init__(self, iid, length):
        self.iid = iid
        self.length = length
        self.character_active = None

    def initial_character(self, character):
        self.character_active = character


class Camera:

    def __init__(self, id, setting, character):
        self.camera_id = id
        self.camera_setting = setting
        self.character = character  # camera bind character
        self.image_path_list = None

    def load_image_path(self, path):
        # initial image_path_list by image folder path
        self.image_path_list = []
        pass


class Object:

    def __init__(self, iid, name, is_character=True):
        self.isCharacter = is_character  # is character or not
        self.iid = iid
        self.name = name
        self.camera = None
        self.action = None
        self.sequence_activation = None  # character action
        self.sequence_action_length = None
        self.sequence_action_start_time = None
        self.sequence_action = None  # len == sequence length, value == cur_sequence action_id

    def load_camera(self, data):
        self.camera = []
        pass

    def load_action_list(self, data):
        self.action = []
        self.sequence_action = []  # this is 2D list, actions -> action-id
        pass

    def active_sequence(self, data):
        self.sequence_activation = []  # character is activate?1:0
        self.sequence_action_start_time = []  # 2D list sequence_id -> actions_start_time
        self.sequence_action_length = []  # value == current actions length


class CostMatrix:

    def __init__(self, project_id, action_cost_weight=5, visual_cost_weight=1, talking_cost_weight=15):
        self.project_id = project_id
        self.action_cost_weight = action_cost_weight
        self.visual_cost_weight = visual_cost_weight
        self.talking_cost_weight = talking_cost_weight

        self.sequence_cover = None
        self.action_map = None
        self.visual_cost_map = None
        self.action_cost_map = None
        self.talking_cost = None

        # ======= sum up the cost parts ===========
        self.quality_cost = None

    def init_sequence_cover(self, sequence_cover):
        self.sequence_cover = sequence_cover

    def init_action_map(self, action_map):
        self.action_map = action_map

    def init_visual_cost_map(self, visual_cost_map):
        self.visual_cost_map = visual_cost_map

    def init_action_cost_map(self, action_cost_map):
        self.action_cost_map = action_cost_map

    def normalize_cost(self, matrix):
        pass

    def init_talking_cost(self, talking_cost):
        self.talking_cost = talking_cost

    def init_quality_cost(self, quality_cost):
        self.quality_cost = quality_cost

