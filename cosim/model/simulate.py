# -*- coding: utf-8 -*-
"""
@author: esther.borkowski.12@ucl.ac.uk

simulate
========
This module contains the class *model* that can be used to run a model from a mono-simulation in EnergyPlus or a co-simulation in EnergyPlus and Dymola through the FMI Standard.
"""

import sys
from eppy.modeleditor import IDF
from datetime import datetime
from buildingspy.simulate.Simulator import Simulator

class simulate:  
        
    def __init__(self, output_dir, s_start=0, s_stop=31536000, s_step=600):
        
        self.output_dir = output_dir
        self.s_start = s_start
        self.s_stop = s_stop
        self.s_step = s_step

    def monosimulate(self,
                     eppy_path, 
                     idd_file, 
                     epw_file, 
                     idf_file, 
                     sim_params=None,
                     leap_year=False):
        
        self.eppy_path = eppy_path
        self.idd_file = idd_file
        self.epw_file = epw_file
        self.idf_file = idf_file
        self.sim_params = {} if sim_params is None else sim_params #no conversion in E+ syntax
        
        sys.path.append(self.eppy_path)
        IDF.setiddname(self.idd_file)
        
        idf = IDF(self.idf_file, self.epw_file)
        
        self.leap_year = leap_year
        
        if leap_year is None:
            pass
        elif self.leap_year == False:
            start = datetime.fromtimestamp(self.s_start)
            stop = datetime.fromtimestamp(self.s_stop)
        elif self.leap_year == True:
            ly = int(datetime(2020,1,1).strftime('%s'))
            start = datetime.fromtimestamp(self.s_start + ly)
            stop = datetime.fromtimestamp(self.s_stop + ly)
        
        start_month = start.strftime('%-m/%-d').split('/')[0]
        start_day = start.strftime('%-m/%-d').split('/')[1]
        stop_month = stop.strftime('%-m/%-d').split('/')[0]
        stop_day = stop.strftime('%-m/%-d').split('/')[1]
                
        runperiod = idf.idfobjects['RunPeriod'][0]
        runperiod.Begin_Month = start_month
        runperiod.Begin_Day_of_Month = start_day
        runperiod.End_Month = stop_month
        runperiod.End_Day_of_Month = stop_day
                
        timestep = idf.idfobjects['Timestep'][0]
        timestep.Number_of_Timesteps_per_Hour = 3600/self.s_step
    
        idf.save()
                
        idf.run(output_directory=self.output_dir, readvars=True, verbose=u'q')

    def cosimulate(self, 
                   model_name,
                   show_gui=False,
                   exit_simulator=True,
                   sim_params=None):
                
        self.model_name = model_name
        self.show_gui = False if show_gui is None else show_gui
        self.exit_simulator = True if exit_simulator is None else exit_simulator
        self.sim_params = {} if sim_params is None else sim_params
        
        s = Simulator(self.model_name, 'dymola')
    
        s.setStartTime(self.s_start)
        s.setStopTime(self.s_stop)
        number_of_intervals = (self.s_stop - self.s_start) / self.s_step
        s.setNumberOfIntervals(int(number_of_intervals))       
                
        s.addParameters(self.sim_params)
    
        s.setTimeOut(-1)
        s.showGUI(self.show_gui)
        s.exitSimulator(self.exit_simulator)
        s.setOutputDirectory(self.output_dir)
        s.setSolver('dassl')
        
        s.simulate()