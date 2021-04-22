# -*- coding: utf-8 -*-
"""
@author: esther.borkowski.12@ucl.ac.uk

export
======
This module contains the classes *idf_to_fmu* and *mat_to_csv* that can be used to export as FMU from an EnergyPlus IDF file and a .mat output file from a Dymola simulation to a .csv file respectively.
"""

import subprocess
from modelicares import SimRes
import os

class idf_to_fmu:
    
    def __init__(self, eptofmu_file, idd_file, epw_file, idf_file):
        self.eptofmu_file = eptofmu_file
        self.idd_file = idd_file
        self.epw_file = epw_file
        self.idf_file = idf_file     

    def export(self):
        export = ['python2', self.eptofmu_file, '-i', self.idd_file, '-w', self.epw_file, '-a', '2', self.idf_file]
        subprocess.call(export)

class mat_to_csv:
    
    def __init__(self, mat_file, csv_file=None):
        self.mat_file = mat_file
        self.csv_file = csv_file
            
    def export(self, output_vars=None):
        
        sim = SimRes(self.mat_file)

        if self.csv_file is not None:
            self.csv_file = os.path.splitext(self.mat_file)[0] + '.csv'
        else:
            self.csv_file = self.csv_file
        
        if output_vars is not None:
            self.output_vars = output_vars
            data = sim.to_pandas(self.output_vars)
        else:
            data = sim.to_pandas()
            
        data = data.loc[~data.index.duplicated(keep='last')]
        data.drop(data.head(1).index, inplace=True)
        data.to_csv(self.csv_file, encoding='utf-8')