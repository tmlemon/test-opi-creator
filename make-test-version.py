
'''
Author: Tyler Lemon
Date: 2020-05-06
GitHub repo: https://github.com/tmlemon/test-opi-creator

Python program embedded into Control Systems Studio (CS-Studio, or CSS)
GUI to replace all PVs in the screen set by the program's input with
local PVs for testing.

End result of program are two screens: a test screen and a control screen.
The test screen is a copy of the input screen with all PVs changed to local
PVs. The control screen is a copy of the test screen with all indicators
changed to controls (and visa versa) and Boolean controls added for all PVs
used in screen to trigger rules.

This program is not executable from standard Python environment since it
relies on Jython functions in CS-Studio.

'''
#Jython functions from CS-Studio (CSS)
from org.csstudio.opibuilder.scriptUtil import PVUtil,ConsoleUtil,FileUtil,GUIUtil,ScriptUtil,DataUtil

import os # used to look at and manipulate files in workspace
from time import sleep # used to add delays to program

# background color to change program output's Control Screen to 
testBKG = ['255','255','0']

# Template of Boolean control widget to add to control screen for rule testing
trigButton = \
['  <widget typeId="org.csstudio.opibuilder.widgets.BoolButton" version="1.0.0">',\
'    <toggle_button>true</toggle_button>',\
'    <border_style>0</border_style>',\
'    <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>',\
'    <alarm_pulsing>false</alarm_pulsing>',\
'    <tooltip>$(pv_name)',\
'$(pv_value)</tooltip>',\
'    <push_action_index>0</push_action_index>',\
'    <rules />',\
'    <effect_3d>true</effect_3d>',\
'    <bit>-1</bit>',\
'    <enabled>true</enabled>',\
'    <wuid>-1a33cb2f:171dfb9c376:-79e8</wuid>',\
'    <on_color>',\
'      <color red="0" green="255" blue="0" />',\
'    </on_color>',\
'    <show_confirm_dialog>0</show_confirm_dialog>',\
'    <password></password>',\
'    <pv_value />',\
'    <released_action_index>0</released_action_index>',\
'    <square_button>true</square_button>',\
'    <show_led>false</show_led>',\
'    <scripts />',\
'    <border_alarm_sensitive>true</border_alarm_sensitive>',\
'    <height>35</height>',\
'    <on_label>$(pv_name)</on_label>',\
'    <border_width>1</border_width>',\
'    <scale_options>',\
'      <width_scalable>true</width_scalable>',\
'      <height_scalable>true</height_scalable>',\
'      <keep_wh_ratio>true</keep_wh_ratio>',\
'    </scale_options>',\
'    <visible>true</visible>',\
'    <pv_name>PV-NAME</pv_name>'\
'    <border_color>',\
'      <color red="0" green="128" blue="255" />',\
'    </border_color>',\
'    <widget_type>Boolean Button</widget_type>',\
'    <off_color>',\
'      <color red="0" green="100" blue="0" />',\
'    </off_color>',\
'    <confirm_message>Are your sure you want to do this?</confirm_message>',\
'    <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>',\
'    <background_color>',\
'      <color red="240" green="240" blue="240" />',\
'    </background_color>',\
'    <width>275</width>',\
'    <x>X_POS</x>',\
'    <name>Boolean Button</name>',\
'    <data_type>0</data_type>',\
'    <y>Y_POS</y>',\
'    <foreground_color>',\
'      <color red="0" green="0" blue="0" />',\
'    </foreground_color>',\
'    <actions hook="false" hook_all="false" />',\
'    <show_boolean_label>true</show_boolean_label>',\
'    <font>',\
'      <opifont.name fontName="Segoe UI" height="9" style="0">Default</opifont.name>',\
'    </font>',\
'    <off_label>$(pv_name)</off_label>',\
'  </widget>']

# function used during debugging to print info to CSS console
def cssprint(l):
    ConsoleUtil.writeInfo(str(l))

# read in file to create test screens for
fin = str(PVUtil.getString(pvs[1]))[1:]

# read in go button to initiate screen creation
go = PVUtil.getDouble(pvs[0]) == 1

# flag used to include PV in rules list if macros are used
macroFlag = False


if go and fin != '':
    fin = str(FileUtil.workspacePathToSysPath(fin))
    testFin = fin.split('.')[0]+'_TEST.opi'
    testCtrlFin = fin.split('.')[0]+'_TEST-CONTROL.opi'

    pvs[2].setValue('Making test screens.')


    # Ask if user wants to remake test screens if they aleady exist
    if os.path.isfile(testFin) or os.path.isfile(testCtrlFin):
        remake = GUIUtil.openConfirmDialog(\
            'Test screens already exist. Remake screens?')
    else:
        remake = True

    # deletes old files if they are to be remade
    if remake:
        try:
            os.remove(testFin)
            os.remove(testCtrlFin)
        except:
            # if either file remove doesn't work, continue since
            # that means file isn't there
            pass

        # reads in screen to make test versions of
        with open(fin,'r') as f:
            opi = f.readlines()

        # pulls out all widgets' PVs and PVs used to trigger rules
        testpvs = []
        rulepvs = []
        for m,line in enumerate(opi):
            if '<pv trig="true">' in line:
                out = line[line.find('>')+1:]
                out = out[:out.find('<')]
                if 'sim' not in out and '$(pv_name)' not in out:
                    testpvs.append(out)
                    rulepvs.append(out)
                if out == '$(pv_name)':
                    macroFlag = True
            if '<pv_name>' in line and line.strip() != '<pv_name></pv_name>':
                foundPV = line.strip().replace('<pv_name>','').replace('</pv_name>','')
                testpvs.append(foundPV)
                if macroFlag:
                    rulepvs.append(foundPV)
                    macroFlag = False
                    
        testpvs = list(set(testpvs))
        testpvs.sort()

        # debugging fun
        #for banana in testpvs:
        #    cssprint(banana)
        
        rulepvs = list(set(rulepvs))
        rulepvs.sort()

        
        # create test screen, replacing all PVs with local PVs
        opiTest = opi
        opi = ''.join(opi)

        for pv in testpvs:
            opi = opi.replace(pv,'loc://'+pv+'(0)')

        with open(testFin,'w') as f:
            f.write(opi)


        # creates control screen, replaceing all controls with
        # indicators and visa versa.
        xStart = int(opi[opi.find('<width>')+7:opi.find('</width>')])+50
        yLimit = int(opi[opi.find('<height>')+8:opi.find('</height>')])
        ruleCtrlHeight = 50
        
        hold = []
        for line in opiTest:
            if 'TextUpdate' in line:
                line = line.replace('TextUpdate','TextInput')
            elif 'TextInput' in line:
                line = line.replace('TextInput','TextUpdate')
            hold.append(line)

        opiTest = hold

        hold = []
        bkgFound = False
        for line in opiTest:
            if '<color red="' in line.strip() and not bkgFound:
                line = line.split('"')
                modline = []
                for p in range(0,len(line),2):
                    modline.append(str(line[p]))
                line = modline[0]+'"'+testBKG[0]+'"'+modline[1]+'"'+\
                       testBKG[1]+'"'+modline[2]+'"'+testBKG[2]+'"'+modline[3]
                bkgFound = True
            hold.append(line)

        lastLine = hold[-1]
        hold = hold[:-1]


        # places boolean controls on control screen for testing rules
        xPos = xStart
        yPos = 25
        for v in rulepvs:
            for line in trigButton:
                line2 = line.replace('PV-NAME',v+'(0)')
                line2 = line2.replace('X_POS',str(xPos))
                line2 = line2.replace('Y_POS',str(yPos))
                line2 += '\n'
                hold.append(line2)
            yPos += 45
            if yPos >= yLimit:
                yPos = 25
                xPos += 300
        hold.append(lastLine)
        
        opiTest = ''.join(hold)
        
        for pv in testpvs:
            opiTest = opiTest.replace(pv,'loc://'+pv)

        with open(testCtrlFin,'w') as f:\
             f.write(opiTest)

    # wait five seconds before printing success message.
    # Gives workspace time to update and find new screens to open
    sleep(5)
    pvs[2].setValue('TEST SCREENS CREATED')    
    
    # opens test screen and control screen
    ScriptUtil.openOPI(widget,testFin,2,None)
    ScriptUtil.openOPI(widget,testCtrlFin,2,None)
    
    pvs[2].setValue('')
    pvs[0].setValue(0)
   

