import warnings
from collections import defaultdict

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from config import Config, parse_config
from algorithms import RandomSelect, LoopSelect

class Trial:
    def __init__(self, nPrisoners, algorithms, **kwargs):
        # Initialize trial-specific config variables. 
        self._algorithms = algorithms

        # Handle all kwargs.
        self._kwargs = kwargs
        
        # Initialize array of prisoners and envelopes. These serve as indices for each respective object.
        self._prisoners = np.arange(0, nPrisoners)
        # nEnvelopes must be in kwargs because of the verifier in config.
        self._envelopes = np.arange(0, kwargs.pop('nEnvelopes'))

        # Randomize envelope indices. Prisoners don't need to be randomized.
        np.random.shuffle(self._envelopes)

    @property
    def result(self):
        return self._result
    
    @property
    def data(self):
        return self._result['data']
    
    @property
    def extra(self):
        return self._result['extra']        
        
    def _run_algo(self, algorithm, prisoners, envelopes, **kwargs):
        ''' Run the prisoner problem simulation on one trial with one algorithm. Helper function for run_all().
        
        
        Parameters
        -----------
        Input: Name of function representing algorithm, as a string. See algorithms.py for more information on algorithm function structure.
        
        Output: result, a dictionary of data indexed in the form self.result[algorithm][data] or self.result[algorithm][extra].'''
        
        result = {'data': [], 'extra': defaultdict(list)}
        
        for prisoner in prisoners:
            algo = algorithm(prisoner, envelopes, **kwargs)
            out = algo.select()
            result['data'].append(out[0])
            if out[1] != None:
                for key in out[1]:
                    result['extra'][key] += [out[1][key]]
        return result
    
    def _run_algos(self, algorithms, prisoners, envelopes, **kwargs):
        ''' Run the prisoner problem simulation on one trial with specified list of algorithms. Helper function for run_all().
        
        
        Parameters
        -----------
        Input: list of algorithms
        
        Output: result, a pandas dataframe indexed in the form self.result[algorithm][data] or self.result[algorithm][data]. '''
        
        
        result = {}
        for algorithm in algorithms:
            result[algorithm.__name__] = self._run_algo(algorithm, prisoners, envelopes, **kwargs)
        return result
        
    def run_all(self):
        ''' Run the prisoner problem simulation on one trial with all algorithms specified in config. 
        This is the default user-facing method to run the simulation.
        
        
        Parameters
        -----------
        Input: None, takes inputs from config.
        
        Output: self.result, a dictionary of data indexed in the form self.result[algorithm][data] or self.result[algorithm][data]. '''

        self._result = self._run_algos(self._algorithms, self._prisoners, self._envelopes, **self._kwargs)
        return self._result

class Simulation():
    def __init__(self, config=None):
        # Go to default prison problem config if one isn't specified, but warn the user.
        if config==None:
            warnings.warn('No config specified! Assuming default prisoner problem statement with 100 prisoners and 100 trials with RandomSelect and LoopSelect algorithms.\nconfig={\'nPrisoners\': 100,\n \'nTrials\': 100,\n \'algorithms\': (RandomSelect, LoopSelect),\n \'schema\': \'default\',\n \'lower\': True,\n \'chunks\': 10,\n \'nEnvelopes\': 100}', stacklevel=2)
            config = {'nPrisoners': 100,
              'nTrials': 100,
              'algorithms': (RandomSelect, LoopSelect),
              'schema': 'default',
              'lower': True,
              'chunks': 10,
              'nEnvelopes': 100,
              }
            
        # Verify config if it is not pre-verified.
        if not isinstance(config, Config):
            config = parse_config(**config)
            
        # Config is now verified, so set it for the simulaiton.
        self._config = config
        
        # Initialize raw trial results dataframe.
        self._results = {}
        for algorithm in config['algorithms']:
            self._results[algorithm.__name__] = {'data': pd.DataFrame(dtype=np.bool), 'extra': defaultdict(dict)}
            
    @property
    def results(self):
        return self._results

    @property
    def data(self):
        data = {}
        for algorithm in self._config['algorithms']:
            data[algorithm.__name__] = self.results[algorithm.__name__]['data']
        return data

    @property
    def extra(self):
        extra = {}
        for algorithm in self._config['algorithms']:
            extra[algorithm.__name__] = self.results[algorithm.__name__]['extra']
        return extra
    
    def stats(self):
        self._stats = defaultdict(dict)
        for algorithm in self._config['algorithms']:
            if self._config['nPrisoners'] in self.data[algorithm.__name__].sum().value_counts():
                self._stats['success'][algorithm.__name__] = self.data[algorithm.__name__].sum().value_counts()[self._config['nPrisoners']]
            else:
                self._stats['success'][algorithm.__name__] = 0
            self._stats['peak'][algorithm.__name__] = self.data[algorithm.__name__].sum().value_counts().idxmax()
        return self._stats
            
    def graph(self):
        print(len(self._config['algorithms']))
        fig, axs = plt.subplots(len(self._config['algorithms']))
        for i in range(len(self._config['algorithms'])):
            counts = self.data[self._config['algorithms'][i].__name__].sum().value_counts().sort_values()
            axs[i].plot(counts, counts.index)
            axs[i].set_title(self._config['algorithms'][i].__name__)
            axs[i].set_ylabel('Successful Prisoners')
            axs[i].set_xlabel('Number of Trials')
        plt.tight_layout()
        plt.show()
                               
    def simulate(self):
        ''' This runs the prisoner problem simulation on all trials with all algorithms, as specified in config, using the Trial object defined above for each trial. 


        Parameters
        -----------
        Input: config with mandatory keys nPrisoners [int], nTrials [int], and algorithms [functions of specific form as described in algorithms.py]. Optional keys include chunks, which 
        determines how often you get progress updates on trial runs (the number of chunks is the number of updates) and lower, which determines whether odd-numbered simulations get one 
        fewer or one extra attempt for the prisoners (as prisoners should get half the amount of prisoners in attempts on selecting the envelopes).

        Output: A pandas dataframe containing data and extra of every trial with all algorithms, organized as results[algorithm][data] or results[algorithm][extra]. '''
        
        for i in range(self._config['nTrials']):
            # This just handles the progress updates.
            if (self._config['chunks'] != None) & ((i % int(self._config['nTrials']/self._config['chunks'])) == 0):
                print('Progress: Currently on trial ' + str(i))
            # Now, for each trial, initialize an object of the Trial class with parameters provided by the config. We can use the config's opts for kwargs, but remove chunks.
            trial_opts = self._config._opts.copy()
            trial_opts.pop('chunks')
            trial = Trial(self._config['nPrisoners'], self._config['algorithms'], **trial_opts)
            trial.run_all()
            for algorithm in self._config['algorithms']:
                self._results[algorithm.__name__]['data'] = pd.concat([self._results[algorithm.__name__]['data'], pd.Series(trial._result[algorithm.__name__]['data'], name='Trial ' + str(i))], axis=1)
                if trial._result[algorithm.__name__]['extra'] != None:
                    for key in trial._result[algorithm.__name__]['extra']:
                        if key not in self._results[algorithm.__name__]['extra'].keys():
                            self._results[algorithm.__name__]['extra'][key] = pd.DataFrame(dtype=np.float64)
                    for key in self._results[algorithm.__name__]['extra']:
                        self._results[algorithm.__name__]['extra'][key] = pd.concat([self._results[algorithm.__name__]['extra'][key], pd.Series(trial._result[algorithm.__name__]['extra'][key], name='Trial ' + str(i))], axis=1)
        if self._config['chunks'] != None:
            print('Concluded: Finished trial ' + str(i) + ' and stored in .results!')
        self.stats