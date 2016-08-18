#--------------------------------------------------
# Written by Joseph Farah
# Last updated: 7/30/16
# Evolution simulator
# User should be able to pick number of organisms, frequency of natural disasters,
# frequency of generation, population limit, maximum number of mutations per cycle, 
# -------------------------------------------------

import random
import math
import time
import string
import matplotlib.pyplot as plt
import numpy
from Tkinter import *
from tkFileDialog import askopenfilename as selectFILE
import tkMessageBox as tkmb

# Constants (or defaults, depending on whether or not the program accepts input)
#---------------------------------------------------------------------------------
# mainloop 
main = Tk()

# constant dictionary
c = {'NUM_ORG':10, 'OPT_OFF_NUM':5, 'NAT_DIS_FREQ':10, 'GEN_FREQ':1, "POP_LIM":1000,'FREQ_MUT':45, 'MAX_MUT':3, 'GEN_NUM':100}
no = IntVar()
oon = IntVar() 
ndf = IntVar()
gf = IntVar()
pl = IntVar()
fm = IntVar()
mm = IntVar()
pop = IntVar()
natcheck = IntVar()

#---------------------------------------------------------------------------------

# classes
class element_input:
    def __init__(self, parent, CONSTANT):

        top = self.top = Toplevel(parent)
        con = self.con = c[CONSTANT]
        CONSTANT = self.CONSTANT = CONSTANT
        Label(top, text="Current value is: {0}\nPlease enter new value for {1}".format(con, CONSTANT)).pack()

        self.e = Entry(top)
        self.e.pack(padx=5)

        b = Button(top, text="submit", command=self.enter_element)
        b.pack(pady=5)

    def enter_element(self):
        new_value = self.e.get()
        var_idx = gui_element_names.index(self.CONSTANT)
        c[self.CONSTANT] = int(new_value)

        self.top.destroy()

class generation_lists:
    def __init__(self, parent):

        top = self.top = Toplevel(parent)
        self.listgen = Listbox(top)
        self.listgen.pack(padx=5)
        self.listgen.insert(END, "none")
        self.listgen.delete(0,END)
        for generation in population_MASTER:
            self.listgen.insert(END,population_MASTER.index(generation))
        
        self.listgen.bind('<<ListboxSelect>>',self.CurSelet)
        b = Button(top, text="submit", command=self.select)
        b.pack(pady=5)

    def select(self):

        self.top.destroy()

    def CurSelet(self, evt):
        value=str(self.listgen.get(self.listgen.curselection()))



# functions


def defining_stuff():
    global weighted_char_list, population_MASTER, char_effect, char_list, natural_disasters, natural_disaster_chance, mutation_chance,NUM_ORG, OPT_OFF_NUM, NAT_DIS_FREQ, GEN_FREQ, POP_LIM, FREQ_MUT, MAX_MUT, GEN_NUM, c
    # defining the weighted characteristics list
    weighted_char_list = []
    # generating a weighted characteristics list that will make some chars more probable than others
    for i in xrange(1,len(characteristics)+1):
        num_char = len(characteristics)-i+1
        for x in range(num_char):
            weighted_char_list.append(i)
    # natural disasters and who survives
    nat_dist_list = [1,2,3,4,5,6]
    natural_disaster_names = {1:'landslide', 2:'blizzard', 3:'drought', 4:'lightning strike', 5:'hurricane', 6:'earthquake'}
    natural_disasters = {1:'4 6 7', 2:'2 3 7', 3:'1 3 7', 4:'1 4 7', 5:'2 3 6', 6:'1 3 4 6'}
    # list for the natural disaster frequency
    natural_disaster_chance = [0 for i in xrange(100)]
    for i in xrange(0,100):
        if i >= c['NAT_DIS_FREQ']:
            break
        else:
            natural_disaster_chance[i] = 1
    # mutation chance list
    mutation_chance = [0 for i in xrange(100)]
    for i in xrange(0,100):
        if i >= c['FREQ_MUT']:
            break
        else:
            mutation_chance[i] = 1



def generate(generation):
    '''this function generates the organisms, their characteristics, and their lifetimes'''
    global weighted_char_list, population_MASTER, char_effect, char_list, natural_disasters, natural_disaster_chance, mutation_chance
    # current gen should be an empty list at the beginning because the current generation doesn't exist yet
    current_gen = []
    # if we are on the first generation, create the first generation without any previous data
    if generation == 0:
        # pick a random character from the list--all the organisms will share this characteristic
        characteristic = random.choice(char_list)
        # iterate through the number of organinisms in the initial generations, established by NUM_ORG
        for org in xrange(c['NUM_ORG']):
            # create smaller lists for each organism
            # first item: organism number, denoted by org
            # second item: characteristic, denoted by characteristic
            # third item: name of the characteristic, selected from the characteristics list
            current_gen.append([org, characteristic, characteristics[characteristic]])
        return current_gen  
    # if we aren't on the first generation, generate a new generation
    # begin by iterating through each organism in the PREVIOUS GENERATION
    for organism in population_MASTER[generation-1]:
        # examine the current organisms characteristic
        # this will determine the success of the organism's reproductive cycle
        org_char = organism[1]
        # value essentially represents the deviation from the optimal offspring, set by OPT_OFF_NUM
        off_change = char_effect[org_char]
        # checking if the deviation is positive or negative
        if off_change == '-':
            # if negative, subtract the optimal offspring number
            number_of_offspring = c['OPT_OFF_NUM'] - random.randint(0,c['OPT_OFF_NUM'])
        elif off_change == '+':
            # if positive, add to the optimal offspring number
            number_of_offspring = c['OPT_OFF_NUM'] + random.randint(0,c['OPT_OFF_NUM'])
        # generating the offspring for each parent
        # iterates through the number of offspring, denoted by number_of_offspring
        for offspring in xrange(0,number_of_offspring):
            # randomly selects from the weighted mutation chance list
            # 1 denotes a successful mutation, 0 denotes no mutation
            will_mutate = random.choice(mutation_chance)
            if will_mutate == 1:
                # if mutation is successful, pick a random characteristic 
                # DIFFERENT from the parent's characteristic
                mutation = random.choice(weighted_char_list)
                while mutation == org_char:
                    mutation = random.choice(weighted_char_list)
                # add it to the current generation
                current_gen.append([offspring,mutation,characteristics[mutation]])
            # if the organism does not mutate, it is identical to the parent. 
            # duplicate the parent and append it to the current gen
            elif will_mutate == 0:
                current_gen.append(organism)
        # find out the size of the current generation
        population_size = len(current_gen)
        # if the population is larger than the limit, denoted by POP_LIM, make it within the limit
        # splice time!
        if population_size >= c['POP_LIM']:
            current_gen = current_gen[:c['POP_LIM']]
    return current_gen

def get_per(generation):
    
    global population_MASTER, char_list, characteristics
    # initiliaze the percentages list
    percentages = []

    # find the length of the current generation
    length = float(len(population_MASTER[generation]))
    # iterate through all possible characteristics, tally up organisms, and divide to find the percentages 
    for attribute in char_list:
        tmp_count = 0
        for organism in population_MASTER[generation]:
            if organism[1] == attribute:
                tmp_count+=1
        percentages.append([characteristics[attribute], 100*(tmp_count/length)])
    return percentages

def get_final_per():
    '''
    get the percentages of each characteristic for the current generation.
    Call this function only!!! after population_MASTER has been filled.   
    '''
    global population_MASTER, per_list
    per_list = []
    for gen in population_MASTER:
        gen_num = population_MASTER.index(gen)
        per_list.append(get_per(gen_num))

def natural_disaster(generation):
    global population_MASTER, char_list, natural_disasters, natural_disaster_names, nat_dist_list, natlist
    gen = population_MASTER[generation]
    nat_dist_type = random.choice(nat_dist_list)
    who_survives = natural_disasters[nat_dist_type].split()
    who_survives = [int(s) for s in who_survives]
    for organism in population_MASTER[generation]:
        if organism[1] not in who_survives:
            population_MASTER[generation].remove(organism)
        else:
            pass
    natlist.append([natural_disaster_names[nat_dist_type],generation])
    return population_MASTER

# button functions

def constant_change(constant):
    element_input(main, constant)


def graph():
    '''
    graph the evolution according to the specifications set by the user
    '''
    global per_list, natlist
    y = []
    approved_list = ['null']
    if no.get() == 1:
        approved_list.append(characteristics[1])
    if oon.get() == 1:
        approved_list.append(characteristics[2]) 
    if ndf.get() == 1:
        approved_list.append(characteristics[3])
    if gf.get() == 1:
        approved_list.append(characteristics[4])
    if pl.get() == 1:
        approved_list.append(characteristics[5])
    if fm.get() == 1:
        approved_list.append(characteristics[6])
    if mm.get() == 1:
        approved_list.append(characteristics[7])


    x = []
    print characteristics[1]
    fig, ax = plt.subplots()
    plt.ion()
    for char in char_list:
        y_list = []
        for gen in per_list: 
            y_list.append(gen[char-1][1])
        y.append([characteristics[char],y_list])
    for i in range(0,len(population_MASTER)):
        x.append(i)
    population_num = []
    for generation in population_MASTER:
         population_num.append(len(generation)/(10*(c['POP_LIM']/1000)))
    if pop.get() == 1:
        ax.plot(x,population_num, linestyle='dashed', label='Population (scaled)')
    for dataset in y:
        if dataset[0] in approved_list:
            ax.plot(x,dataset[1],label=dataset[0])
        plt.pause(0.1)
    for ND in natlist:
        ax.text(ND[1],90, '-{0}'.format(ND[0]),rotation=45)
        if natcheck.get() == 1:
            ax.axvline(x=ND[1], linewidth=1, color='k')


    # making the legend
    legend = ax.legend(loc='upper right', shadow=True)
    for label in legend.get_texts():
        label.set_fontsize('small')

    plt.show()
    # generation_lists(main)



def main_function():
    '''generate population master, including all effects to the population'''
    global c, population_MASTER, nat_dist_check, natural_disaster_chance, per_list
    del population_MASTER[:]
    defining_stuff()
    for i in range(0,c['GEN_NUM']):
        population_MASTER.append(generate(i))
        nat_dist_check = random.choice(natural_disaster_chance)
        if nat_dist_check == 1:
            population_MASTER = natural_disaster(i)
            #time.sleep(c['GEN_FREQ'])
    get_final_per()
    tkmb.showinfo("Process Completed","Process complete, EVOLUTION terminated")

def get_profile():
    '''load profile from file'''
    global gui_element_names
    profile_filepath = selectFILE()
    with open(profile_filepath) as f:
        profile = f.readlines()
    f.close()
    for i in range(len(gui_element_names)):
        c[gui_element_names[i]] = int(profile[i])
    tkmb.showinfo("Process Completed","Current Profile Loaded")

def export_profile():
    '''export profile to file'''
    global gui_element_names
    profilename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))+'.profile'
    with open(profilename, 'w') as o:
        for i in range(len(gui_element_names)):
            o.write("%s\n" % c[gui_element_names[i]])
    o.close()
    tkmb.showinfo("Process Completed","Profile Exported")




# main portion of program

# Lists and dictionaries
#---------------------------------------------------------------------------------
characteristics = {1:'heat-resistant', 2:'cold-resistant', 3:'energy-efficient', 4:'fast', 5:'slow', 6:'big', 7:'small', 8:'attractive'}
# character list for iteration
char_list = [1,2,3,4,5,6,7]
# defining which characteristics lead to an increase, decrease, or no change in reproductive activity
char_effect = {1:'-', 2:'+',3:'+',4:'+',5:'-',6:'+',7:'-',8:'+'}
nat_dist_list = [1,2,3,4,5,6]
natural_disaster_names = {1:'landslide', 2:'blizzard', 3:'drought', 4:'lightning strike', 5:'hurricane', 6:'earthquake'}
natural_disasters = {1:'4 6 7', 2:'2 3 7', 3:'1 3 7', 4:'1 4 7', 5:'2 3 6', 6:'1 3 4 6'}
# the master list that contains all generations
population_MASTER = []
# percentage lists
per_list = []
natlist = []
# defining of GUI elements
gui_element_names = ['NUM_ORG', 'OPT_OFF_NUM', 'NAT_DIS_FREQ', 'GEN_FREQ', 'POP_LIM', 'FREQ_MUT', 'MAX_MUT', 'GEN_NUM']
r = 0
cc = 0
for element in gui_element_names:
    Label(main, text=element).grid(row=r,column=cc)
    r += 1
r = 0
for char in char_list:
    Label(main, text=characteristics[char]+'?').grid(row=r, column=3)
    r +=1

menubar = Menu(main)
menubar.add_command(label="Quit!", command=main.quit)
menubar.add_command(label="Load Profile", command=get_profile)
menubar.add_command(label="Export Profile", command=export_profile)


Button(main,text='NUM_ORG', command=lambda:constant_change('NUM_ORG')).grid(row = 0, column=1)
Button(main,text='OPT_OFF_NUM', command=lambda:constant_change('OPT_OFF_NUM')).grid(row = 1, column=1)
Button(main,text='NAT_DIS_FREQ', command=lambda:constant_change('NAT_DIS_FREQ')).grid(row = 2, column=1)
Button(main,text='GEN_FREQ', command=lambda:constant_change('GEN_FREQ')).grid(row = 3, column=1)
Button(main,text='POP_LIM', command=lambda:constant_change('POP_LIM')).grid(row = 4, column=1)
Button(main,text='FREQ_MUT', command=lambda:constant_change('FREQ_MUT')).grid(row = 5, column=1)
Button(main,text='MAX_MUT', command=lambda:constant_change('MAX_MUT')).grid(row = 6, column=1)
Button(main,text='GEN_NUM', command=lambda:constant_change('GEN_NUM')).grid(row = 7, column=1)
Button(main,text='EXECUTE MAIN',command=main_function).grid(row=8,column=0)
Button(main,text='GRAPH',command=graph).grid(row=8,column=1)
a = Checkbutton(main, text="<---Graph", variable=no)
a.grid(row=0, column=2, sticky=W)
a.toggle()
b=Checkbutton(main, text="<---Graph", variable=oon)
b.grid(row=1, column=2, sticky=W)
b.toggle()
c1 = Checkbutton(main, text="<---Graph", variable=ndf)
c1.grid(row=2, column=2, sticky=W)
c1.toggle()
k1=Checkbutton(main, text="<---Graph", variable=gf)
k1.grid(row=3, column=2, sticky=W)
k1.toggle()
d1=Checkbutton(main, text="<---Graph", variable=pl)
d1.grid(row=4, column=2, sticky=W)
d1.toggle()
e1=Checkbutton(main, text="<---Graph", variable=fm)
e1.grid(row=5, column=2, sticky=W)
e1.toggle()
f1=Checkbutton(main, text="<---Graph", variable=mm)
f1.grid(row=6, column=2, sticky=W)
f1.toggle()
g1=Checkbutton(main, text="Graph pop", variable=pop)
g1.grid(row=7, column=2, sticky=W)
g1.toggle()
h1=Checkbutton(main, text="Show natural disaster lines?", variable=natcheck)
h1.grid(row=8, column=2, sticky=W, columnspan=2)

main.config(menu=menubar)
main.mainloop()

