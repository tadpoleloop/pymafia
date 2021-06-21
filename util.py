from kolmafia import km, MafiaAbort
import json
from math import ceil as ceiling
import re
import sys
from time import sleep
import logging

RETURNED_PATTERN = "Returned: (.*)\r\n"

logging.basicConfig(filename='util.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# km.KoLmafia.main(["--GUI"])

def cli(prop):
    return km.cli(prop)

def cli_int(prop):
    command = cli(prop)
    return int(cli.value)

def cli_bool(prop):
    command = cli(prop)
    if command.value == "false":
        return False
    elif command.value == "true":
        return True
    else:
        raise
        
def get_property(prop):
    return km.get_property(prop)

def get_property_int(prop):
    return int(get_property(prop))

def get_property_bool(prop):
    s = get_property(prop)
    if s == "true":
        return True
    elif s == "false":
        return False
    else:
        raise
        
visit_url = km.visit_url
    
def available_amount(item):
    return cli_int("available_amount {}".format(item))

def item_amount(item):
    return cli_int(f"item_amount {item}")

def recover_mp(upto):
    if cli_int("my_maxmp") < upto:
        raise ("impossible")
    mp =  cli_int("my_mp")
    if mp >= upto:
        return
    count = 0
    while cli_int("my_mp") < upto:
        count += 1
        if count > 10:
            raise "stuck in loop"
        if item_amount("sausage casing") + item_amount("magical sausage") > 0:
            logging.info("eating sausage")
            cli("eat magical sausage")
            continue
        logging.info("no sausages, recovering mana with invigorating tonics")
        cli(f"acquire Doc Galaktik's Invigorating Tonic")
        cli(f"use Doc Galaktik's Invigorating Tonic")
    
def recover_hp(min_hp_percent = 0.8):
    while cli_int("my_hp") / cli_int("my_maxhp") < min_hp_percent:
        if get_property_int("_hotTubSoaks") < 5:
            cli("hottub")
        elif cli_int("my_mp") < 20:
            print("not enough mp")
            raise
        else:
            cast("cannelloni cocoon")
            
def maximize(text):
    return cli(f"maximize {text}")
    
def cast(*spells):
    cli("skill {}".format(", ".join(spells)))
    
def equip(item, slot = None):
    if slot:
        cli(f"ashq equip($item[{item}], $slot[{slot}])")
    else:
        cli(f"equip {item}")
        
def acquire(item, num = 1):
    cli(f"acquire {num} {item}")
    
def use(item, num = 1):
    cli(f"use {num} {item}")
    
def try_use(item, num = 1):
    if item_amount(item) >= num:
        use(item, num)
        return True
    else:
        return False
        
def have_effect(effect):
    return cli_int(f"ash have_effect($effect[{effect}])")

def ensure_effect(effect, turns = 1):
    while have_effect(effect) < turns:
        cli_command = cli(f"ash $effect[{effect}].default").value
        cli(cli_command)
        
def handling_choice():
    return cli_bool("ash handling_choice()")

def which_choice():
    if handling_choice():
        return cli_int("ash last_choice()")
    else:
        return -1 #not in a choice
        
def map_monster(location, monster, macro = None):
    if not cli_bool("get mappingMonsters"):
        cast("map the monsters")
    if not cli_bool("get mappingMonsters"):
        raise
    location_url = cli(f"ash to_url($location[{location}])").value
    r = visit_url(location_url)
    assert("Leading Yourself Right to Them" in r.text)
    r = visit_url("choice.php", method = "post", data = {
        "pwd": km.get_pwd_hash(),
        "whichchoice": 1435, 
        "option": 1,
        "heyscriptswhatsupwinkwink": cli_int(f"ash $monster[{monster}].id")
    })
    assert("You're fighting" in r.text)
    if macro is not None:
        run_combat(macro)
#         if "use the force" in macro.macro():
#             run_choice(3)

def my_adventures():
    return cli_int("ash my_adventures()")
    
def adv1(location, macro):
    return cli(f"ash adv1($location[{location}], -1, \"{macro.macro()}\")")

def run_combat(macro):
    cli(f"ashq run_combat(\"{macro.macro()}\")")

def set_choice(choice, number):
    km.set_property(f"choiceAdventure{choice}", number)
    
def run_choice(number = -1):
    cli(f"ashq run_choice({number})")
    
def get_fax(monster):
    cli(f"ashq faxbot($monster[{monster}], 'cheesefax')")
    
def get_and_use_fax(monster, macro):
    get_fax(monster)
    visit_url("inv_use.php", params = {"pwd": km.get_pwd_hash(), "whichitem": 4873})
    run_combat(macro)
    if which_choice() == 1387:
        print("Using force yellow-ray")
        run_choice()
    
def get_fax_with_chat(monster):
    cli(f"ashq chat_private('cheesefax', '{monster}')")
    #need to receive fax still
    raise
    
def sausage_goblin_fight_up():
    """stolen from bean, who stole it from dictator"""
    goblins_fought = get_property_int("_sausageFights")
    last_sausage = get_property_int("_lastSausageMonsterTurn")
    guaranteed_sausage_adventure = last_sausage + 4 + goblins_fought * 3 + max(0, goblins_fought - 5) ** 3
    return (goblins_fought == 0) or (cli_int("total_turns_played") >= guaranteed_sausage_adventure)

def fight_sausage_goblin(macro):
    cli("familiar hobo monkey")
    maximize("meat drop, equip kramco")
    equip("Kramco")
    adv1("noob Cave", macro)
    
def fight_sausage_goblin_if_up(macro):
    if sausage_goblin_fight_up():
        fight_sausage_goblin(macro)
        return True
    else:
        return False
    
def boombox(song):
    if song == "meat":
        if km.get_property("boomBoxSong") != "Total Eclipse of Your Meat":
            cli("boombox meat")
    elif song in ["fists", "punching"]:
        if km.get_property('boomBoxSong') != "These Fists Were Made for Punchin'":
            cli("boombox fists")
    elif song == "food":
        if get_property('boomBoxSong') != "Food Vibrations":
            cli("boombox food")
    else:
        raise
        
def pull(item, price_limit = 50000):
    if cli_int(f"storage_amount {item}") == 0:
        cli(f"buy using storage {item} @{price_limit}")
    cli(f"pull {item}")
    
def wish_effect(effect, dur = 1):
    if have_effect(effect) >= dur:
        pass
    else:
        cli(f"genie effect {effect}")
    
def wish_fight(monster, macro):
    visit_url("inv_use.php", params = {"whichitem": 9537, "pwd": km.get_pwd_hash()}) #use pocket wish
    visit_url("choice.php", method = "post", data = {
        "pwd": km.get_pwd_hash(),
        "option": 1,
        "whichchoice": 1267,
        "wish": f"to fight {monster}"
    })
    #could go for a try-except in ash
    logging.info("Refressing main page to start genie combat?")
    visit_url("fight.php")
    sleep(0.1)
    assert(cli_int("current_round") > 0)
    run_combat(macro)
    assert(item_amount("candy cane") == 1)
    
class Macro:
    
    mark = 0
    
    def __init__(self):
        self.commands = []
        
    def __add__(self, other):
        result = Macro()
        result.commands = self.commands + other.commands
        return result
        
    def skill(self, skill):
        macro = Macro()
        macro.commands = [command for command in self.commands]
        macro.commands.append(f"if hasskill {skill}")
        macro.commands.append(f"skill {skill}")
        macro.commands.append("endif")
        return macro
    
    def attack(self):
        macro = Macro()
        macro.commands = [command for command in self.commands]
        macro.commands = self.commands
        macro.commands.append("attack")
        return macro
        
    def use(self, *items):
        macro = Macro()
        macro.commands = [command for command in self.commands]
        if len(items) == 1:
            macro.commands.append(f"use {items[0]}")
        elif len(items) == 2:
            macro.commands.append(f"use {items[0]}, {items[1]}")
        else:
            raise
        return macro
            
    def if_else(self, predicate, if_macro, else_macro = None):
        outer = Macro()
        outer.commands = [command for command in self.commands]
        outer.commands.append(f"if {predicate}")
        outer += if_macro
        if else_macro is not None:
            outer.commands.append(f"goto {self.mark}")
        outer.commands.append(f"endif")
        if else_macro is not None:
            outer += else_macro
            outer.commands.append(f"mark {self.mark}")
            self.increment_mark()
        return outer
    
    def _while(self, predicate, macro):
        outer = Macro()
        outer.commands = [command for command in self.commands]
        outer.commands.append(f"while {predicate}")
        outer += macro
        outer.commands.append(f"endwhile")
        return outer
    
    def repeat(self):
        macro = Macro()
        macro.commands = [command for command in self.commands]
        macro.commands.append("repeat")
        return macro
    
    def abort(self):
        macro = Macro()
        macro.commands = [command for command in self.commands]
        macro.commands.append("abort")
        return macro
        
    def macro(self):
        m = ";".join(self.commands)
        if '"' in m:
            logging.warn('" quotation mark found in macro, if not escaped properly, will cause errors')
        return m
    
    @classmethod
    def increment_mark(cls):
        cls.mark += 1
    
    def freeform(self, text):
        macro = Macro()
        macro.commands = [command for command in self.commands]
        macro.commands.append(text)
        return macro