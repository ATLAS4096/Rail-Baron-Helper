## Copyright 2018 Corey Ethington
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.



import time
import random
from random import randint
from termcolor import colored, cprint

#Colors:
#sudo pip install termcolor

debug = False
simButton = False

B1 = 11
B2 = 22

L1 = 12
L2 = 13
L3 = 15

A1 = 18
A2 = 16

#DESTINATION CHART

Empty_E = {
    2 : '',
    3 : '',
    4 : '',
    5 : '',
    6 : '',
    7 : '',
    8 : '',
    9 : '',
    10 : '',
    11 : '',
    12 : ''
    }
Empty_O = {
    2 : '',
    3 : '',
    4 : '',
    5 : '',
    6 : '',
    7 : '',
    8 : '',
    9 : '',
    10 : '',
    11 : '',
    12 : ''
    }
Empty = {
    True : Empty_E,
    False : Empty_O
    }

Regions = {
    1 : 'Northeast',
    2 : 'Southeast',
    3 : 'North Central',
    4 : 'South Central',
    5 : 'Plains',
    6 : 'Northwest',
    7 : 'Southwest'
    }

Northeast_E = {
        2 : 'New York',
        3 : 'New York',
        4 : 'New York',
        5 : 'Albany',
        6 : 'Boston',
        7 : 'Buffalo',
        8 : 'Boston',
        9 : 'Portland',
        10 : 'New York',
        11 : 'New York',
        12 : 'New York'
    }
Northeast_O = {
        2 : 'New York',
        3 : 'Washington',
        4 : 'Pittsburgh',
        5 : 'Pittsburgh',
        6 : 'Philadelphia',
        7 : 'Boston',
        8 : 'Philadelphia',
        9 : 'Baltimore',
        10 : 'Baltimore',
        11 : 'Baltimore',
        12 : 'New York'
        }
Northeast = {
    True : Northeast_E,
    False : Northeast_O
    }

Southeast_E = {
    2 : 'Charlotte',
    3 : 'Charlotte',
    4 : 'Chattanooga',
    5 : 'Atlanta',
    6 : 'Atlanta',
    7 : 'Atlanta',
    8 : 'Richmond',
    9 : 'Knoxville',
    10 : 'Mobile',
    11 : 'Knoxville',
    12 : 'Mobile'
    }
Southeast_O = {
    2 : 'Norfolk',
    3 : 'Norfolk',
    4 : 'Norfolk',
    5 : 'Charleston',
    6 : 'Miami',
    7 : 'Jacksonville',
    8 : 'Miami',
    9 : 'Tampa',
    10 : 'Tampa',
    11 : 'Mobile',
    12 : 'Norfolk'
    }
Southeast = {
    True : Southeast_E,
    False : Southeast_O
    }

North_Central_E = {
    2 : 'Cleveland',
    3 : 'Cleveland',
    4 : 'Cleveland',
    5 : 'Cleveland',
    6 : 'Detroit',
    7 : 'Detroit',
    8 : 'Indianapolis',
    9 : 'Milwaukee',
    10 : 'Milwaukee',
    11 : 'Chicago',
    12 : 'Milwaukee'
    }
North_Central_O = {
    2 : 'Cincinnati',
    3 : 'Chicago',
    4 : 'Cincinnati',
    5 : 'Cincinnati',
    6 : 'Columbus',
    7 : 'Chicago',
    8 : 'Chicago',
    9 : 'St Louis',
    10 : 'St Louis',
    11 : 'St Louis',
    12 : 'St Louis'
    }
North_Central = {
    True : North_Central_E,
    False : North_Central_O
    }

South_Central_E = {
    2 : 'Memphis',
    3 : 'Memphis',
    4 : 'Memphis',
    5 : 'Little Rock',
    6 : 'New Orleans',
    7 : 'Birmingham',
    8 : 'Louisville',
    9 : 'Nashville',
    10 : 'Nashville',
    11 : 'Louisville',
    12 : 'Memphis'
    }
South_Central_O = {
    2 : 'Shreveport',
    3 : 'Shreveport',
    4 : 'Dallas',
    5 : 'New Orleans',
    6 : 'Dallas',
    7 : 'San Antonio',
    8 : 'Houston',
    9 : 'Houston',
    10 : 'Fort Worth',
    11 : 'Fort Worth',
    12 : 'Fort Worth'
    }
South_Central = {
    True : South_Central_E,
    False : South_Central_O
    }

Plains_E = {
    2 : 'Kansas City',
    3 : 'Kansas City',
    4 : 'Denver',
    5 : 'Denver',
    6 : 'Denver',
    7 : 'Kansas City',
    8 : 'Kansas City',
    9 : 'Kansas City',
    10 : 'Pueblo',
    11 : 'Pueblo',
    12 : 'Oklahoma City'
    }
Plains_O = {
    2 : 'Oklahoma City',
    3 : 'St. Paul',
    4 : 'Minneapolis',
    5 : 'St. Paul',
    6 : 'Minneapolis',
    7 : 'Oklahoma City',
    8 : 'Des Moines',
    9 : 'Omaha',
    10 : 'Omaha',
    11 : 'Fargo',
    12 : 'Fargo'
    }
Plains = {
    True : Plains_E,
    False : Plains_O
    }

Northwest_E = {
    2 : 'Spokane',
    3 : 'Spokane',
    4 : 'Seattle',
    5 : 'Seattle',
    6 : 'Seattle',
    7 : 'Seattle',
    8 : 'Rapid City',
    9 : 'Caspar',
    10 : 'Billings',
    11 : 'Billings',
    12 : 'Spokane'
    }
Northwest_O = {
    2 : 'Spokane',
    3 : 'Salt Lake City',
    4 : 'Salt Lake City',
    5 : 'Salt Lake City',
    6 : 'Portland',
    7 : 'Portland',
    8 : 'Portland',
    9 : 'Pocatello',
    10 : 'Butte',
    11 : 'Butte',
    12 : 'Portland'
    }
Northwest = {
    True : Northwest_E,
    False : Northwest_O
    }

Southwest_E = {
    2 : 'San Diego',
    3 : 'San Diego',
    4 : 'Reno',
    5 : 'San Diego',
    6 : 'Sacramento',
    7 : 'Las Vegas',
    8 : 'Phoenix',
    9 : 'El Paso',
    10 : 'Tucumcari',
    11 : 'Phoenix',
    12 : 'Phoenix'
    }
Southwest_O = {
    2 : 'Los Angeles',
    3 : 'Oakland',
    4 : 'Oakland',
    5 : 'Oakland',
    6 : 'Los Angeles',
    7 : 'Los Angeles',
    8 : 'Los Angeles',
    9 : 'San Francisco',
    10 : 'San Francisco',
    11 : 'San Francisco',
    12 : 'San Francisco'
    }
Southwest = {
    True : Southwest_E,
    False : Southwest_O
    }

def search():
    ans = roll()
    EO = red()
    if EO == True:
        if ans == 2:
            region = "Plains"
        elif ans >= 3 and ans <=5:
            region = "Southeast"
        elif ans >= 6 and ans <= 7:
            region = "North Central"
        else:
            region = "Northeast"
    else:
        if ans == 2:
            region = "Southwest"
        elif ans >= 2 and ans <= 5:
            region = "South Central"
        elif ans >= 6 and ans <= 7:
            region = "Southwest"
        elif ans == 8:
            region = "Plains"
        elif ans >=9 and ans <= 10:
            region = "Northwest"
        elif ans == 11:
            region = "Plains"
        else:
            region = "Northwest"
    if debug == True:
        print 'Dice roll: ' + _Y(str(ans)) + ', Even: ' + _Y(str(EO)) + '.'
    #time.sleep(0.3)
    return region

def roll():
    dA = randint(1,6)
    dB = randint(1,6)
    Dest = dA + dB
    return Dest

def red():
    if randint(0,1) == 1:
        return True
    else:
        return False

def pickCity(region):
    ans = roll()
    EO = red()
    if region == 'Northeast':
        return Northeast[EO][ans]
    if region == 'Southeast':
        return Southeast[EO][ans]
    if region == 'North Central':
        return North_Central[EO][ans]
    if region == 'South Central':
        return South_Central[EO][ans]
    if region == 'Plains':
        return Plains[EO][ans]
    if region == 'Northwest':
        return Northwest[EO][ans]
    if region == 'Southwest':
        return Southwest[EO][ans]

def chooseRegion():
    print _M('<----------Manually Selecting Region---------->')
    region = raw_input(_Y("Region: "))
    fCity = _R('--ERROR--')
    if region == 'Northeast':
        fCity = pickCity('Northeast')
    elif region == 'Southeast':
        fCity = pickCity('Southeast')
    elif region == 'North Central':
        fCity = pickCity('North Central')
    elif region == 'South Central':
        fCity = pickCity('South Central')
    elif region == 'Plains':
        fCity = pickCity('Plains')
    elif region == 'Northwest':
        fCity = pickCity('Northwest')
    elif region == 'Southwest':
        fCity = pickCity('Southwest')

    if fCity != _R('--ERROR--'):
        print 'Your destination is ' + _G(fCity) + ', ' + _B(region)
    else:
        print _R("Invalid region.  Consult game board or manual for list of regions.")
    return fCity

def _Y(s):
    return colored(s, 'yellow', attrs=['bold'])

def _R(s):
    return colored(s, 'red', attrs=['bold'])

def _G(s):
    return colored(s, 'green', attrs=['bold'])

def _B(s):
    return colored(s, 'blue', attrs=['bold'])

def _C(s):
    return colored(s, 'cyan', attrs=['bold'])

def _I(s):
    return colored(s, 'cyan', attrs=['reverse'])

def _M(s):
    return colored(s, 'yellow', attrs=['reverse'])

# get a destination city
def getCity():
    print _I('<----------Searching for Destination---------->')
    nR = search()
    fCity = _R('--ERROR--')
    if nR == 'Northeast':
        fCity = pickCity('Northeast')
    elif nR == 'Southeast':
        fCity = pickCity('Southeast')
    elif nR == 'North Central':
        fCity = pickCity('North Central')
    elif nR == 'South Central':
        fCity = pickCity('South Central')
    elif nR == 'Plains':
        fCity = pickCity('Plains')
    elif nR == 'Northwest':
        fCity = pickCity('Northwest')
    elif nR == 'Southwest':
        fCity = pickCity('Southwest')
    print 'Your destination is ' + _G(fCity) + ', ' + _B(nR)
    return fCity

# obsolete???
def cCity(nR):
    fCity = _R('--ERROR--')
    if nR == 'Northeast':
        fCity = pickCity('Northeast')
    elif nR == 'Southeast':
        fCity = pickCity('Southeast')
    elif nR == 'North Central':
        fCity = pickCity('North Central')
    elif nR == 'South Central':
        fCity = pickCity('South Central')
    elif nR == 'Plains':
        fCity = pickCity('Plains')
    elif nR == 'Northwest':
        fCity = pickCity('Northwest')
    elif nR == 'Southwest':
        fCity = pickCity('Southwest')
    print 'Your destination is ' + _G(fCity) + ', ' + _B(nR)


#def destroy():
#    return

# old intitial run function.  Not needed if not independant.

#if __name__ == '__main__':
#    try:
#        chooseRegion()
#    except KeyboardInterrupt:
#        destroy()
