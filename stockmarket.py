"""
!IMPORTANT!
This code should be run on CodeSkulptor to access the comp140_module3 module. 
A link can be found here: https://py3.codeskulptor.org/#user308_jWYuGPbBsv_0.py.
"""

import comp140_module3 as stocks
import random

def markov_chain(data, order):
    """
    Create a Markov chain with the given order from the given data.

    inputs:
        - data: a list of ints or floats representing previously collected data
        - order: an integer repesenting the desired order of the markov chain

    returns: a dictionary that represents the Markov chain
    """
    chain = {}
    length = len(data)
    for num in range(length - order):
        state = tuple(data[num: num + order])
        event = data[num + order]
        # the two if-statements creates a dictionary if there is none for a given 
        # state, and also creates a key-value pairing in the dictionary associated
        # with a state if there is none
        if state not in chain:
            chain[state] = {}
        if event not in chain[state]:
            chain[state][event] = 1
        # code below increments existing key-value pairing
        else:
            chain[state][event] = chain[state][event] + 1
    for dictionary in chain:
        # count total number of data points in a given dictionary
        count = 0
        for key in chain[dictionary]:
            count += chain[dictionary][key]
        # divide by count to get probability
        for key in chain[dictionary]:
            chain[dictionary][key] = chain[dictionary][key]/count
    return chain


### Predict

def make_choice(dictionary):
    """
    Predict the next choice based on a dictionary that represents a 0th order 
    Markov chain.
    
    inputs:
        - dictionary: a dictionary representing a Markov chain
    
    returns: a random weighted result based on the Markov chain
    """
    # generates a random number from 0 to 1
    random_number = random.random()
    # we make a new dictionary based on adding the cumulative probabilities
    # of the given dictionary to create intervals from 0 to 1 that correspond
    # to each of the keys in the dictionary
    prefix_sum = {}
    chance = 0
    for key in dictionary:
        chance += dictionary[key]
        prefix_sum[key] = chance
    for key in dictionary:
        if key in prefix_sum and random_number < prefix_sum[key]:
            return key
    # return 3 is here in case float addition does not add to 1 and there is some
    # left over
    return 3

def predict(model, last, num):
    """
    Predict the next num values given the model and the last values.

    inputs:
        - model: a dictionary representing a Markov chain
        - last: a list (with length of the order of the Markov chain)
                representing the previous states
        - num: an integer representing the number of desired future states

    returns: a list of integers that are the next num states
    """
    prediction = []
    # we choose to make a copy -- otherwise state would directly modify the inputs
    state = last.copy()
    for index in range(num):
        if tuple(state) in model:
            choice = make_choice(model[tuple(state)])
            prediction.append(choice)
        # else statement runs if there is no key-value pairing and makes a 
        # uniformly random decision
        else:
            choice = random.randrange(0,4)
            prediction.append(choice)  
        state.pop(0)
        state.append(choice)
    return prediction

### Error

def accuracy(result, expected):
    """
    Calculate the accuracy between two data sets.

    The length of the inputs, result and expected, must be the same.

    inputs:
        - result: a list of integers or floats representing the actual output
        - expected: a list of integers or floats representing the predicted output

    returns: a float that is the mean squared error between the two data sets
    """
    count = 0
    for index in range(len(result)):
        if result[index] == expected[index]:
            count += 1
    return count / len(result)


### Experiment

def run_experiment(train, order, test, future, actual, trials):
    """
    Run an experiment to predict the future of the test
    data given the training data.

    inputs:
        - train: a list of integers representing past stock price data
        - order: an integer representing the order of the markov chain
                 that will be used
        - test: a list of integers of length "order" representing past
                stock price data (different time period than "train")
        - future: an integer representing the number of future days to
                  predict
        - actual: a list representing the actual results for the next
                  "future" days
        - trials: an integer representing the number of trials to run

    returns: a float that is the mean squared error over the number of trials
    """
    chain = markov_chain(train, order)
    # sums mse over all trials
    accuracy_sum = 0
    for num in range(trials):
        accuracy_sum += accuracy(predict(chain, test, future), actual)
    # gives mean sme by dividing over trials
    return accuracy_sum / trials


### Application

def run():
    """
    Runs application.
    """
    # Get the supported stock symbols
    symbols = stocks.get_supported_symbols()

    # Get stock data and process it

    # Training data
    changes = {}
    bins = {}
    for symbol in symbols:
        prices = stocks.get_historical_prices(symbol)
        changes[symbol] = stocks.compute_daily_change(prices)
        bins[symbol] = stocks.bin_daily_changes(changes[symbol])

    # Test data
    testchanges = {}
    testbins = {}
    for symbol in symbols:
        testprices = stocks.get_test_prices(symbol)
        testchanges[symbol] = stocks.compute_daily_change(testprices)
        testbins[symbol] = stocks.bin_daily_changes(testchanges[symbol])


    # Run experiments
    orders = [4]
    ntrials = 500
    days = 5

    for symbol in symbols:
        print(symbol)
        print("====")
        print("Actual Data:", testbins[symbol][-days:])
        for order in orders:
            error = run_experiment(bins[symbol], order,
                                   testbins[symbol][-order-days:-days], days,
                                   testbins[symbol][-days:], ntrials)
            print("Accuracy", order, ":", error)

           
run()
