#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#
# 4 hours remaining.
# For a new player, the game is confusing and difficult to understand.
# Solution: tutorial mode.
# Can it be done?

import pygame , time


import stats , extra , resource
import map_items
import game
from primitives import *
from game_types import *
from difficulty import DIFFICULTY


__tutor = None

def On(width: int) -> None:
    global __tutor
    __tutor = Tutor_Memory(width)

    Message(None, "welcome",
        "Welcome to 20,000 Light Years Into Space!",
        "You are playing the interactive tutorial. As you play, " +
        "information boxes like this one will appear on your screen. " +
        "When each message appears, read it, and then follow the " +
        "instructions that it provides.\n" +
        "To proceed, select the City, which is in the centre of the map.",
        False)


def City_Selected() -> None:
    Message("welcome", "citysel",
        "Your City",
        "To win the game, you must upgrade the city. Upgrades " +
        "raise the Technology Level of the City. Currently, the City " +
        "is at level 1 - you can see this on the right hand side of " +
        "the screen ('Tech Level'). When the City's Tech Level " +
        "reaches " + str(DIFFICULTY.CITY_MAX_TECH_LEVEL) + ", you win.\n" +
        "You can upgrade the City at any time, but you should wait " +
        "until you have secured some more supplies of steam.\n" +
        "Now click on the structure to the right of the City.",
        False)

def Steam_Maker_Selected(first: bool) -> None:
    if ( first ):
        Message("citysel", "steamsel",
            "The First Steam Maker",
            "You have just selected a Steam Maker. " +
            "Steam Makers are the " +
            "source of your steam supply. You'll need " +
            "to build more of these " +
            "in order to win the game, and you'll need " +
            "to connect them to your " +
            "city via Pipes.\n" +
            "Steam Makers have to be built on top of Steam " +
            "Sources. These are producing clouds of steam - " +
            "there are about ten of them, " +
            "dotted around the map.\n" +
            "Click 'Build Node', then click on one of the Steam " +
            "Sources. Ideally, you should choose one that's near the City.",
            False)
    else:
        Message("steamsel", "newsteam",
            "The New Steam Maker",
            "You've just built a new Steam Maker. " +
            "Or, more accurately, you've planned the construction " +
            "of a new Steam Maker. It won't actually be built until " +
            "it is connected by some Pipes to your City.\n" +
            "Your next job is to connect your Steam Maker to your City. " +
            "For this, you'll need to build a Pipe.\n" +
            "Click 'Build Pipe', then click first on the City, and " +
            "then on the new Steam Maker.",
            False)

def Pipe_Added() -> None:
    Message("newsteam", "building",
        "Building",
        "Now you've planned the beginnings of your network. " +
        "You have two Steam Makers, one operational, the other " +
        "under construction, and Pipes linking them to the City.\n" +
        "Please wait while the new Steam Maker is " +
        "built. While construction is in progress, try clicking on the " +
        "Pipes and the Steam Makers. You'll see some information about " +
        "them, including the progress of construction!",
        False)

def All_Nodes_Finished() -> None:
    Message("building", "nodesready",
        "Building Complete!",
        "Great! Your City is now supplied with Steam from two sources.\n" +
        "You can safely upgrade it now. Click 'Upgrade', and then " +
        "click on the City. The upgrade will begin immediately.",
        False)

def City_Upgrade_Running() -> None:
    Message("nodesready", "upgraderunning",
        "Upgrade In Progress",
        "The City upgrade is now in progress. As soon as you started " +
        "the upgrade, two things happened:\n" +
        "- You got an extra Work Unit. Now, two of your buildings " +
        "can be built simultaneously. Currently, one Work Unit is being " +
        "used to upgrade the City. The other one is spare.\n" +
        "- The City's steam requirement increased. Note the figures for " +
        "Supply and Demand on the right hand side. Demand has just " +
        "gone up. Fortunately, as you have two Steam Makers, Supply will " +
        "be able to match it.\n" +
        "Now you should strengthen your network. Later in the game, you'll " +
        "be under attack in a variety of nasty ways.\n" +
        "To do that, create a new Node somewhere between the two Steam " +
        "Makers. Nodes are just connection points. They store steam, " +
        "but they don't produce it or consume it.\n" +
        "Click 'Build Node' and then click on the position of " +
        "your new node.",
        False)

def Node_Selected() -> None:
    Message("upgraderunning", "makinglinks",
        "Making New Links",
        "Your network's strength depends on the number of links. " +
        "Generally, the more routes between two points, the better. The only " +
        "disadvantage of adding new routes is that they consume Work Units " +
        "during construction and repair. Don't worry about that for now.\n" +
        "Now build three new Pipes, each running " +
        "from your new Node: one to the City, and two for the two " +
        "Steam Makers. These connections make your network stronger. " +
        "Wait for these to be built.",
        False)

def Number_Of_Pipes_Is(pipe_count: int) -> None:
    if ( pipe_count >= 5 ):
        Message("makinglinks", "networkbasics",
            "Almost There...",
            "Excellent. Your network is now strong enough to withstand " +
            "attacks. You are almost ready to begin playing for real! " +
            "But before you do, you have to understand how steam flows. " +
            "Please click on one of the pipes.",
            False)

def Pipe_Selected() -> None:
    Message("networkbasics", "networkbasics2",
        "Steam is Water..",
        "To understand the network, it helps to imagine that the steam " +
        "is just (liquid) water. The City is like a drain: it is draining " +
        "water out of the system. The Steam Makers are like taps: they are " +
        "adding water to the system. In both cases, the flow rate " +
        "depends only on the amount of Upgrades you have applied.\n" +
        "Flow rates are given in Flow Units (U). Flow rates are represented " +
        "by the green dots that move along the pipes. The movement of the " +
        "dots is proportional to the velocity of the flow.\n" +
        "Now click on one of the nodes.",
        False)

def Any_Node_Selected() -> None:
    Message("networkbasics2", "networkbasics3",
        "Pressure..",
        "Water always finds it's own level. If you have two water tanks " +
        "and you connect them with a pipe, the water level will try to " +
        "equalise. The same effect happens here, but with steam.\n" +
        "All of the Nodes are steam storage tanks. The 'level' is " +
        "steam pressure. It is constantly trying to equalise.\n" +
        "Pressure is given in Pressure Units (P). " +
        "Now you've selected a Node, you can see its pressure on the right " +
        "hand side. Pressure is limited: to increase the limit, you can " +
        "upgrade the node, but there's no need to do that yet.\n" +
        "You lose the game if the pressure at the City falls too low (below " +
        str(PRESSURE_DANGER) + " P) for more than a certain " +
        "period of time (" + str(DIFFICULTY.GRACE_TIME) + " days, in " +
        "Beginner mode). To avoid that, ensure that Supply matches Demand.\n" +
        "We're almost done. Please click on a pipe again.",False)

def Pipe_Selected_2() -> None:
    Message("networkbasics3", "networkbasics4",
        "Rules Of Thumb",
        "The steam pressures in your Nodes will never equalise, because " +
        "steam is being added and removed from the network. However, you " +
        "may wonder why pressure and flow vary so much.\n" +
        "The answer is Resistance. Each pipe has only a limited capacity. " +
        "There's a limit to the rate at which steam can move, imposed " +
        "by each pipe. Resistance is a hidden property: you can't see " +
        "it, but it affects the game. Longer pipes have more resistance " +
        "than short ones.\n" +
        "All of this will reduce to a few rules of thumb.\n" +
        "- Build one Steam Maker per City Upgrade.\n" +
        "- Make lots of Pipes.\n" +
        "- Don't do an Upgrade unless the steam pressure at your City " +
        "is stable.\n" +
        "Now you're ready to experience an attack. Please click on your " +
        "City.", False)

def City_Selected_2() -> None:
    Message("networkbasics4", "attack",
        "Alien Attack",
        "The Aliens are coming!\n" +
        "You can't fight the aliens: all you can do is rebuild " +
        "your network. They'll try to destroy your Nodes and Pipes: " +
        "they'll only be able to put your Nodes out of action, but " +
        "they can destroy your Pipes.\n" +
        "The attack will last for two minutes. If sound is enabled, " +
        "you will hear an alarm " +
        "before each wave of alien attackers.\n" +
        "When you're ready for them, " +
        "click on the planet's surface.", False)

def Nothing_Selected() -> None:
    Message("attack", "running",
        "Alien Attack",
        "Remember:\n" +
        "- Rebuild Pipes that are destroyed by aliens.\n" +
        "- You can add new Pipes, Nodes, and Steam Makers.\n" +
        "- Your goal is always to upgrade the City.\n" +
        "The Aliens disappear after 2 minutes. Good luck." , True)


def Aliens_Gone() -> None:
    Message("running", "ended",
        "You Survived",
        "Good work! You survived the attack.\n" +
        "Now you are ready to play for real. Now click " +
        "'Exit to Main Menu' and begin your first game!\n" +
        "Good luck, and have fun.", True)




def Notify_Select(item: Optional[map_items.Item]) -> None:
    global __tutor
    if ( __tutor is None ):
        return

    if ( isinstance(item, map_items.Node) ):
        Any_Node_Selected()


    if ( isinstance(item, map_items.City_Node) ):
        City_Selected()
        City_Selected_2()
    elif ( isinstance(item, map_items.Well_Node) ):
        first = item.tutor_special
        Steam_Maker_Selected(first) # note change of terminology :(
    elif ( isinstance(item, map_items.Node) ):
        Node_Selected()
    elif ( isinstance(item, map_items.Pipe) ):
        Pipe_Selected()
        Pipe_Selected_2()
    elif ( item is None ):
        Nothing_Selected()

def Notify_Add_Pipe() -> None:
    global __tutor
    if ( __tutor is None ):
        return

    Pipe_Added()

def Notify_Add_Node(n: map_items.Item) -> None:
    global __tutor
    if ( __tutor is None ):
        return

    #Node_Added(n)

def Examine_Game(g: "game.Game_Data") -> None:
    global __tutor
    if ( __tutor is None ):
        return

    # test 1 - are all nodes finished?
    all_finished = True
    for n in g.net.node_list:
        all_finished = all_finished and ( not n.Needs_Work() )

    if ( all_finished ):
        All_Nodes_Finished()

    # test 2 - has the city begun an upgrade?
    if ( g.net.hub.city_upgrade != 0 ):
        City_Upgrade_Running()

    # test 3 - number of pipes.
    pipe_count = 0
    for p in g.net.pipe_list:
        if (( not p.Is_Destroyed() ) and ( not p.Needs_Work() )):
            pipe_count += 1

    # test 4 - season
    if ( g.season in [ Season.STORM , Season.QUAKE ] ):
        Aliens_Gone()
        g.game_running = False

    Number_Of_Pipes_Is(pipe_count)

def Off() -> None:
    global __tutor
    __tutor = None

def Message(previous_msg_name: Optional[str], this_msg_name: str,
            title: str, text: str, sf: bool) -> None:
    global __tutor
    t = __tutor
    if ( t is not None ):
        t.Add_Message((previous_msg_name, this_msg_name,
                title, text, sf))

def Draw(screen: SurfaceType, g: "game.Game_Data") -> None:
    global __tutor
    t = __tutor
    if ( t is not None ):
        t.Draw(screen, g)

def Permit_Season_Change() -> bool:
    global __tutor
    t = __tutor
    if ( t is not None ):
        return t.Permit_Season_Change()
    else:
        return True

def Frozen() -> bool:
    return False

def Active() -> bool:
    global __tutor
    return ( __tutor is not None )

def Has_Changed() -> bool:
    global __tutor
    t = __tutor
    if ( t is not None ):
        x = t.update
        t.update = False
        return x
    else:
        return False


class Tutor_Memory:
    def __init__(self, w: int) -> None:
        self.current_msg_name: Optional[str] = None
        self.current_msg_surf: Optional[SurfaceType] = None
        self.current_msg_popup = False
        self.width = w
        self.update = False
        self.permit_season_change = False

    def Add_Message(self, arg: Tuple[Optional[str], str, str, str, bool]) -> None:
        (previous_msg_name, this_msg_name, title, text, sf) = arg

        if ( self.current_msg_name == previous_msg_name ):
            self.current_msg_name = this_msg_name
            self.current_msg_surf = self.__Draw(title, text)
            self.current_msg_popup = True
            self.update = True
            self.permit_season_change = sf

    def Permit_Season_Change(self) -> bool:
        return self.permit_season_change

    def Draw(self, screen: SurfaceType, g: "game.Game_Data") -> None:
        if ( self.current_msg_popup and ( self.current_msg_surf is not None )):
            r = self.current_msg_surf.get_rect()
            r.top = r.left = 30
            screen.blit(self.current_msg_surf, r)

    def __Draw(self, title: str, text: str) -> SurfaceType:
        height = 10
        (surf, height) = self.__Draw_H(title, text, height)
        (surf, height) = self.__Draw_H(title, text, height)
        return surf

    def __Draw_H(self, title: str, text: str, height: int) -> Tuple[SurfaceType, int]:
        width = self.width
        margin = 10
        fs1 = 12
        fs2 = 14
        newline_gap = 12

        surf = pygame.Surface((width, height))
        bbox = surf.get_rect()
        extra.Tile_Texture(surf, "006metal.jpg", bbox)

        tsurf = stats.Get_Font(fs1).render(title, True, (250,250,200))
        tsurf_r = tsurf.get_rect()
        tsurf_r.center = bbox.center
        tsurf_r.top = margin

        surf.blit(tsurf, tsurf_r.topleft)

        y = tsurf_r.bottom + margin
        # line edging for title
        extra.Line_Edging(surf, pygame.Rect(0,0,width,y), True)

        y += margin
        x = margin
        height = y

        while ( len(text) != 0 ):
            newline = False
            i = text.find(' ')
            j = text.find("\n")

            if (( j >= 0 ) and ( j < i )):
                i = j
                newline = True

            if ( i < 0 ):
                i = len(text)

            word = text[ : i ] + " "
            text = text[ i + 1 : ].lstrip()

            tsurf = stats.Get_Font(fs2).render(word, True, (250,200,250))
            tsurf_r = tsurf.get_rect()
            tsurf_r.topleft = (x,y)
            if ( tsurf_r.right > ( width - 5 )):
                # Wrap.
                y += tsurf_r.height
                x = margin
                tsurf_r.topleft = (x,y)

            surf.blit(tsurf, tsurf_r.topleft)
            x = tsurf_r.right
            height = tsurf_r.bottom + margin

            if ( newline ):
                x = margin
                y = tsurf_r.bottom + newline_gap

        # line edging for rest of box
        extra.Line_Edging(surf, bbox, True)

        return (surf, height)



