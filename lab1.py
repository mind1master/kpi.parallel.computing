# Find max norm of a random filled vector sequentially and parallel.

import sys
import time

import numpy.random as nprnd
from multiprocessing import Process
from multiprocessing.sharedctypes import Value
    
def divide_into_piles(vector, processes_number):
    """Divide initial vector into pieces, called piles."""
    piles = []
    for pile_id in xrange(processes_number):
        pile_size = len(vector) / processes_number
        remainder = len(vector) - (pile_id+1) * pile_size
        if remainder < pile_size:
            cur_pile_size += remainder
        else:
            cur_pile_size = pile_size
        pile = vector[pile_id*pile_size: (pile_id+1)*cur_pile_size]
        piles.append(pile)
    return piles
    
def fill_vector(size):
    """Fill a vector with random numbers."""
    return nprnd.randint(1000, size=size)
    
def find_max_norm(shared_value, vector):
    """Find max norm of the vector. max_norm is a shared value, used for 
    acessing after process finished."""
    max_norm = 0
    for number in vector:
        absolute_number = abs(number)
        if absolute_number > max_norm:
            max_norm = absolute_number
    shared_value.value = max_norm

def run_sequentially(vector):
    """Execute process of finding vector's max norm sequentially."""
    max_norm = Value('i', 0)
    process = Process(target=find_max_norm, args=(max_norm, vector))
    process.start()
    process.join()
    return max_norm.value

def run_parallel(vector, processes_number):
    """Execute process of finding vector's max norm parallel."""
    piles = divide_into_piles(vector, processes_number)
    shared_values = [Value('i', 0) for pile in piles]
    processes = []
    for value, pile in zip(shared_values, piles):
        processes.append(Process(target=find_max_norm, args=(value, pile)))
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    max_norm = 0
    for norm in shared_values:
        if norm.value > max_norm:
            max_norm = norm.value
    return max_norm

def main(size=1000, processes_number=2):
    """Find max norm of the random filled vector sequentially and parallel"""
    vector = fill_vector(size)
    print 'Starting sequantial process...'
    start_time = time.time()
    result = run_sequentially(vector)
    end = time.time() - start_time
    print 'Max norm - %s' % result
    print 'Execution time: %s' % end
    print '='*20
    print 'Starting parallel process...'
    start_time = time.time()
    result = run_parallel(vector, processes_number)
    end = time.time() - start_time
    print 'Max norm - %s' % result
    print 'Execution time: %s' % end
    print '='*20

if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(size=int(sys.argv[1]), processes_number=int(sys.argv[2]))
    else:
        raise Exception(
            'Please specify size of a vector and number of processes.')
