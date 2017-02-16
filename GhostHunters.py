########################################################
#
# GhostHunters 1.0 Copyright (C) RVJ Callanan 2012
#
# This is FREE software, licensed under the GNU GPLv3
# See: <http://www.gnu.org/licenses/>.
#
########################################################


########################################################
# Imports
########################################################

from turtle import *
from math import *
from random import *
from sys import *
from winsound import *

########################################################
# Constants
########################################################

XMIN = -200                 # left-most 
XMAX =  200                 # right-most
YMIN = -200                 # top-most
YMAX =  200                 # bottom-most

LEVEL_TICKS = 1000          # Clock ticks per level
MAX_TICKS = 5 * LEVEL_TICKS # Game never goes beyond this point

STATUS_TICKS = 10           # Controls persistence of status message

MAX_FUEL = 5000             # Capacity of fuel tank
FULL_FUEL = MAX_FUEL - 10   # Full fuel indicator threshold
TICK_FUEL = 1               # Fuel used in normal motion
TURN_FUEL = 50              # Fuel used in single rotate

FUEL_WARN = 200             # Low Fuel Warn Threshold
FUEL_ALERT = 50             # Low Fuel Alert Threshold

BONUS_FUEL = 1000           # Bonus fuel at each new level 
TOPUP_FUEL = 100            # Fuel topup amount

TOPUP_COST_L0 = 100         # Fuel topup cost (level 0)
TOPUP_COST_L4 = 500         # Fuel topup cost (level 4)

HIT_BOUNTY_L0 = 500         # Hit bounty (level 0)
HIT_BOUNTY_L4 = 2500        # Hit bounty (level 4)

RAND_TICKS = 10             # Randomiser interval

RAND_CHANCE_L0 = 20         # Randomiser chance (level 0)
RAND_CHANCE_L4 = 40         # Randomiser chance (level 4)

GI_CHANCE_L0 = 5            # Chance of ghost being invisible (level 0) 
GI_CHANCE_L4 = 25           # Chance of ghost being invisible (level 4)

GE_CHANCE_L0 = 20           # Chance of ghost being energised (level 0) 
GE_CHANCE_L4 = 40           # Chance of ghost being energised (level 4)

GE_MIN_PROX_L0 = 9          # Min ghost proximity to energise (level 0)
GE_MIN_PROX_L4 = 5          # Min ghost proximity to energise (level 4)

GH_CHANCE_L0 = 20           # Chance of ghost heading change (level 0) 
GH_CHANCE_L4 = 40           # Chance of ghost heading change (level 4)

GJ_CHANCE_L0 = 20           # Chance of ghost jump (level 0) 
GJ_CHANCE_L4 = 40           # Chance of ghost jump (level 4)

GJ_MIN_L0 = 20              # Min ghost jump proximity (level 0)
GJ_MAX_L0 = 50              # Max ghost jump proximity (level 0)

GJ_MIN_L4 = 28              # Min ghost jump proximity (level 4)
GJ_MAX_L4 = 90              # Max ghost jump proximity (level 4)

GR_L0 = 60                  # Ghost radius (level 0)
GR_L4 = 20                  # Ghost radius (level 4)

CENTER_WEIGHT = 50          # Percentage difficulty reduction at centre
                            # For weighted parameters only

########################################################
# Global Variables
########################################################

state = "idle"      # game state
level = 0           # difficulty level
hits = 0            # total ghosts hit
cash = 0            # net earnings
ticks = 0           # elapsed time
fuel = 0            # fuel in tank
used = 0            # amount of fuel used
spilled = 0         # amount of fuel spilled
bonuses = 0         # total fuel bonuses
topups = 0          # total top-ups
cash = 0            # net earnings
purchases = 0       # total purchases (fuel)
bounties = 0        # total bounty income
bounty = 0          # current bounty
topupcost = 0       # current topup cost
status = ""         # status message
statuscount = 0     # tracks status persistence
collision = False   # currently touching
fatal = False       # fatal collision

px = 0              # player X pos
py = 0              # player Y pos
pr = 0              # player radius
ph = 0              # player heading

gx = 0              # ghost X pos
gy = 0              # ghost Y pos
gr = 0              # ghost radius
gh = 0              # ghost heading
gv = False          # Ghost Visible
ge = False          # Ghost Energised

########################################################
# Functions
########################################################

def StartUp():

    setup (width=500, height=500)
    mode("logo")
    speed("fastest")
    ht()
    seth(90)
    color("green")
    tracer(0)

    onkey(KeySpace, "space")
    onkey(KeyLeft, "Left")
    onkey(KeyRight, "Right")
    onkey(KeyF2, "F2")
    onkey(KeyF3, "F3")
    
    title("Ghost Hunters")
    listen()

########################################################

def ShutDown():
    bye()
    quit()

########################################################

def HealthCheck():

    # Shuts down if strange behaviour detected.
    # Health checks should be done at critical
    # code sections and before every low-level
    # draw operation.
    
    # For example, if user closes window in middle
    # of game, it could cause spurious turtle window
    # to open with draw operations continuing as if
    # nothing happened. The easiest way to determine
    # if all is okay is to check turtle settings
    # that are set to non-defaults by StartUp()
    # and are never changed during normal execution.
    # If any of these have changed then we know that
    # a spurious Turtle screen has been activated.

    if mode() != "logo"     \
    or isvisible()          \
    or tracer() != 0:
        ShutDown()

########################################################

def SoundOver():
    Beep(1000,1000)

########################################################

def SoundError():
    Beep(2000,100)

########################################################

def SoundHit():
    Beep(500,100)

########################################################

def SoundNewLevel():
    Beep(5000,100)

########################################################
    
def DrawLine(x1,y1,x2,y2):
    
    HealthCheck()
    
    pu()
    goto(x1,y1)
    pd()
    goto(x2,y2)
    pu()

########################################################
    
def DrawRect(xmin,ymin,xmax,ymax):
    
    HealthCheck()
    
    pu()
    goto(xmin,ymax)
    pd()
    goto(xmax,ymax)
    goto(xmax,ymin)
    goto(xmin,ymin)
    goto(xmin,ymax)
    pu()

########################################################
    
def DrawCircle(x,y,r):
    
    HealthCheck()
    
    pu()
    goto(x,y-r)
    pd()
    circle(r)
    pu()

########################################################

def DrawPointer(x,y,h,r):

    # Draw dot within circle showing heading

    HealthCheck()

    a = radians(h)
    
    dx = round(cos(a)*0.7*r)
    dy = round(sin(a)*0.7*r)
    
    pu()
    goto(x+dx,y+dy)
    pd()
    dot()
    pu()

########################################################

def DrawText(x,y,t,align):

    HealthCheck()
    
    pu()
    goto(x,y-8)
    write(t, False, align)
    pu()

########################################################
    
def DrawWall():
    
    color("blue")
    DrawRect(XMIN,YMIN,XMAX,YMAX)

########################################################

def DrawPlayer():

    if fuel > FULL_FUEL:
        f = "FULL"
    else:
        f = fuel

    SetPlayerColor()
        
    DrawCircle(px,py,pr)
    DrawPointer(px,py,ph,pr)
    DrawText(px,py,f,"center")

########################################################

def DrawGhost():

    # Only draw ghost if currently visible
    
    if gv:
        SetGhostColor()
        DrawCircle(gx,gy,gr)

########################################################

def DrawLevel():
    
    color("blue")
    DrawText(XMIN,YMAX+10, "Level " + str(level) + ": " + format(ticks,'04d'), "left")

########################################################

def DrawPrompt(prompt):
    
    color("red")
    DrawText(0,YMAX+10, prompt, "center")
    
########################################################

def DrawCash():
    
    color("blue")
    DrawText(XMAX,YMAX+10, "Cash = €" + format(cash,','), "right")

########################################################

def DrawBounty():
    
    color("blue")
    DrawText(XMIN,YMIN-10, "Bounty = €" + format(bounty,','), "left")

########################################################

def DrawStatus():
    
    color("red")
    DrawText(0,YMIN-10, status, "center")

########################################################

def DrawTopupCost():
    
    color("blue")
    DrawText(XMAX,YMIN-10, "Topup = €" + format(topupcost,','), "right")

########################################################

def DrawHelp():
    
    color("blue")
    DrawText(0,180,"GHOST HUNTERS 1.0","center")
    DrawText(0,160,"by Roger and David Callanan","center")

    color("grey30")
    DrawText(0,130,"INSTRUCTIONS","center")
    DrawText(0,110,"You are a ghost hunter in a slow inertial world where direction means everything.", "center")
    DrawText(0,90,"You have to maximise your net earnings before your time or fuel run out.","center")
    DrawText(0,70,"Ghosts implode at the touch but they are elusive and your movement is restricted.","center")
    DrawText(0,50,"Each hit adds a bounty to your earnings, but fuel top-ups eat into your cash reserves.","center")
    DrawText(0,30,"When you complete each level, you get a fuel bonus but ghosts become more deceptive.","center")
    DrawText(0,10,"While bounties are more attractive, fuel prices rocket as global supplies run low.","center")
    DrawText(0,-10,"And the more you turn to give chase or avoid energised ghosts, the more fuel you use!","center")
    DrawText(0,-30,"This game is more about strategy, patience and economy than nimble fingers!","center")
    DrawText(0,-50,"Do you use inertia to save fuel and only attack ghosts within pouncing distance?","center") 
    DrawText(0,-70,"Do you use early earnings to stock up on fuel while it is still cheap?","center")
    DrawText(0,-90,"Do you later top-up your fuel using money you might not recover?","center")
    DrawText(0,-110,"Do you abandon the hunt and cash-in when you get a good run of luck?","center")

    color("darkgreen")
    DrawText(0,-140,"Press LEFT and RIGHT arrow keys to rotate and SPACE bar to top-up fuel","center")
    DrawText(0,-160,"Press F2 to pause/continue game or F3 to abandon hunt and cash-in","center")
    DrawText(0,-180,"Watch your fuel readout. You turn sickly green when fuel is low!","center")
    DrawText(0,-200,"Beware of fuel spillage when level bonuses and top-ups overflow a full tank!","center")
    DrawText(0,-220,"Hitting an energised ghost (red) wipes out all your fuel and cash","center")

########################################################

def DrawStats():
    
    color("blue")

    DrawText(0,160,"YOUR GAME STATS","center")
    
    DrawText(-100,120,"Net Earnings","left")
    DrawText(100,120,"€" + format(cash,','),"right")
    
    DrawText(-100,100,"Bounty Income","left")
    DrawText(100,100,"€" + format(bounties,','),"right")

    DrawText(-100,80,"Average Bounty","left")
    DrawText(100,80,"-" if hits == 0 else "€" + format(round(bounties/hits),','),"right")

    DrawText(-100,60,"Fuel Costs","left")
    DrawText(100,60,"€" + format(purchases,','),"right")

    DrawText(-100,40,"Verified Hits","left")
    DrawText(100,40,hits,"right")

    DrawText(-100,20,"Hunting Time","left")
    DrawText(100,20,ticks,"right")

    DrawText(-100,0,"Level Reached","left")
    DrawText(100,0,level,"right")
 
    DrawText(-100,-20,"Fuel Economy (%)","left")
    DrawText(100,-20,str(round(100*ticks/used)),"right")   

    DrawText(-100,-40,"Fuel Used","left")
    DrawText(100,-40,used,"right")

    DrawText(-100,-60,"Fuel Bonuses (" + str(bonuses) + ")","left")
    DrawText(100,-60,bonuses*BONUS_FUEL,"right")

    DrawText(-100,-80,"Fuel Topups (" + str(topups) + ")","left")
    DrawText(100,-80,topups*TOPUP_FUEL,"right")

    DrawText(-100,-100,"Fuel Spilled","left")
    DrawText(100,-100,spilled,"right")

    DrawText(-100,-120,"Average Topup Cost","left")
    DrawText(100,-120, "-" if topups == 0 else "€" + str(round(purchases/topups)),"right")

    DrawText(-100,-140,"Excess Fuel","left")
    DrawText(100,-140,fuel,"right")

    DrawText(-100,-160,"Excess Time","left")
    DrawText(100,-160,MAX_TICKS-ticks,"right")

    if fatal:
        color("red")
        DrawText(0,-200,"Total Cash/Fuel wipeout due to FATAL hit!","center")
        return
    
    if cash != bounties - purchases:
        color("red")
        DrawText(0,-200,"ACCOUNTING ERROR - Send for the Auditors!","center")
        
########################################################

def SetGhostColor():

    # Energised Ghost is normally red but turns
    # pink after a hit (fatal). Unenergised ghost
    # color gets hazier as difficulty level increases

    if fatal:
        color("pink")
    elif ge:
        color("red")
    else:    
        if level == 0:
            color("grey70")
        elif level == 1:
            color("grey75")
        elif level == 2:
            color("grey80")
        elif level == 3:
            color("grey85")
        else:
            color("grey90")

########################################################

def SetPlayerColor():

    # Player color is normally healthy but flashes
    # red after a hit and turns blue after a fatal
    # hit. Shows increasingly unhealthy color as
    # fuel gets close to empty. This will prompt
    # player to top up before too late

    if fatal:
        color("blue")
    elif collision:
        color("red")
    else:
        if fuel > FUEL_WARN:
            color("darkgreen")
        elif fuel > FUEL_ALERT:
            color("green")
        else:
            color("lightgreen")

########################################################          

def UpdateStatus(msg = None):

    # Updates global status and statuscount
    # variables. If msg parameter is supplied,
    # it is applied immediately to the status
    # variable and statuscount is set to 1.
    # If msg is not supplied and a status message
    # is current, statuscount is incremented.
    # When statuscount exceeds STATUS_TICKS,
    # the status variables are cleared. In
    # this way, a status message will persist
    # long enough for player to see it on the
    # screen. This would not be possible if it
    # was displayed for only one tick cycle

    global status, statuscount

    if msg:
        status = msg
        statuscount = 1
        return
    
    if statuscount > 0:
        statuscount = statuscount + 1
        if statuscount <= STATUS_TICKS:
            return

    statuscount = 0
    status = ""

########################################################

def GetDistance(x1,y1,x2,y2):
    
    # Note this returns floating point number
    return sqrt((x1-x2)**2 + (y1-y2)**2)

########################################################

def Proximity():
    
    # Note this returns floating point number
    return GetDistance(px,py,gx,gy) - (pr+gr)

########################################################

def Lval(L0val,L4val):

    # Returns a value for current level based
    # on supplied level 0 and level 4 values.
    # Assumes values in between are proportional. 

    global level
    
    return L0val + round(level*(L4val - L0val)/4)

########################################################

def LvalWeighted(L0val,L4val):

    # Weighted version of Lval() function
    # Determines player distance from center
    # and weighs value accordingly. This can
    # be used to remove any advantage of
    # loitering at edges and corners. In fact
    # it should encourage player to stay near
    # centre. Of course, loitering near center
    # would use up too much fuel due to constant
    # turning so when weighting is applied, it
    # adds an interesting dimension to the game.

    global level
    
    val = L0val + round(level*(L4val - L0val)/4)

    # get max and actual player-to-centre distances

    maxp2c = GetDistance(0,0,XMAX,YMAX) - pr
    actp2c = GetDistance(0,0,px,py)

    # defined values apply at max distance from centre
    # reduce level value as player approaches centre

    weight = 1 - (1-CENTER_WEIGHT/100)*(maxp2c-actp2c)/(maxp2c)

    return round(weight*(L0val + level*(L4val - L0val)/4))

########################################################

def Spin(chance):

    # Returns True or False depending on the
    # value of the CHANCE parameter. This is
    # expressed as the percentage likelyhood.
    # A chance of 100 always returns True.
    # A chance of 0 always returns False.
  
    return randint(0,99) < chance 

########################################################

def Randomise():

    # Randomises game based on preset parameters.
    # Called regularly at randomiser ticks interval.

    global gx,gy,gh,gv,ge

    # Randomisation itself is subject to chance
    # This removes any time predictabilty

    chance = Lval(RAND_CHANCE_L0, RAND_CHANCE_L4)
    
    if Spin(chance) == False:
        return

    # Ghost invisibility is subject to chance.
    # Need to track when ghost re-appears to
    # force a position change (jump) later

    reappearing = False
    chance = Lval(GI_CHANCE_L0, GI_CHANCE_L4)

    if Spin(chance):
        gv = False
    else:
        if gv == False:
            reappearing = True
            gv = True
            
    # When ghost is invisible, other randomisations
    # are not necessary. But a reappearing ghost will
    # always safely re-position away from player
    
    if not gv:
        return

    # Ghost position jumps are subject to chance.
    # A reappearing ghost should also force a change
    # of position. In both cases, we must prevent
    # an "immediate" collision. However we don't
    # want to be too far away either. The jump
    # location is random but the min and max
    # distances from player are level dependent
    # AND weighted. We must also keep track of
    # jump to force heading randomisation later.

    jumping = False
    chance = Lval(GJ_CHANCE_L0, GJ_CHANCE_L4)
  
    if Spin(chance) or reappearing:

        jumping = True

        minjump = LvalWeighted(GJ_MIN_L0, GJ_MIN_L4)
        maxjump = LvalWeighted(GJ_MAX_L0, GJ_MAX_L4)

        while True:
            
            gx = randint(XMIN+gr,XMAX-gr)
            gy = randint(YMIN+gr,YMAX-gr)

            distance = Proximity()

            if distance >= minjump and distance <= maxjump:
                break

    # Chance of ghost heading change increases with level
    # But when it changes, equal chance in all directions.
    # Always force a heading randomisation when jumping

    chance = Lval(GH_CHANCE_L0, GH_CHANCE_L4)

    if Spin(chance) or jumping:
        gh = randint(0,7)*45

    # Ghost energisation is subject to chance but only
    # when ghost is not too close to player.

    minprox = Lval(GE_MIN_PROX_L0, GE_MIN_PROX_L4)

    if Proximity() >= minprox:
        
        chance = Lval(GE_CHANCE_L0, GE_CHANCE_L4)
        ge = Spin(chance)
        
########################################################

def PlotPlayer():
    
    global px,py,ph

    px,py,ph = PlotNext(px,py,ph,pr)

########################################################

def PlotGhost():
    
    global gx,gy,gh

    gx,gy,gh = PlotNext(gx,gy,gh,gr)

########################################################

def PlotNext(x,y,h,r):

    a = radians(h)
    
    dx = round(cos(a))
    dy = round(sin(a))

    cxmax = XMAX-r
    cxmin = XMIN+r

    cymax = YMAX-r
    cymin = YMIN+r

    if dx == 1:
        if x == cxmax:
            dx = -1
    elif dx == -1:
        if x == cxmin:
            dx = 1

    if dy == 1:
        if y == cymax:
            dy = -1
    elif dy == -1:
        if y == cymin:
            dy = 1

    x = x + dx
    y = y + dy

    if dx == 1:
        if dy == 0:
            h = 0
        elif dy == 1:
            h = 45
        else: # dy == -1
            h = 315
    elif dx == -1:
        if dy == 0:
            h = 180
        elif dy == 1:
            h = 135
        else:
            h = 225
    else: # dx == 0
        if dy == 1:
            h = 90
        else: # dy == -1
            h = 270

    return x,y,h

########################################################

def Rotate(h, direction):

    if direction == "left":
        h = h + 45
    else:
        h = h - 45

    if h < 0:
        h = h + 360

    if h >= 360:
        h = h - 360

    return h

########################################################

def RotatePlayer(direction):
    
    # Rotates player and depletes fuel.
    # Sound error if not enough fuel left.
    # In this case, all fuel is used up
    # but no rotation takes place.
    
    global ph

    if UseFuel(TURN_FUEL) < TURN_FUEL:
        SoundError()
    else:
        ph = Rotate(ph, direction)

########################################################

def UseFuel(qty):

    # Use up amount of fuel requested or empty
    # the tank. Returns amount actually used

    global fuel,used

    if fuel >= qty:
        f = qty
    else:
        f = fuel

    fuel = fuel - f
    used = used + f
    
    return f

########################################################

def AddFuel(qty):

    # Add amount of fuel specified. Anything
    # beyond the tank's capacity is spilled
    # Returns amount actually added

    global fuel,spilled

    if MAX_FUEL - fuel >= qty:
        f = qty
        s = 0
    else:
        f = MAX_FUEL - fuel
        s = qty - f
        UpdateStatus("SPILL")

    fuel = fuel + f
    spilled = spilled  + s
    
    return f

########################################################

def TopupFuel():
    
    # Top up fuel by sacrificing some earnings
    # Sounds error if not enough cash available
    # Topup cost increases with difficulty level
    # Note that topping up a tank that is full
    # or close to full simply causes a spillage

    global cash,topups,purchases

    if cash < topupcost:
        SoundError()
    else:
        cash = cash - topupcost
        purchases = purchases + topupcost
        topups = topups + 1
        AddFuel(TOPUP_FUEL)

########################################################

def KeySpace():

    if state != 'busy':
        return

    TopupFuel()

########################################################

def KeyLeft():
    
    if state != 'busy':
        return
    
    RotatePlayer("left")

########################################################

def KeyRight():
    
    if state != 'busy':
        return
    
    RotatePlayer("right")

########################################################

def KeyF2():
    
    # Starts, pauses or continues game
    
    global state
  
    if state == "ready":
        state = "busy"
    elif state == "busy":
        state = "pause"
    elif state == "pause":
        state = "busy"
    elif state == "recap":
        state = "idle"

########################################################

def KeyF3():
    
    # Enters game OVER state if game in progress
    # Otherwises enters EXITING state
    
    global state

    if state == "busy":
        state = "over"
    else:
        state = "exiting"

########################################################

def Tick():

    # Adds another tick to the game clock
    # and carry out any tick related tasks
    
    global ticks,level,collision,gr

    ticks = ticks + 1

    # Clear status and any other transient
    # global variables

    UpdateStatus()
    collision = False
    
    # Detect level transition
    # Allocate bonus fuel
    # Reduce ghost radius

    if level < 4:
        if ticks >= (level + 1) * LEVEL_TICKS:
            NewLevel()
    
    # Use up normal "ticking over" fuel

    UseFuel(TICK_FUEL)

    # Randomise at defined intervals
   
    if ticks % RAND_TICKS == 0:
        Randomise()

########################################################

def NewLevel():

    global level,bounty,topupcost,bonuses,gr
    
    level = level + 1
    SoundNewLevel()
    UpdateStatus("NEW LEVEL")

    # Add fuel bonus but causes spillage
    # if not enough tank capacity

    bonuses = bonuses + 1
    AddFuel(BONUS_FUEL)

    # Make bounty more attractive
            
    bounty = Lval(HIT_BOUNTY_L0,HIT_BOUNTY_L4)

    # Make cost of topping up fuel more penal
            
    topupcost = Lval(TOPUP_COST_L0,TOPUP_COST_L4)

    # Reduce ghost radius which also has the
    # nice side effect of not allowing a
    # collision to coincide with level change
    
    gr = Lval(GR_L0,GR_L4)

    # Re-seed random number generator
    
    seed()

########################################################

def PlotAndDetect():

    # Plots next positions of player and ghost
    # while also detecting collisions.

    global collision
   
    PlotPlayer()
    if gv and Proximity() < 0.5:
        collision = True
    else:  
        PlotGhost()
        if gv and Proximity() < 0.5:
            collision = True
 
    if collision:
        RegisterHit()

########################################################

def RegisterHit():

    # Hit is fatal when ghost is energised
    # Otherwise hit delivers bounty    

    global fatal,cash,fuel,hits,bounties

    if ge:
        fatal = True
        cash = 0
        fuel = 0
        return

    hits = hits + 1
    SoundHit()

    cash = cash + bounty
    bounties = bounties + bounty
    UpdateStatus("HIT")

########################################################

def StateIdle():

    # IDLE state occurs at game start and restart.
    # Seeds/re-seeds random number generator.
    # Initialises global game variables.
    # Shows basic help screen
    # Enters READY state.

    global state,level,ticks
    global fuel,used,spilled,bonuses,topups,cahs,purchases,bounties
    global bounty,topupcost
    global collision,fatal,status,statuscount
    global px,py,pr,ph
    global gx,gy,gr,gh,gv,ge

    seed()

    level = 0
    hits = 0
    ticks = 0
    fuel = BONUS_FUEL
    used = 0
    spilled = 0
    bonuses = 1
    topups = 0
    cash = 0
    purchases = 0
    bounties = 0
    bounty = HIT_BOUNTY_L0
    topupcost = TOPUP_COST_L0
    status = ""
    statuscount = 0
    collision = False
    fatal = False
    
    px = 0
    py = 100
    pr = 50
    ph = 90
 
    gx = 0
    gy = -100
    gr = GR_L0
    gh = 270
    gv = True
    ge = False
    
    clear()
    
    DrawPrompt("F2=Start F3=Exit")
    DrawHelp()

    state = "ready"

########################################################

def StateReady():

    # READY state leaves help information on
    # screen and remains in READY state until
    # user starts or restarts game

    pass

########################################################

def StateBusy():

    # BUSY state performs active game processing
    # until game is paused, abandoned or expired

    global state,gv
 
    Tick()
    PlotAndDetect()

    # Fuel alert overides any prior status messages
          
    if fuel <= FUEL_ALERT:
        UpdateStatus("FUEL ALERT")

    # But gameover overides fuel alert
    
    gameover = False

    if fatal or ticks >= MAX_TICKS or fuel <= 0:
        
        if fatal:
            UpdateStatus("FATAL HIT")
        elif ticks >= MAX_TICKS:
            UpdateStatus("TIME UP")
        else:
            UpdateStatus("FUEL EMPTY")
            
        gameover = True
        
    # Update screen
            
    clear()
     
    DrawWall()
    DrawGhost()
    DrawPlayer()
    DrawLevel()
    DrawPrompt("F2=Pause F3=Cash-in")
    DrawCash()
    DrawBounty()
    DrawStatus()
    DrawTopupCost()
    
    update()

    # Ghost always disappears after a hit
    # but only after screen has been updated.
    # This allows visual appearance of
    # collision to persist for one cycle

    if collision:
        gv = False

    if gameover:
        state = "over"

########################################################

def StatePause():

    # PAUSE state just keeps screen frozen and
    # remains in this state until user continues
    # or exits

    pass

########################################################

def StateOver():

    # OVER state shows game stats and moves
    # immediately to RECAP state

    global state

    state = "recap"

    SoundOver()
    clear()
    
    DrawPrompt("GAME OVER: F2=New F3=Exit")
    DrawStats()
    
    update()

########################################################

def StateRecap():

    # RECAP state leaves game stats on screen
    # and remains in RECAP state until user
    # exits or starts a new game

    pass

########################################################

def StateExiting():

    # EXITING state occurs when user has indicated
    # he wants to exit but exit has not yet begun.
    # Goes immediately to EXIT state where shutdown
    # proper occurs. In the future we may put an
    # "are you sure" prompt here.

    global state
    
    state = "exit"

########################################################

def StateExit():

    # EXIT state goes immediately to EXITED state
    # and shuts down.

    state = "exited"
    ShutDown()

########################################################

def StateMachine():

    global state

    HealthCheck()
   
    if state == "idle":
        StateIdle()
    elif state == "ready":
        StateReady()
    elif state == "busy":
        StateBusy()
    elif state == "pause":
        StatePause()
    elif state == "over":
        StateOver()
    elif state == "recap":
        StateRecap()
    elif state == "exiting":
        StateExiting()
    elif state == "exit":
        StateExit()

    # Schedule next state machine cycle with
    # small delay for processing other events
    # Timer is not actived in EXITED state

    if state != "exited":
        ontimer(StateMachine, 10)

########################################################
# Start of Program Execution
########################################################

StartUp()
StateMachine()
done()

########################################################
# End of Program Execution
########################################################
