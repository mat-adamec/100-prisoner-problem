import math
import random
import warnings

import numpy as np

class AttemptSchema():
    ''' This class exists to handle cases of the simulation where the number of attempts is anything other than half of the number of envelopes. The possible attempt schemas include:
    
    default: the default behavior. The number of attempts is half the number of envelopes. No parameter.
    modified: similar to the default behavior, but allows variation in the number of attempts. The formula for attempts is attempts = nEnvelopes/param, so the parameter serves as a divisor. Thus, param=2 replicates the default behavior.
    
    Others can be defined as functions which return the number of attempts, so long as they are added to the appropriate maps at the beginning of the __init__.
    
    The lower key determines whether indivisible integers are raised or lowered.
    '''
    def __init__(self, envelopes, schema='default', param=None, **kwargs):
        self._nEnvelopes = len(envelopes)
        self._schema = schema
        self._params = {'param': param, 'lower': kwargs.pop('lower')}
        
        type_map = {'default': (None), 'modified': (int)}
        func_map = {'default': self._default, 'modified': self._modified}
        self.attempts = func_map[self._schema](self._nEnvelopes, **self._params)
        
    def _round(self, attempts, lower=True):
        ''' This helper function rounds the inputted attempts up or down, depending on the value of lower. '''
        if lower==True:
            attempts = math.floor(attempts)
        else:
            attempts = math.ceil(attempts)
        return attempts
        
    def _default(self, nEnvelopes, param=None, lower=True):
        return self._round(nEnvelopes/2, lower)
        
    def _modified(self, nEnvelopes, param, lower=True):
        return self._round(nEnvelopes/param, lower)
                   
                   
            
            
class Algorithm():
    def __init__(self, prisoner, envelopes, **kwargs):
        ''' Initialize the variables necessary to execute the selection algorithm. If attempt_scheme is default, prisoners get half the attempts
        We also want to store two outputs: whether the run was successful and whether any extra information was provided by the algorithm (in a dictionary). '''
        self._prisoner = prisoner
        self._envelopes = envelopes

        # For non-standard prisoner problem, we need to specify a schema for the number of attempts.
        self._schema = AttemptSchema(envelopes, **kwargs)
        self._attempts = self._schema.attempts
        
        self._unchecked = self._envelopes.copy()
        
        # Initialize results.
        self.result = None
        self.extras = None
    
    def _run(self, prisoner, unchecked, attempts):
        ''' This is where the selection algorithm is actually provided. Intended to be subclassed with specific implementations. Returns a guess - an envelope to be opened. '''
        pass
    
    def select(self):
        ''' This just automates the selection on the class' initialization variables. This is the user-facing function. It may need to be edited with kwargs depending on how _guess is defined. '''
        out = self._run(self._prisoner, self._unchecked, self._attempts)
        if type(out) == tuple:
            self.result = out[0]
            self.extras = out[1]
        else:
            self.result = out
        return self.result, self.extras
    
class RandomSelect(Algorithm):
    def __init__(self, prisoner, envelopes, **kwargs):
        super().__init__(prisoner, envelopes, **kwargs)
    
    def _run(self, prisoner, unchecked, attempts):
        success = False
        while (success == False) & (attempts > 0):
            attempts -= 1
            # Choose an index at random.
            guess = random.choice(range(len(unchecked)))
            check = unchecked[guess]
            # Remove the index from the unchecked list since it's now been checked. We don't care about preserving indices when we're making a random choice.
            unchecked = np.append(unchecked[:guess], unchecked[-guess:])
            if prisoner == check:
                success = True
        return success
        
class LoopSelect(Algorithm):
    def __init__(self, prisoner, envelopes, **kwargs):
        super().__init__(prisoner, envelopes, **kwargs)
        
    def _run(self, prisoner, unchecked, attempts):
        success = False
        # Initialize the previous checked envelope at the index of the prisoner's number.
        check = prisoner
        loop_size = 0
        # Here, we moved the attempts to the success check so that we can continue counting the loop size even after the prisoner has failed.
        while (success == False):
            attempts -= 1
            loop_size += 1
            # Check the envelope corresponding to the last envelope's result. We don't need to update unchecked since we're going to find a closed loop, so there will be no repeats. In fact, we don't want to update it because that would mess up the indices for the loop!
            guess = check
            check = unchecked[guess]
            if prisoner == check:
               # If prisoner still has attempts, success!
               if attempts > 0:
                    success = True
               # Otherwise, get out of the loop!
               else:
                    break
        return success, {'loop_size': loop_size}