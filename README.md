# The Hundred Prisoner Problem
# The Hundred Prisoner Problem
## Problem Statement
The hundred prisoner problem is a mathematical problem that seeks the optimal solution to the following riddle: 100 prisoners are indexed by numbers which are placed it to 100 envelopes, not necessarily (and indeed, not typically!) in the same order. Each prisoner independently goes in and selects 50 envelopes. If all prisoners find their own number, then all prisoners are freed.

## Solutions
### Random Selection
The naive solution to this problem would involve random choice on the part of each prisoner. But this has an exceptionally low probability of success. Since each prisoner has a 50% chance of success, we would expect the probability that all succeed is (0.5)^100. Virtually no chance at freedom!

### The Loop Method
A better solution exists by reframing the problem in terms of closed loops. Consider this: each prisoner chooses the envelope corresponding to their index, then the envelope corresponding to the index in the previous envelope. The last envelope they choose, if successful, would lead them back to the envelope they first chose (if the process didn't terminate). Thus this is a problem of finding closed loops! Furthermore, the probability of success is the  probability that there is no loop greater in size than 50. Since longer loops are rarer in a random system, this is far more likely to succeed than the random method. 

A corollary is that if prisoners are allowed to swap two envelopes, they can always succeed, as they can divide a loop of size 100 in the worst case into two loops of size 50!

It has been shown that the probability of success with the loop method asymptotically approaches 30% as the number of prisoners increases, and that it is the optimal solution for the problem.

## This Repository
This repository simulates both of the algorithms described above for the hundred prisoner problem. It permits us to modify the number of prisoners in the simulation, the algorithms we wish to use (in case we want to define other ones), and the number of trials we run. It can additionally handle odd numbers of envelopes by an optional raising or lowering parameter, and you can define your own schema for the number of attempts (rather than nEnvelopes/2), in which case the lower parameter handles cases where the schema's number of attempts are not divisible into integers. Finally, there is an optional nEnvelopes parameter to divorce the number of envelopes from the number of prisoners, though the minimal amount of envelopes is the number of prisoners (this is necessary, or the experiment could not succeed). Extra envelopes merely correspond to indices that represent no prisoners.

## Future Improvements
There are performance issues with high numbers of trials, probably because the code currently handles each individual trial as a class. Thus, each individual trial runs and then adds its results to a pandas dataframe. A more efficient solution would treat the trials as an array, run the experiment on the whole array, and then add the results to a dataframe. This is a planned update in the long-term, but for the moment (for my purposes) the current code is sufficient.
