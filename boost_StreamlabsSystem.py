# ---------------------------------------
#   Import Libraries
# ---------------------------------------
import json
import codecs
import re
import os
import clr

clr.AddReference("IronPython.Modules.dll")
import urllib

# ---------------------------------------
#   [Required]  Script Information
# ---------------------------------------
ScriptName = "Boost"
Website = "https://www.twitch.tv/frittenfettsenpai"
Description = "Boost System. No API Key required. You can add boostpoints to a viewer and the viewer can"
Creator = "frittenfettsenpai"
Version = "1.0.0"


# ---------------------------------------
#   [Required] Intialize Data (Only called on Load)
# ---------------------------------------
def Init():
    global settings, boostData
    settingsfile = os.path.join(os.path.dirname(__file__), "settings.json")

    try:
        with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
            settings = json.load(f, encoding="utf-8")
    except:
        settings = {
            "command": "!boostticket",
            "commandTicket": "!tickets",
            "commandAdd": "!addTicket",
            "commandRemove": "!removeTicket",
            "commandTransfer": "!transferTicket",
            "boostSound": "boost.wav",
            "boostSoundVolume": 1.00,
            "userCoolDown": 3600,
            "globalCoolDown": 800,
            "languageBoost": "{0} ueberspringt mit seinem/Ihrem Level die Queue PogChamp",
            "languageTickets": "{0} hat noch {1} Boosttickets!",
            "languageAddTicket": "{0} hat ein Boostticket bekommen und besitzt nun {1} davon!",
            "languageRemoveTicket": "{0} wurde ein Boostticket entfernt und besitzt nun {1} davon!",
            "languageTransferTicket": "{0} uebergibt {1} ein Boostticket!",
            "languageErrorNoTicket": "{0} du hast leider keine Boosttickets mehr!",
            "languageErrorSyntaxTransfer": "Falsche Syntax! Bitte nutze '{0} targetUserName' ",
            "languageErrorUserCooldown": "{0} du musst leider noch mindestens {1} Sekunden warten (User Cooldown).",
            "languageErrorGlobalCooldown": "{0} du musst leider noch mindestens {1} Sekunden warten (Global Cooldown).",
        }

    try:
        datafile = os.path.join(os.path.dirname(__file__), "data.json")
        with codecs.open(datafile, encoding="utf-8-sig", mode="r") as f:
            boostData = json.load(f, encoding="utf-8")
    except:
        boostData = {}
    return


# ---------------------------------------
#   [Required] Execute Data / Process Messages
# ---------------------------------------
def Execute(data):
    global settings, boostData
    if data.IsChatMessage():
        user = data.User
        username = Parent.GetDisplayName(user).lower()

        if (data.GetParam(0).lower() == settings["command"]):
            if username not in boostData:
                boostData[username] = 0
            if boostData[username] == 0:
                Parent.SendTwitchMessage(settings["languageErrorNoTicket"].format(username))
                return

            if (Parent.IsOnUserCooldown(ScriptName, settings["command"], user) and Parent.HasPermission(user, "Caster", "") == False):
                cooldown = Parent.GetUserCooldownDuration(ScriptName, settings["command"], user)
                Parent.SendTwitchMessage(settings["languageErrorUserCooldown"].format(username, cooldown))
                return
            if (Parent.IsOnCooldown(ScriptName, settings["command"]) and Parent.HasPermission(user, "Caster", "") == False):
                cooldown = Parent.GetCooldownDuration(ScriptName, settings["command"])
                Parent.SendTwitchMessage(settings["languageErrorGlobalCooldown"].format(username, cooldown))
                return

            Parent.AddCooldown(ScriptName, settings['command'], settings['userCoolDown'])
            Parent.AddUserCooldown(ScriptName, settings['command'], user, settings['userCoolDown'])

            boostData[username] = boostData[username] - 1
            SetData()
            Parent.SendTwitchMessage(settings["languageBoost"].format(username))
            if (settings['boostSound'] != ""):
                soundfile = os.path.join(os.path.dirname(__file__), settings['boostSound'])
                Parent.PlaySound(soundfile, settings['boostSoundVolume'])
        elif (data.GetParam(0) == settings["commandTicket"]):
            if username not in boostData:
                boostData[username] = 0
            Parent.SendTwitchMessage(settings["languageTickets"].format(username, boostData[username]))
        elif (data.GetParam(0) == settings["commandAdd"] and Parent.HasPermission(user, "Caster", "")):
            toUser = str(data.GetParam(1)).lower().replace('@', '')
            if toUser not in boostData:
                boostData[toUser] = 0
            boostData[toUser] = boostData[toUser] + 1
            SetData()
            Parent.SendTwitchMessage(settings["languageAddTicket"].format(toUser, boostData[toUser]))
        elif (data.GetParam(0) == settings["commandRemove"] and Parent.HasPermission(user, "Caster", "")):
            toUser = str(data.GetParam(1)).lower().replace('@', '')
            if toUser not in boostData:
                boostData[toUser] = 0
            if boostData[toUser] > 0:
                boostData[toUser] = boostData[toUser] - 1
            SetData()
            Parent.SendTwitchMessage(settings["languageRemoveTicket"].format(toUser, boostData[toUser]))
        elif (data.GetParam(0) == settings["commandTransfer"]):
            toUser = str(data.GetParam(1)).lower().replace('@', '')
            if toUser == "":
                Parent.SendTwitchMessage(settings["languageErrorSyntaxTransfer"].format(settings["commandTransfer"]))
                return

            if toUser not in boostData:
                boostData[toUser] = 0
            if username not in boostData:
                boostData[username] = 0
            if boostData[username] == 0:
                Parent.SendTwitchMessage(settings["languageErrorNoTicket"].format(username))
                return
            boostData[username] = boostData[username] - 1
            boostData[toUser] = boostData[toUser] + 1
            SetData()
            Parent.SendTwitchMessage(settings["languageTransferTicket"].format(username, toUser))
    return


# ---------------------------------------
#    [Required] Tick Function
# ---------------------------------------
def Tick():
    return


def SetData():
    global settings, boostData
    datafile = os.path.join(os.path.dirname(__file__), "data.json")
    file = open(datafile, "w")
    file.write(json.dumps(boostData))
    file.close()
    return
