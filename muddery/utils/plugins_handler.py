"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.data_sets import DATA_SETS


class PluginsHandler(object):
    """
    This model translates default strings into localized strings.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.plugins = {}
        self.notifications = {}

    def clear(self):
        """
        Clear data.
        """
        self.plugins = {}
        self.notifications = {}

    def reload(self):
        """
        Reload all plugins.
        """
        logger.log_info("Reload plugins.")
        
        self.clear()
        
        for plugin_name in settings.PLUGINS:
            self.load_plugin(plugin_name)
            
        for plugin_name in settings.PLUGINS:
            self.load_notifications()
            
    def load_plugin(self, plugin_name):
        """
        Load a plugin.
        
        Args:
            plugin: (string) plugin's name.
        """
        logger.log_info("Loading plugin: %s" % plugin_name)
        module_path = settings.MUDDERY_PLUGINS_DIR + "." + plugin_name + ".handler"
        module = __import__(module_path, fromlist=["handler"])
        handler = module.HANDLER
        if handler:
            self.plugins[plugin_name] = handler
            handler.at_init()
            logger.log_info("%s loaded." % plugin_name)
            
    def load_data(self):
        """
        Call all plugin's at_loading_data.
        """
        for name, plugin in self.plugins.iteritems():
            try:
                plugin.at_load_data()
                logger.log_info("%s's data loaded." % name)
            except Exception, e:
                err_message = "Can not load data of plugin '%s': %s" % (name, e)
                logger.log_tracemsg(err_message)
                
    def load_notifications(self):
        """
        Load all plugins' notifications.
        """
        for name, plugin in self.plugins.iteritems():
            try:
                plugin.load_notifications(self)
                logger.log_info("%s's notifications loaded." % name)
            except Exception, e:
                err_message = "Can not load notifications of plugin '%s': %s" % (name, e)
                logger.log_tracemsg(err_message)

    def register_notification(self, typeclass, notification, handler):
        """
        Add a new notification.
        
        Args:
            typeclass: (string) typeclass's key
            notification: (string) notification's name
            handler: (object) plugin's handler
        """
        self.notifications[(typeclass, notification,)] = handler
        
    def at_notification(self, typeclass, func_name, sender, args=None, kwargs=None, rtn=None):
        """
        Called when an object run a function.
        
        Args:
            typeclass: (string) typeclass's key of the object
            func_name: (string) function's name
            rtn: function's return
        """
        key = (typeclass, func_name,)
        if key in self.notifications:
            plugin = self.notifications[key]
            try:
                rtn = plugin.at_notification(typeclass, func_name, sender, args, kwargs, rtn)
            except Exception, e:
                err_message = "Notification error in plugin '%s': %s" % (plugin.name, e)
                logger.log_tracemsg(err_message)

        return rtn

    def load_commands(self, cmdset):
        """
        Load all plugins' notifications.
        """
        for name, plugin in self.plugins.iteritems():
            try:
                plugin.load_commands(cmdset)
            except Exception, e:
                err_message = "Can not load commands of plugin '%s': %s" % (name, e)
                logger.log_tracemsg(err_message)


# main plugins handler
PLUGINS_HANDLER = PluginsHandler()