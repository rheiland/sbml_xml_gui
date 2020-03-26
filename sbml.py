"""
====================================================================================================
  Parse a PhysiCell configuration file (XML) and generate a Jupyter (Python) module: 
    sbml_def.py - containing widgets for SBML parameters.
  
====================================================================================================
 
  Inputs - takes none, 1, 2, 3, or 4 arguments
  ------
    config filename (str, optional): the PhysiCell configuration file (.xml) (Default = config.xml)
    GUI module (str, optional):      the primary GUI for the Jupyter notebook 
    colorname1, colorname2 (str, optional): the colors to use for the alternating rows of widgets 
                                            (Defaults: lightgreen, tan)
  Examples (with 0,1,2,3,4 args):
  --------
    python sbml.py [PhysiCell_settings.xml]
  
  Outputs
  -------
    sbml_def.py: Python module used to create/edit cell parameters (--> "SBML" GUI tab)
 
Authors:
Randy Heiland (heiland@iu.edu)
Dr. Paul Macklin (macklinp@iu.edu)

--- History ---
"""

import sys
import os
import math
import xml.etree.ElementTree as ET

# Defaults
config_file = "config.xml"
colorname1 = 'lightgreen'
colorname2 = 'tan'

num_args = len(sys.argv)
print("num_args=",num_args)
if (num_args < 2):
    print()
    print("*** NOTE:  using config.xml  ***")
    print()
else:
    config_file = sys.argv[1]
    if not os.path.isfile(config_file):
        print(config_file, "does not exist")
        print("Usage: python " + sys.argv[0] + " <config-file.xml> [<gui-file.py>] [<colorname1> <colorname2>]")
        sys.exit(1)

if (num_args == 3):
    gui_file = sys.argv[2]
elif (num_args == 4):
    colorname1 = sys.argv[2]
    colorname2 = sys.argv[3]
elif (num_args == 5):
    gui_file = sys.argv[2]
    colorname1 = sys.argv[3]
    colorname2 = sys.argv[4]
elif (num_args > 5):
    print("Usage: python " + sys.argv[0] + " <config-file.xml> [<gui-file.py>] [<colorname1> <colorname2>]")
    sys.exit(1)

print()
print("config_file = ",config_file)
print("colorname1 = ",colorname1)
print("colorname2 = ",colorname2)
print()

if (num_args == 3):
    with open(gui_file) as f:   # e.g., "mygui.py"
    #  newText = f.read().replace('myconfig.xml', config_file) # rwh todo: don't assume this string; find line
        file_str = f.read()
        idx = file_str.find('main_xml_filename')  # verify > -1
        file_pre = file_str[:idx] 
        idx2 = file_str[idx:].find('\n')
        file_post = file_str[idx+idx2:] 

    with open(gui_file, "w") as f:
        f.write(file_pre)
        f.write("main_xml_filename = '" + config_file + "'")
        f.write(file_post)

#---------------------------------------------------------------------------------------------------
sbml_tab_header = """ 
# This file is auto-generated from a Python script that parses a PhysiCell configuration (.xml) file.
#
# Edit at your own risk.
#
import os
from ipywidgets import Label,Text,Checkbox,Button,HBox,VBox,FloatText,IntText,BoundedIntText,BoundedFloatText,Layout,Box
    
class SBMLDefTab(object):

    def __init__(self):
        
        micron_units = Label('micron')   # use "option m" (Mac, for micro symbol)

        constWidth = '180px'
        tab_height = '500px'
        stepsize = 10

        #style = {'description_width': '250px'}
        style = {'description_width': '25%'}
        layout = {'width': '400px'}

        text_layout={'width':'25%'}
        name_button_layout={'width':'25%'}
        widget_layout = {'width': '15%'}
        units_button_layout ={'width':'15%'}
        desc_button_layout={'width':'45%'}
        divider_button_layout={'width':'40%'}

        self.sbml_filename = Text(
            value='',
            placeholder='sbml_filename',
            description='SBML file:',
            disabled=True
        )

        box_layout = Layout(display='flex', flex_flow='row', align_items='stretch', width='100%')

        self.species_column = Label(value='Species', layout=text_layout)
        self.substrate_column = Label(value='Substrate', layout=text_layout)
        row0 = [self.species_column, self.substrate_column] 
        box0 = Box(children=row0, layout=box_layout)

"""

"""
        self.therapy_activation_time = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='therapy_activation_time',
            style=style, layout=layout,
            # layout=Layout(width=constWidth),
        )
        self.save_interval_after_therapy_start = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='save_interval_after_therapy_start',
            style=style, layout=layout,
        )

        label_blankline = Label('')

        self.tab = VBox([HBox([self.therapy_activation_time, Label('min')]), 
                         HBox([self.save_interval_after_therapy_start, Label('min')]), 
                         ])  
"""

fill_gui_str= """

    # Populate the GUI widgets with values from the XML
    def fill_gui(self, xml_root):
        uep = xml_root.find('.//intracellular')  # find unique entry point
        map_vars = []   # pointers to <species> nodes
        if uep:
            for imap in uep.findall('map'):   # imap.tag = 'map'  (type 'str')
                map_vars.append(imap)

        self.sbml_filename.value = uep.find('.//sbml_filename').text

"""

fill_xml_str= """

    # Read values from the GUI widgets to enable editing XML
    def fill_xml(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        sp = []   # pointers to <species> nodes
        if uep:
            for var in uep.findall('species'):
                sp.append(var)

"""
# Now parse a configuration file (.xml) and map the user parameters into GUI widgets
#tree = ET.parse('../config/PhysiCell_settings.xml')
try:
    tree = ET.parse(config_file)
except:
    print("Cannot parse",config_file, "- check it's XML syntax.")
    sys.exit(1)

root = tree.getroot()

indent = "        "
indent2 = "          "

# self.tab = VBox([HBox([self.therapy_activation_time, Label('min')]), 
vbox_str = "\n" + indent + "self.tab = VBox([\n"
vbox_str += indent2 + "self.sbml_filename,\n"
vbox_str += indent2 + "box0,\n"
#units_buttons_str = "\n" 
desc_buttons_str = "\n"
header_buttons_str = "\n"
row_str = "\n"
box_str = "\n" + indent + "box_layout = Layout(display='flex', flex_flow='row', align_items='stretch', width='100%')\n"
row_header_str = "\n"
box_header_str = "\n"
#        box1 = Box(children=row1, layout=box_layout)\n"

menv_var_count = 0
param_count = 0
color_count = 0
#param_desc_count = 0
map_count = 0

#---------- intracellular --------------------
# TODO: cast attributes to lower case before doing equality tests; perform more testing!

uep = root.find('.//intracellular')  # find unique entry point (uep) 

print_vars = True
#print_var_types = False

tag_list = []

#===========  main loop ===================
# NOTE: we assume a simple "children-only" hierarchy in <intracellular>
for child in uep:   # uep = "unique entry point" from above
    if print_vars:
        print(child.tag, child.attrib)

    if child.tag.lower() == 'map':
#             self.therapy_activation_time = BoundedFloatText(
#            min=0., max=100000000, step=stepsize,
        full_name = "self." + child.tag
        # map_count += 1
        # if child.attrib['species'] not in child.keys():
        if False:   # validate
            print("    *** Error - Invalid species attribute: " + child.attrib['species'])
            sys.exit(1)
        else:
            # self.species1 = Text(value='foo', layout=text_layout)
            # child.attrib['species']
            map_count += 1
            # species_widget = indent + "self.species" + str(map_count) + " =  Text(value="
            species_name = "self.species" + str(map_count)
            substrate_name = "self.substrate" + str(map_count)
            sbml_tab_header += indent + species_name + " =  Text(value='" + child.attrib['species'] + "', layout=text_layout)\n"
            sbml_tab_header += indent + substrate_name + " =  Text(value='" + child.attrib['substrate'] + "', layout=text_layout)\n"
            # row1 = [self.species1, self.substrate1] 
            row_name = "row" + str(map_count)
            sbml_tab_header += indent + row_name + " =  [" + species_name + "," + substrate_name +  "]\n"
            sbml_tab_header += indent + "box" + str(map_count) + " = Box(children=" + row_name + ", layout=box_layout)\n"
            # sbml_tab_header += "\n" + indent + param_name_button + " = " + "Button(description='" + child.tag + "', disabled=True, layout=name_button_layout)\n"


                # sbml_tab_header += indent2 + "value=" + child.text + ",\n"
                # Note: "step" values will advance the value to the nearest multiple of the step value itself :-/


            # Strings
            # elif child.attrib['type'] == "string":
            #     sbml_tab_header += indent2 + "value='" + child.text + "',\n"

            # row_name = "row" + str(param_count)
            box_name = "box" + str(map_count)
            # if (not divider_flag):
            #     # We're processing a "normal" row - typically a name, numeric field, units, description
            #     #  - append the info at the end of this widget
            #     sbml_tab_header += indent2 + "style=style, layout=widget_layout)\n"

            #     row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " +      units_btn_name + ", " + desc_row_name + "] \n"

            #     box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"

            vbox_str += indent2 + box_name + ",\n"

            # if (not divider_flag):
            #     # float, int, bool
            #     if (type_cast[child.attrib['type']] == "bool"):
            #         fill_gui_str += indent + full_name + ".value = ('true' == (uep.find('.//" + child.tag + "').text.lower()) )\n"
            #     else:
            #         fill_gui_str += indent + full_name + ".value = " + type_cast[child.attrib['type']] + "(uep.find('.//" + child.tag + "').text)\n"

            #     fill_xml_str += indent + "uep.find('.//" + child.tag + "').text = str("+ full_name + ".value)\n"

vbox_str += indent + "])"

# Write the beginning of the Python module for the user parameters tab in the GUI
sbml_tab_file = "sbml_def.py"
print("\n --------------------------------- ")
print("Generated a new: ", sbml_tab_file)
print()
fp= open(sbml_tab_file, 'w')
fp.write(sbml_tab_header)
# fp.write(units_buttons_str)
fp.write(desc_buttons_str)
fp.write(row_str)
fp.write(box_str)
fp.write(vbox_str)
fp.write(fill_gui_str)
fp.write(fill_xml_str)
fp.close()


#=================================================================
print()
#print("If this is your first time:")
#print("Run the GUI via:  jupyter notebook mygui.ipynb")
print("Test the minimal GUI via:  jupyter notebook test_gui.ipynb")
print("run the Jupyter menu item:  Cell -> Run All")
print()
print("(or, if you already have a previous GUI running and want to see new params:")
print("run the Jupyter menu item:  Kernel -> Restart & Run All)")
print()