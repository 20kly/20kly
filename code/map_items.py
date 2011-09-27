# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# Items that you will find on the map.
# All inherit from the basic Item.

import pygame 
from pygame.locals import *

import bresenham, intersect, extra, stats, resource, draw_obj 
import sound, trig, steam_model, work, newui
from primitives import *
from colours import *
from mail import New_Mail

# Cris Grada's new icons
IC = "icons.png"        # g4018.png, 26/05/2011
ICG = "iconsg.png"      # same, but greyscale


DOT_SPACING = FPX
DOT_VELOCITY_FACTOR = FPX * 100

__uid = 0

def Get_UID():
    global __uid
    __uid += 1
    return "tm%X" % __uid

def Delete_Factory(net, parent):
    
    def Delete():
        net.Destroy(parent)

    return Delete

class Item:
    def __init__(self):
        self.pos = None
        self.name_type = "?"
        self.draw_obj = None
        self.emits_steam = False
        self.tutor_special = False
        self.work_gradient = 0
        self.uid = Get_UID()

    def Draw(self, output):
        self.draw_obj.Draw(output, self.pos, (0,0))

    def Draw_Selected(self, output, highlight):
        return None

    def Get_Popup_Menu(self, net):
        return None

    def Prepare_To_Die(self):
        pass

    def Take_Damage(self, dmg_level=1):
        # Basic items have no health and therefore can't be damaged
        return False

    def Is_Destroyed(self):
        return False

    def Sound_Effect(self):
        pass

    def Debug(self):
        print 'default'

class Well(Item):
    def __init__(self, (x,y)):
        Item.__init__(self)
        self.pos = (x,y)
        self.draw_obj = draw_obj.Grid_Draw_Obj("well.png", None, 1)
        self.emits_steam = True

class Building(Item):
    def __init__(self):
        Item.__init__(self)
        self.health = 0
        self.complete = False
        self.was_once_complete = False
        self.max_health = work.BASE_NODE_WORK
        self.base_colour = WHITE
        self.connection_value = 0
        self.other_item_stack = []
        self.popup_disappears_at = 0
        self.destroyed = False
        self.tech_level = 1
        self.transfer = 0

    def Prepare_To_Die(self):
        self.popup_disappears_at = 0
        self.health = 0
        self.destroyed = True

    def Take_Damage(self, dmg_level=1):
        x = int(dmg_level * DIFFICULTY.DAMAGE_FACTOR)
        self.health -= x
        if ( self.health <= 0 ):
            self.Prepare_To_Die()
            return True
        return False

    def Do_Upgrade(self):
        pass

    def Save(self, other_item):
        # Used for things that stack on top of other things,
        # e.g. steam maker on top of well
        assert isinstance(other_item, Item)
        assert other_item.pos == self.pos
        self.other_item_stack.append(other_item)

    def Restore(self):
        if ( len(self.other_item_stack) != 0 ):
            return self.other_item_stack.pop()
        else:
            return None

    def Is_Destroyed(self):
        return self.destroyed
    
    def Needs_Work(self):
        return ( self.max_health != self.health ) and not self.destroyed
        
    def Is_Broken(self):
        return self.Needs_Work()

    def Do_Work(self):
        """A single unit of work is applied here."""
        if self.destroyed:
            self.health = 0
        else:
            self.health = min(self.health + work.WORK_UNIT_SIZE, 
                        self.max_health)
            if self.health == self.max_health:
                self.complete = True
                self.was_once_complete = True
                return True # Work done!

        return False

    def Get_Popup_Menu(self, net):
        return None

    def Get_Level_Data(self):
        return (str(self.tech_level), WHITE)

    def Get_Health_Data(self):
        return (str(self.health), self.Get_Health_Colour())

    def Get_Health_Colour(self):
        percent = (self.health * 100) / self.max_health
        if percent < 25:
            colour = RED
        elif percent < 50:
            colour = ORANGE
        elif percent < 75:
            colour = YELLOW
        elif percent < 100:
            colour = ORANGE_GREEN
        else:
            colour = GREEN

        return colour

    def Get_Health_Bar(self):
        return (self.health, self.max_health, self.Get_Health_Colour())

    def Get_Transfer_Data(self):
        return (str(self.transfer), WHITE)

    def Get_Transfer_Bar(self):
        assert False    # Not valid - no maximum transfer

    def Do_Upgrade(self):
        assert False    # Not an upgradeable building

class Node_Popup(newui.Popup_Menu):
    def __init__(self, parent, net, caption = "Node", 
                transfer_name = "Transfer", has_max_transfer = False,
                can_delete = True, can_upgrade = False):
        newui.Popup_Menu.__init__(self, DARK_BLUE, RED_YELLOW)

        # Caption
        self.Add_To_Layout(newui.Label_Item(caption, WHITE))
        self.Add_To_Layout(newui.Space_Item(5))

        # Information about the node
        self.Add_To_Layout(newui.Data_Label_Item("Tech Level", WHITE,
                            parent.Get_Level_Data))
        self.Add_To_Layout(newui.Space_Item(1))

        self.Add_To_Layout(newui.Data_Label_Item(transfer_name, WHITE,
                            parent.Get_Transfer_Data))
        if has_max_transfer:
            self.Add_To_Layout(newui.Bar_Item(BAR_BACK_COLOUR, 
                                parent.Get_Transfer_Bar))
        self.Add_To_Layout(newui.Space_Item(1))

        self.Add_To_Layout(newui.Data_Label_Item("Integrity", WHITE,
                            parent.Get_Health_Data))
        self.Add_To_Layout(newui.Bar_Item(BAR_BACK_COLOUR, 
                            parent.Get_Health_Bar))
        self.Add_To_Layout(newui.Space_Item(1))

        # Controls
        buttons = []
        if can_delete:
            buttons.append(newui.Button_Item(
                    "destroy.png", None, Delete_Factory(net, parent)))
        if can_upgrade:
            buttons.append(newui.Button_Item(
                        "upgrade.png", None, parent.Do_Upgrade))

        if len(buttons) != 0:
            self.Add_To_Layout(newui.Button_Group_Item(buttons))


class Node(Building):
    def __init__(self, (x,y)):
        Building.__init__(self)
        self.pipes = []
        self.pos = (x,y)
        self.base_colour = RED_YELLOW
        r = Rect(0, 154, 35, 35)
        self.draw_obj_finished = draw_obj.Grid_Draw_Obj(IC, r, 1)
        self.draw_obj_incomplete = draw_obj.Grid_Draw_Obj(ICG, r, 1)
        self.draw_obj = self.draw_obj_incomplete
        self.work_units = 0

    def Debug(self):
        print 'transfer', self.transfer

    def Get_Popup_Menu(self, net):
        return Node_Popup(self, net, caption = "Node", 
                    transfer_name = "Steam Transfer", 
                    has_max_transfer = False,
                    can_delete = True, 
                    can_upgrade = (self.tech_level < NODE_MAX_TECH_LEVEL))

    def Do_Upgrade(self):
        if ( self.tech_level >= NODE_MAX_TECH_LEVEL ):
            New_Mail("Node cannot be upgraded further.")
            sound.FX("error")
        elif ( self.Needs_Work() ):
            New_Mail("Node must be operational before an upgrade can begin.")
            sound.FX("error")
        else:
            sound.FX("crisp")

            # Upgrade a node to get a higher capacity and more health.
            # More health means harder to destroy.
            # More capacity means your network is more resilient.
            self.tech_level += 1
            self.max_health += NODE_UPGRADE_WORK * HEALTH_UNIT
            self.complete = False

    def Compute(self):
        if self.Is_Broken():
            self.draw_obj = self.draw_obj_incomplete
        else:
            self.draw_obj = self.draw_obj_finished

    def Draw_Selected(self, output, highlight):
        ra = ( Get_Grid_Size() / 2 ) + 4
        pygame.draw.circle(output, highlight,
                        Grid_To_Scr(self.pos), ra , 2 )
        return Grid_To_Scr_Rect(self.pos).inflate(ra,ra)

    def Sound_Effect(self):
        sound.FX("bamboo")

    def Draw(self, output):
        self.draw_obj.Draw(output, self.pos, (0,0))

class City_Node(Node):
    def __init__(self,(x,y)):
        Node.__init__(self, (x,y))
        self.base_colour = CITY_COLOUR

        self.draw_obj = draw_obj.Grid_Draw_Obj(IC,
                        Rect(45, 98, 45, 48), 3)
        self.draw_obj_finished = self.draw_obj_incomplete = self.draw_obj

        self.work_unit_manufacture = 0
        self.reserve_kept = 0
        self.city_rank = 0
        self.population = 100
        self.steam_total = (self.population * 
                    steam_model.PERSON_STEAM * steam_model.CONSERVATISM)

    def Get_Popup_Menu(self, net):
        return Node_Popup(self, net, caption = "City", 
                    transfer_name = "Steam Usage", 
                    has_max_transfer = False,
                    can_delete = True, 
                    can_upgrade = False)

    def Compute_City(self, net):
        # New steam added
        self.steam_total += self.transfer

        # What do we spend steam on?
        # 1. Life support
        life_support = self.population * steam_model.PERSON_STEAM

        if self.steam_total < life_support:
            # The city depopulates.
            # (Nothing horrible happens, they just move away!!!)
            new_pop = max(1, 
                    self.steam_total / steam_model.PERSON_STEAM)
            emigrants = self.population - new_pop
            net.Add_Emigrants(emigrants)
            self.population = new_pop
            self.city_rank = 0

        self.steam_total = max(self.steam_total - life_support, 0)

        # 2. Manufacture of work units
        self.work_unit_manufacture += self.population

        while ((self.work_unit_manufacture >= work.WORK_UNIT_SIZE)
        and (self.steam_total >= steam_model.WORK_UNIT_STEAM)
        and (self.work_units < work.MAX_WORK_UNITS_AT_NODE)):
            net.Work_Generate(self)
            self.work_unit_manufacture -= work.WORK_UNIT_SIZE
            self.steam_total -= steam_model.WORK_UNIT_STEAM

        # 3. Steam reserves
        self.reserve_kept = (self.population * 
                    steam_model.PERSON_STEAM * steam_model.CONSERVATISM)
        if self.reserve_kept <= self.steam_total:
            # Do nothing else until reserves are full
            can_spend = 0
        else:
            can_spend = self.steam_total - self.reserve_kept
            self.steam_total = self.reserve_kept

        # 4. Luxury spending
        self.city_rank = ((self.city_rank * 99) + (can_spend * 1)) / 100

    def Needs_Work(self):
        return False

    def Is_Broken(self):
        return False

    def Do_Work(self):
        return False

    def Take_Damage(self, dmg_level=1):  # Can't destroy a city.
        return False

    def Draw_Selected(self, output, highlight):
        r = Grid_To_Scr_Rect(self.pos).inflate(CITY_BOX_SIZE,CITY_BOX_SIZE)
        pygame.draw.rect(output, highlight,r,2)
        return r.inflate(2,2)

    def Sound_Effect(self):
        sound.FX("computer")

    def Draw(self, output):
        self.draw_obj.Draw(output, self.pos, (0,0))



class Well_Node(Node):
    def __init__(self,(x,y)):
        Node.__init__(self, (x,y))
        self.base_colour = WHITE
        r = Rect(49, 154, 36, 35)
        self.draw_obj_finished = draw_obj.Grid_Draw_Obj(IC, r, 1)
        self.draw_obj_incomplete = draw_obj.Grid_Draw_Obj(ICG, r, 1)
        self.draw_obj = self.draw_obj_incomplete
        self.emits_steam = True

    def Sound_Effect(self):
        sound.FX("bamboo1")

    def Get_Current_Limit(self):
        return steam_model.BASE_WELL_PRODUCTION

    def Get_Popup_Menu(self, net):
        return Node_Popup(self, net, caption = "Steam Well", 
                    transfer_name = "Production", 
                    has_max_transfer = True,
                    can_delete = True, 
                    can_upgrade = False)

    def Get_Transfer_Bar(self):
        return (self.transfer, steam_model.BASE_WELL_PRODUCTION, CYAN)





class Pipe_Popup(newui.Popup_Menu):
    def __init__(self, parent, net):
        newui.Popup_Menu.__init__(self, VERY_DARK_GREEN, RED_YELLOW)

        # As a mark of respect to our ancestors we shall use only
        # 19th century British measurements. 
        yards = (parent.length_fp * 250) >> FPS

        # Caption
        self.Add_To_Layout(newui.Label_Item("%u yard pipe" % yards, WHITE))
        self.Add_To_Layout(newui.Space_Item(5))

        # Information about the pipe
        self.Add_To_Layout(newui.Data_Label_Item("Pipe Gauge", WHITE,
                            parent.Get_Level_Data))
        self.Add_To_Layout(newui.Space_Item(1))

        self.Add_To_Layout(newui.Data_Label_Item("Transfer", WHITE,
                            parent.Get_Transfer_Data))
        self.Add_To_Layout(newui.Bar_Item(BAR_BACK_COLOUR, 
                            parent.Get_Transfer_Bar))
        self.Add_To_Layout(newui.Space_Item(1))

        self.Add_To_Layout(newui.Data_Label_Item("Energy Loss", WHITE,
                            parent.Get_Loss_Data))
        self.Add_To_Layout(newui.Bar_Item(BAR_BACK_COLOUR, 
                            parent.Get_Loss_Bar))
        self.Add_To_Layout(newui.Space_Item(1))

        self.Add_To_Layout(newui.Data_Label_Item("Integrity", WHITE,
                            parent.Get_Health_Data))
        self.Add_To_Layout(newui.Bar_Item(BAR_BACK_COLOUR, 
                            parent.Get_Health_Bar))
        self.Add_To_Layout(newui.Space_Item(1))

        # Controls
        buttons = []
        buttons.append(newui.Button_Item(
                    "destroy.png", None, Delete_Factory(net, parent)))
        if parent.tech_level < len(steam_model.PIPE_CURRENT_LIMIT):
            buttons.append(newui.Button_Item(
                        "upgrade.png", None, parent.Do_Upgrade))

        self.Add_To_Layout(newui.Button_Group_Item(buttons))

class Pipe(Building):
    def __init__(self,n1,n2):
        Building.__init__(self)
        assert n1 != n2
        n1.pipes.append(self)
        n2.pipes.append(self)
        self.n1 = n1
        self.n2 = n2
        (x1,y1) = n1.pos
        (x2,y2) = n2.pos
        self.pos = ((x1 + x2) / 2, (y1 + y2) / 2)
        self.length_fp = trig.Distance((x1 - x2) << FPS, (y1 - y2) << FPS)
        self.length = self.length_fp >> FPS
        self.max_health = (self.length_fp * work.BASE_PIPE_WORK) >> FPS
        self.velocity = 0 # n.b. velocity towards self.n2

        self.base_colour = DARK_GREEN
        self.trans_colour = self.Get_Transfer_Colour()

        self.pipe_loss = self.max_pipe_loss = 0
        self.dot_drawing_offset = 0

    def Get_Popup_Menu(self, net):
        return Pipe_Popup(self, net)

    def Get_Transfer_Data(self):
        return (str(abs(self.velocity)), self.trans_colour)

    def Get_Transfer_Bar(self):
        return (abs(self.velocity), self.Get_Current_Limit(), 
                self.trans_colour)

    def Get_Loss_Data(self):
        return (str(self.pipe_loss), self.trans_colour)

    def Get_Loss_Bar(self):
        return (self.pipe_loss, self.max_pipe_loss, 
                self.trans_colour)

    def Split(self, new_node):
        """Pipe is split at new_node. The caller will have
        checked that new_node is in the right place."""

        pipe1 = Pipe(self.n1, new_node)
        pipe2 = Pipe(new_node, self.n2)

        for p in [pipe1, pipe2]:
            p.tech_level = self.tech_level
            p.health = max(0, min(self.max_health - 1,
                    ((self.health * p.max_health) / self.max_health) - 1))

        self.health = 0
        return (pipe1, pipe2)

    def Do_Upgrade(self):
        pass

    def Take_Damage(self, dmg_level=1):
        # Pipes have health proportional to their length.
        # To avoid a rules loophole, damage inflicted on
        # pipes is multiplied by their length. Pipes are
        # a very soft target.
        return Building.Take_Damage(self, dmg_level * (self.length + 1))

    def Get_Transfer_Colour(self):
        target = (abs(self.velocity) * 100) / self.Get_Current_Limit()
        for (rf, total, colour) in steam_model.SUB_PIPES:
            target -= total
            if target <= 0:
                return colour

        return colour

    def Draw(self,output):
        """Pipe drawn on the given surface in the correct place."""
        pos_a = Grid_To_Scr(self.n1.pos)
        pos_b = Grid_To_Scr(self.n2.pos)
        if self.Needs_Work():
            # Plain red line
            pygame.draw.line(output, RED, pos_a, pos_b, 3)
            self.dot_drawing_offset = 0
            return


        # Backing line colour depends on current limit
        colour = self.Get_Transfer_Colour()
        (r, g, b) = colour
        self.trans_colour = (min(r * 2, 255),
                min(g * 2, 255),
                min(b * 2, 255))

        pygame.draw.line(output, colour, pos_a, pos_b, 3)

        if self.velocity == 0:
            # No dots if no movement
            return

        # The moving-dots feature was not in the game until suggested 
        # by Tom Dalton, though another person did independently
        # contribute a similar patch.
        colour = DOT_COLOUR
        r = Rect(0, 0, 1, 1)

        for interp in xrange(self.dot_drawing_offset, 
                            self.length_fp, DOT_SPACING):
            pos = extra.Partial_Vector(pos_a, pos_b, (interp, self.length_fp)) 
            r.center = pos
            output.fill(colour, r)


    def Frame_Advance(self):
        """Dots are advanced along the pipe in accordance with the speed."""

        self.dot_drawing_offset += ((DOT_VELOCITY_FACTOR * self.velocity) >> FPS)
        self.dot_drawing_offset %= DOT_SPACING

    def Make_Ready_For_Save(self):
        pass

    def __Draw_Original(self, output):
        (x1,y1) = Grid_To_Scr(self.n1.pos)
        (x2,y2) = Grid_To_Scr(self.n2.pos)
        if ( self.Needs_Work() ):
            c = RED
        else:
            c = self.Get_Diagram_Colour()
        pygame.draw.line(output, c, (x1,y1), (x2,y2), 2)

    def Draw_Selected(self, output, highlight):
        p1 = Grid_To_Scr(self.n1.pos)
        p2 = Grid_To_Scr(self.n2.pos)
        pygame.draw.line(output, highlight, p1, p2, 5)
        #self.Draw(output) # Already done elsewhere.

        return Rect(p1,(1,1)).union(Rect(p2,(1,1))).inflate(7,7)

    def Sound_Effect(self):
        sound.FX("bamboo2")

    def Debug(self):
        print 'speed', abs(self.velocity)

    def Get_Current_Limit(self):
        return steam_model.PIPE_CURRENT_LIMIT.get(self.tech_level, 0)

    def Get_Subpipes(self):
        resistance = self.length_fp / (steam_model.CONDUCTANCE.get(
                            self.tech_level, 1))
        current_limit = self.Get_Current_Limit()

        for (rf, l, _) in steam_model.SUB_PIPES:
            yield (resistance * rf, (current_limit * l) / 100)



