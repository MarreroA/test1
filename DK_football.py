##draftkings code
#gettingturnt.py

import csv
import math
import numpy
import copy
import time

## Stattleship Information

appname = 'nicetrain'

clientID = "6f51ee37258ba410a2806a9bc93d8a56"

clientSecret = "d29c90885537446bd38679a17d6b052457e8d47abd40384a4dd17d5b8fcfdabd"

accessToken = "8c1612a30a7f98342ee39944b4cfadcf"


##----------
#----input values#######################
                                       #
salary_cap = 50000                     #              
                                       #
#limiting search space                 #
#----------

        
#player limits to pull from global salary rankings. 
#should be large enough to get accurate average/standard deviation data
QB_limit = 20
RB_limit = 30
WR_limit = 30
TE_limit = 30
DST_limit= 10
#search limits will be used to prune the player search space after analysis has been conducted and expected points modified
QB_search = 10
RB_search = 25
WR_search = 25
TE_search = 10
DST_search = 5

solution_limit = 100000000    #10,000,000
counter_limit = 10000000000   #1,000,000,000

#----------

block_list = []
                                       #
                                       #
                                       #
                                       #
########################################


                                       
def update_lineups(best_lineup,current):
    #method for updating lineups with each new lineup iteration. to be used inside search algo
    for i in range(len(best_lineup)):
        current_iteration=best_lineup[i]
        if current[0] > current_iteration[0]:
            best_lineup[(1+i):]=best_lineup [i:]
            best_lineup[i] = current
            break
    best_lineup = best_lineup[:45]
    return best_lineup

def player_stats (player_list,point_loc):
    #returns new list with (mean,standard deviation)
    print 'inside player stats'
    n = len(player_list)
    sum_1 = 0
    sum_2 = 0
    for i in range(n):
        player = player_list[i]
        sum_1 = sum_1 + player[point_loc]
    avg = sum_1/float(n)
    for i in range(n):
        player = player_list[i]
        sum_2 = sum_2 + (player[point_loc]-avg)**2
    sd = sum_2/float(n)
    sd = sd**0.5
    return [avg,sd]

def update_rankings_method1(temp_list,globe_list,rankings,teams):

    #method 1
    print 'inside method1'
    #uses a sine wave to predict values of players based on the defense rankings at position
    #values will range from 1.5 to 0.5 of average based on matchup
    
    for player_i in range (len(temp_list)):
        player = temp_list[player_i]
    
        opponent = player[4]
        
        for rank_i in range (2,34):
            #make sure it is in order
            team = rankings[rank_i]
##            teambefore = rankings[rank_i-1]
##            if float(team[16])>float(teambefore[16]):
##                print 'out of order'
##                ##DO SOMETHING
            if teams[opponent] == team[0]:
                break
        
        correction = -0.5*math.sin((rank_i-17)*(math.pi/32))
        newpoints = player[1] * (1+correction)
        
        temp_row = [player[0],newpoints,player[2]]
        globe_list.append(temp_row)

        
    return globe_list

def update_rankings_method2(temp_list,globe_list,rankings,teams,location_of_points):

    #method 2. uses standard deviation to find projected points

    temp = player_stats (temp_list,1)
    player_avg = temp[0]
    player_sd = temp[1]

    def_avg = rankings[0]
    def_avg = def_avg [location_of_points]
    def_sd = rankings[1]
    def_sd = def_sd [location_of_points]

    for player_i in range(len(temp_list)):
        player = temp_list[player_i]
        opponent = player[4]
        for rank_i in range(2,34):
            team = rankings[rank_i]
            if teams[opponent] == team[0]:
                break
        def_deviation = (team[location_of_points]-def_avg)/def_sd
        player_deviation = (player[1]-player_avg)/player_sd
        newpoints = ((player_deviation + 1.2*def_deviation)*player_sd)+player_avg
        temp_row = [player[0],newpoints,player[2]]
        globe_list.append(temp_row)
    return globe_list

def write_projections (globe_list,position,temp_position,rankings,teams,location_of_points):
    globe1 = []
    globe2 = []
    method1 = update_rankings_method1(temp_position,globe1,rankings,teams)
    method2 = update_rankings_method2(temp_position,globe2,rankings,teams,location_of_points)
    for i in range (len(temp_position)):
        player = temp_position[i]
        name = player[0]
        points_0 = player[1]
        price = player[2]
        points_1 = method1[i]
        points_2 = method2[i]
        points_1 = points_1[1]
        points_2 = points_2[1]
        temp = [position,name,points_0,points_1,points_2,price]
        globe_list.append(temp)
    return globe_list
    
    
def search_tree (globeQB,globeRB,globeWR,globeTE,globeDST,QB_limit,RB_limit,WR_limit,TE_limit,DST_limit,salary_cap,best_lineup,solution_limit,counter_limit):
    
    ##-----search tree
    print 'searching....'
    solutions = 0
    counter = 0
    t_0 = time.time()
    time_i = 15
    for qb_i in range (QB_limit):
        qb = globeQB[qb_i]
        qb_remaining=salary_cap - qb[2]
        for rb1_i in range(RB_limit):
            rb1 = globeRB[rb1_i]
            rb1_remaining=qb_remaining - rb1[2]
            for rb2_i in range (rb1_i,RB_limit):
                #tempRB = globeRB[:]
                #tempRB.remove(rb1)
                rb2 = globeRB[rb2_i]
                rb2_remaining=rb1_remaining - rb2[2]
                if rb2==rb1:
                    counter = counter+1
                    continue
                for wr1_i in range (WR_limit):
                    wr1 = globeWR[wr1_i]
                    wr1_remaining = rb2_remaining - wr1[2]
                    if wr1_remaining < 12000:
                        #print 'stopped at,', wr1[0]
                        counter = counter+1
                        continue
                    for wr2_i in range (wr1_i,WR_limit):
                        wr2 = globeWR[wr2_i]
                        if wr2 == wr1:
                            continue
                        wr2_remaining = wr1_remaining - wr2[2]
                        if wr2_remaining < 9500:
                            #print 'stopped at ',wr2[0]
                            counter = counter+1
                            continue
                        for wr3_i in range (wr2_i,WR_limit):
                            wr3 = globeWR[wr3_i]
                            if wr3 == wr2:
                                continue
                            if wr3 == wr1:
                                continue
                            wr3_remaining = wr2_remaining - wr3[2]
                            if wr3_remaining < 7000:
                                #print 'stopped at', wr3[0]
                                counter = counter+1
                                continue
                            for te_i in range(TE_limit):
                                te = globeTE[te_i]
                                te_remaining=wr3_remaining-te[2]
                                if te_remaining < 4500:
                                    #print 'stopped at',te[0]
                                    counter = counter+1
                                    continue
                                localflex = globeRB[rb2_i:] + globeWR[wr3_i:] + globeTE[te_i:]
                                
                                for flex_i in range (len(localflex)):
                                    flex = localflex[flex_i]
                                    if flex == rb2:
                                        continue
                                    if flex == wr3:
                                        continue
                                    if flex == te:
                                        continue
                                    if flex == wr1:
                                        continue
                                    if flex == rb1:
                                        continue
                                    if flex == wr2:
                                        continue
                                    
                                    flex_remaining = te_remaining - flex[2]
                                    if flex_remaining < 2000:
                                        counter = counter+1
                                        #print 'stopped at flex ',flex[0]
                                        continue
                                    
                                    for dst_i in range (DST_limit):
                                        dst = globeDST[dst_i]
                                        dst_remaining = flex_remaining - dst[2]
                                        if dst_remaining < 0:
                                            counter = counter+1
                                            #print 'stopped at ',dst[0]
                                            continue
                                        ##solution found

                                        points = qb[1]+rb1[1]+rb2[1]+wr1[1]+wr2[1]+wr3[1]+te[1]+flex[1]+dst[1]
                                        lineup = [points,qb[0],rb1[0],rb2[0],wr1[0],wr2[0],wr3[0],te[0],flex[0],dst[0],dst_remaining]
                                        best_lineup = update_lineups(best_lineup,lineup)
                                        solutions = solutions + 1
                                        if (time.time()-t_0) > time_i:
                                            print 'Time Elapsed [seconds] = ',time_i
                                            time_i = time_i + 15

                                        if solutions > solution_limit or counter > counter_limit:
                                            break
                                    if solutions > solution_limit or counter > counter_limit:
                                        break
                                if solutions>solution_limit or counter>counter_limit:
                                    break
                            if solutions>solution_limit or counter>counter_limit:
                                break
                        if solutions>solution_limit or counter > counter_limit:
                            break
                    if solutions>solution_limit or counter> counter_limit:
                        break
                if solutions>solution_limit or counter> counter_limit:
                    break
            if solutions > solution_limit or counter > counter_limit:
                break
        if solutions>solution_limit or counter > counter_limit:
            break

    print 'search complete---------------------------------------'
    return best_lineup
                  
thing = open('DKSalaries_week13.csv')
DKglobal = csv.reader(thing)

thing = open('DEF_QB.csv')
qb_def_csv = csv.reader(thing)

thing = open('DEF_WR.csv')
wr_def_csv = csv.reader(thing)

thing = open('DEF_RB.csv')
rb_def_csv = csv.reader(thing)

thing = open('DEF_TE.csv')
te_def_csv = csv.reader(thing)

globeQB = []
globeWR = []
globeRB = []
globeTE = []
globeDST= []
tempQB = []
tempRB = []
tempWR = []
tempTE = []
tempDST= []

lineup = [0,0]
best_lineup = [lineup,lineup,lineup]
                   
team_def = {'ATL':'Atlanta Falcons',
            'NO':'New Orleans Saints',
            'CLE':'Cleveland Browns',
            'BAL':'Baltimore Ravens',
            'NYG':'New York Giants',
            'DET':'Detroit Lions',
            'PIT':'Pittsburgh Steelers',
            'JAX':'Jacksonville Jaguars',
            'OAK':'Oakland Raiders',
            'TEN':'Tennessee Titans',
            'SF':'San Francisco 49ers',
            'TB':'Tampa Bay Buccaneers',
            'MIA':'Miami Dolphins',
            'NE':'New England Patriots',
            'SD':'San Diego Chargers',
            'GB':'Green Bay Packers',
            'HOU':'Houston Texans',
            'CHI':'Chicago Bears',
            'BUF':'Buffalo Bills',
            'WAS':'Washington Redskins',
            'PHI':'Philadelphia Eagles',
            'IND':'Indianapolis Colts',
            'KC':'Kansas City Chiefs',
            'NYJ':'New York Jets',
            'ARI':'Arizona Cardinals',
            'DAL':'Dallas Cowboys',
            'MIN':'Minnesota Vikings',
            'SEA':'Seattle Seahawks',
            'CAR':'Carolina Panthers',
            'CIN':'Cincinnati Bengals',
            'STL':'St. Louis Rams',
            'DEN':'Denver Broncos'}



for row in DKglobal:
    if row[0] == 'Position':
        continue
    price = int(row[2])
    name = row[1]
    position = row[0]
    points = float(row[4])
    team = row[5]
    game = row[3]
    game = game.split()
    game = game[0]
    opponent = game.split('@')
    if opponent[0] == team:
        away = True
        opponent = opponent [1]
    else:
        away = False
        opponent = opponent [0]

    team = team.upper()
    opponent = opponent.upper()
    
    temp_row = [name,points,price,team,opponent,away]

    if name in block_list:
        continue
    if position == 'QB' and len(tempQB)<QB_limit:
        tempQB.append(temp_row)
    elif position == 'RB' and len(tempRB) < RB_limit:
        tempRB.append(temp_row)
    elif position == 'WR' and len(tempWR) < WR_limit:
        tempWR.append(temp_row)
    elif position == 'TE' and len(tempTE) < TE_limit:
        tempTE.append(temp_row)
    elif position == 'DST' and len(tempDST) < DST_limit:
        tempDST.append(temp_row)

DEF_QB = []
DEF_WR = []
DEF_RB = []
DEF_TE = []
DEF_DST=[]


for row in qb_def_csv:
    temp = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],float(row[16]),row[17]]
    DEF_QB.append(temp)

for row in wr_def_csv:
    temp = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],float(row[10]),row[11]]
    DEF_WR.append(temp)
for row in rb_def_csv:
    temp = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],float(row[13]),row[14]]
    DEF_RB.append(temp)
for row in te_def_csv:
    temp = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],float(row[10]),row[11]]
    DEF_TE.append(temp)
    
globe_list = []
globe_list_initial = ['Position','Name','Average ','Method 1','Method 2','Price']
globe_list.append(globe_list_initial)
globe_list = write_projections (globe_list,'QB',tempQB,DEF_QB,team_def,16)
globe_list = write_projections (globe_list,'RB',tempRB,DEF_RB,team_def,13)
globe_list = write_projections (globe_list,'WR',tempWR,DEF_WR,team_def,10)
globe_list = write_projections (globe_list,'TE',tempTE,DEF_TE,team_def,10)

print 'about to write'

with open ("week13_rankings","wb") as thing2:
    writer=csv.writer(thing2)
    writer.writerows(globe_list)

    
##
##globeQB = update_rankings_method2(tempQB,globeQB,DEF_QB,team_def,16)
##globeWR = update_rankings_method2(tempWR,globeWR,DEF_WR,team_def,10)
##globeRB = update_rankings_method2(tempRB,globeRB,DEF_RB,team_def,13)
##globeTE = update_rankings_method2(tempTE,globeTE,DEF_TE,team_def,10)
##
##
###trimming global player lists to a smaller search space. 
##globeQB = globeQB[:QB_search]
##globeWR = globeWR[:WR_search]
##globeRB = globeRB[:RB_search]
##globeTE = globeTE[:TE_search]
##globeDST= tempDST[:DST_search]
##
##best_lineup = search_tree (globeQB,globeRB,globeWR,globeTE,globeDST,QB_search,RB_search,WR_search,TE_search,DST_search,salary_cap,best_lineup,solution_limit,counter_limit
##                           )

##
##best_lineup[1:]=best_lineup [:]
##best_lineup[0] = ['Points','QB','RB1','RB2','WR1','WR2','WR3','TE','FLEX','DST','Salary Remaining']
##with open ("week11_football_2.csv","wb") as thing2:
##    writer=csv.writer(thing2)
##    writer.writerows(best_lineup)
##    
