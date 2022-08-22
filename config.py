import warnings
from numpy import ndarray

from algorithms import Algorithm

class Config:
    def __init__(self, nPrisoners, nTrials, algorithms, **kwargs):
        self._reqs = {'nPrisoners': nPrisoners, 'nTrials': nTrials, 'algorithms': algorithms}
        self._opts = kwargs
        
        self._verify()
    
        # The actual config, to be accessed by the user.
        self._setConfig({**self._reqs, **self._opts})

    def _verify(self):
        ''' This function verifies that both the required and optional arguments have the appropriate form. See their specifications below. '''
        self._verify_reqs()
        self._verify_opts()
        
    def _setConfig(self, config):
        ''' This function sets the config once it has been verified. This is the only property that should be accessed by the user. '''
        self.config = config
        
    def __getitem__(self, key):
        return self.config[key]
    
    def _verify_reqs(self):
        ''' Helper function that checks that all of the mandatory keys are specified appropriately and gives errors otherwise. 
        
        
        Parameters
        ---------------------
        algorithms: the algorithms the prisoners will use to open the envelopes
        nPrisoners: the number of prisoners in the experiment
        nTrials: the number of trials in the experiment
        
        Output: None if successful (or warning), otherwise error.
        '''
        
        
        def _standardize(dict_, key, type_):
            ''' Helper function that standardizes a key in dict_ to the type_ specified. '''
            dict_[key] = type_(dict_[key])
        
        # Verify that algorithms specified were a tuple-type object.
        if type(self._reqs['algorithms']) != tuple:
            # Check if it's a 1D numpy array or list. These are acceptable inputs, but we'll standardize them to a tuple for internal consistency.
            if type(self._reqs['algorithms']) == list:
                _standardize(self._reqs, 'algorithms', tuple)
            elif (type(self._reqs['algorithms']) == ndarray) & (self._reqs['algorithms'].ndim == 1):
                _standardize(self._reqs, 'algorithms', tuple)
            # If a single algorithm is specified as a function, it doesn't need to be in a tuple, but we again standardize the behavior to a tuple.
            elif callable(self._reqs['algorithms']):
                _standardize(self._reqs, 'algorithms', tuple)
            # Otherwise, we can try to convert it to a tuple, but we should shoot a warning 
            else:
                try:
                    _standardize(self._reqs, 'algorithms', tuple)
                    warnings.warn('Algorithm type not recognized as standard, but conversion was possible. \
                    You should manually verify the simulation executed correctly despite this discrepency.', SyntaxWarning, stacklevel=2)
                except TypeError:
                    raise TypeError('Algorithms poorly specified in config. Please input them as a tuple of functions.')
        
        # Verify that each algorithm in algorithms corresponds to a subclass of Algorithm. Everything should be standardized to a tuple now!
        for algorithm in self._reqs['algorithms']:
            if not issubclass(algorithm, Algorithm):
                raise TypeError(str(algorithm) + ' does not correspond to a subclass of the Algorithm class.')
                
        # Now we double check that nPrisoners and nTrials are ints.
        for key in self._reqs.keys():
            if key == 'algorithms':
                continue
            else:
                # If not an int, we get a ValueError and want to return an error.
                try:
                    # Check that each input is equal to the integer of itself, then standardize to int.
                    if self._reqs[key] == int(self._reqs[key]):
                        _standardize(self._reqs, key, int)
                    else:
                        raise TypeError(key + ' must be an integer!')
                except ValueError:
                    raise TypeError(key + ' must be an integer!')
                    
    def _verify_opts(self):
        ''' Helper function that checks that all of the optional keys are specified appropriately and gives warnings otherwise. 
        
        
        Parameters
        ---------------------
        lower: on odd simulations, whether prisoners open half-1 or half+1 envelopes.
        chunks: the behavior of the progress bar. The number of chunks is the number of (evenly-spaced) updates you will receive.
        
        Output: None if successful (or warning), otherwise error.
        '''
        
        
        def _standardize(dict_, key, type_):
            ''' Helper function that standardizes a key in dict_ to the type_ specified. '''
            dict_[key] = type_(dict_[key])
        
        # Make sure lower is properly specified. It should be a Boolean.
        if 'lower' not in self._opts.keys():
            # Give a warning if lower isn't specified with an odd-numbered simulation.
            if (self._reqs['nPrisoners'] % 2) == 1:
                warnings.warn('The number of envelopes is odd, so opening half of the envelopes is ambiguous. \
                            Defaulting to rounding down (\'lower\'=True) since this is the tighter constraint on the simulation. \
                            If you would prefer to round up, specify \'lower\'=False in the config.', stacklevel=2)
                self._opts['lower'] = True
        elif type(self._opts['lower']) != bool:
            if (self._reqs['nPrisoners'] % 2) == 1:
                warnings.warn('lower is inappropriately specified. It should be a Boolean. \
                            Defaulting to rounding down (\'lower\'=True) since this is the tighter constraint on the simulation. \
                            If you would prefer to round up, specify \'lower\'=False in the config.', stacklevel=2)
                self._opts['lower'] = True
            else:
                warnings.warn('lower is inappropriately specified. It should be a Boolean. As the simulation has an even number of prisoners, this means nothing and can be ignored.', stacklevel=2)
                self._opts['lower'] = True
                
        # If chunks is not specified, default to None.
        if 'chunks' not in self._opts.keys():
            self._opts['chunks'] = None
        # Send division by zero to default.
        elif self._opts['chunks'] == 0:
            self._opts['chunks'] = None
        elif self._opts['chunks'] == None:
            pass
        else:
            # If not an int, we get a ValueError but we want to return a warning and issue default behavior.
            try:
                # Check that each input is equal to the integer of itself, then standardize to int. Error catches non-numeric types, conditional handles floats and other numeric types.
                if self._opts['chunks'] == int(self._opts['chunks']):
                    _standardize(self._opts, 'chunks', int)
                else:
                    warnings.warn('chunks should be an integer! Defaulting to no progress updates.', stacklevel=2)
                    self._opts['chunks'] = None
            except ValueError:
                warnings.warn('chunks should be an integer! Defaulting to no progress updates.', stacklevel=2)
                self._opts['chunks'] = None
        
        # If nEnvelopes is not specified, default to nPrisoners.
        if 'nEnvelopes' not in self._opts.keys():
            self._opts['nEnvelopes'] = self._reqs['nPrisoners']
        # Otherwise, check that it's an int as we did with chunks above.
        else:
            try:
                if self._opts['nEnvelopes'] == int(self._opts['nEnvelopes']):
                    _standardize(self._opts, 'chunks', int)
                else:
                    warnings.warn('nEnvelopes should be an integer! Defaulting nEnvelopes to nPrisoners.', stacklevel=2)
                    self._opts['nEnvelopes'] = self._reqs['nPrisoners']
            except ValueError:
                warnings.warn('nEnvelopes should be an integer! Default nEnvelopes to nPrisoners.', stacklevel=2)
                self._opts['nEnvelopes'] = self._reqs['nPrisoners']
        # Finally, nEnvelopes must be greater than nPrisoners. If there's more envelopes, it's fine. Some will just not correspond to prisoners.
        if self._opts['nEnvelopes'] < self._reqs['nPrisoners']:
            warnings.warn('nEnvelopes is smaller than nPrisoners, but there must be at least as many envelopes as prisoners. Defaulting nEnvelopes to nPrisoners.', stacklevel=2)
            self._opts['nEnvelopes'] = self._reqs['nPrisoners']
                
        # If schema is not specified, set it to default.
        if 'schema' not in self._opts.keys():
            self._opts['schema'] = 'default'
            
        # If schema is defined but not in the schema keys, set it to default with a warning.
        schemas = ['default', 'modified']
        if self._opts['schema'] not in schemas:
            warnings.warn('schema should be one of ' + str(schemas) + ' but got ' + str(self._opts['schema']) + '. Setting to default.', stacklevel=2)
            self._opts['schema'] = 'default'
            
        # Check if there are any other keys specified.
        for key in self._opts.keys():
            if key in ['lower', 'chunks', 'nEnvelopes', 'schema', 'param']:
                continue
            else:
                warnings.warn(str(key) + ' was provided as an optional argument, but it does not correspond to anything in the config.', stacklevel=2)
                
def parse_config(**kwargs):
    # Handle mandatory keys.
    try:
        nPrisoners = kwargs.pop('nPrisoners')
        nTrials = kwargs.pop('nTrials')
        algorithms = kwargs.pop('algorithms')
    except KeyError:
        raise KeyError('Missing mandatory keys. Ensure nPrisoners, nTrials, and algorithms are all specified in your config dictionary.')
        
    # Remaining kwargs are optional keys.
    opts = kwargs
    
    cfg = Config(nPrisoners=nPrisoners, nTrials=nTrials, algorithms=algorithms, **opts)
    return cfg