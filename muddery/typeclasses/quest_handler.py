"""
QuestHandler
"""

import re
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class MudderyQuest(MudderyObject):
    """
    """
    def at_object_creation(self):
        """
        Set default values.
        """
        self.db.finished = {}


    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyObjectCreater, self).load_data()

        self.set_objectives(self.db.objectives)

    
    def set_objectives(self, obj_string):
        """
        """
        objectives = {}
        types = set()

        for string in obj_string.split(","):
            items = string.split(":")
            
            obj = {"type" : "",
                   "obj" : "",
                   "num" : 0}

            try:
                obj["type"] = items[0]
                obj["obj"] = items[1]
                obj["num"] = int(items[2])
            except:
                pass

            obj_id = obj["type"] + ":" + obj["obj"]
            objectives[obj_id] = obj
            types.add(obj["type"])

        self.objectives = objectives
        self.types = types
    

    def finished(self):
        """
        """
        for key in self.db.objectives:
            obj_num = self.db.objectives[key]["num"]
            finished = self.db.finished.get(key, 0)
    
            if finished < obj_num:
                return False

        return True


    def at_character_move_in(self):
        """
        """
        if "reach" in self.objectives:
            if


class QuestHandler(object):
    """
    """
    def __init__(self, obj):
        """
        Initialize handler
        """
        self.obj = obj


    def has_quest(self, quest):
        """
        Checks if has the given quest.
        """
        return quest in self.obj.quests


    def quest_finished(self, quest):
        """
        Checks if the given quest is finished.
        """
        return quest in self.obj.quests_finished


    def at_character_move_in(self):
        """
        """
        pass


    def at_character_move_out(self):
        """
        """
        pass


    def match_condition(self, caller, condition):
        """
        check condition
        """
        if not condition:
            return True

        # add "caller" to condition
        condition = self.safe_statement(condition)

        try:
            # check it
            match = eval(condition, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("match_condition error:%s %s" % (condition, e))
            return False

        return match


    def do_dialogue_action(self, caller, dialogue, sentence):
        """
        do dialogue's action
        """
        
        # get dialogue
        dlg = self.get_dialogue(dialogue, sentence)
        if not dlg:
            return

        # do dialogue's action
        self.do_action(caller, dlg["action"])


    def do_action(self, caller, action):
        """
        do action
        """
        if not action:
            return

        # add "caller" to action
        action = self.safe_statement(action)

        # run action
        try:
            eval(action, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("do_dialogue_action error:%s %s" % (action, e))
            
        return


    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}


    re_words = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)|(\"(.*?)\")")
    def safe_statement(self, statement):
        """
        Add "caller." before every words.
        """
        return self.re_words.sub(self.sub_statement, statement)


    statement_keywords = {"not", "and", "or"}
    def sub_statement(self, match):
        """
        Replace <match> with caller.<match> except key words.
        """
        match = match.group()

        # keep the key words
        if match in self.statement_keywords:
            return match

        # keep the strings in quotes
        if match[0] == "\"" and match[-1] == "\"":
            return match

        return "caller." + match


# main dialoguehandler
DIALOGUE_HANDLER = DialogueHandler()