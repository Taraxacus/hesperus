#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# simulation.py:

from game import run
import numpy as np

def test(gui):
    try:
        n = int(input("Number of tests? "))
    except:
        n = 100
    list_turns= []
    list_times= []
    for i in range(n):
        turn, times = run(gui)
        list_turns.append(turn)
        list_times.append(times)
        print(times)
        if i == 0:
            list_times.pop()
    len_times = len(list_times[0])
    list_time = [times[len_times-1] - times[0] for times in list_times]
    time_mu = sum(list_time)/n
    time_sigma = np.sqrt( sum([(t-time_mu)**2 for t in list_time]) /n)
    time_rel = 100*time_sigma/time_mu
    turns_mu = sum(list_turns)/n
    turns_sigma = np.sqrt( sum([(t-turns_mu)**2 for t in list_turns]) /n)
    turns_rel = 100*turns_sigma/turns_mu
    #print(mu, sigma)
    print(f"Average time per game: {time_mu} +- {time_sigma} seconds. Relative deviation: {time_rel} %")
    print(f"Average number of turns per game: {turns_mu} +- {turns_sigma}. Relative deviation: {turns_rel} %")
    #turn_time = time_sigma/turns_sigma
    #print(f"Estimated time per turn: {turn_time} seconds")
    #list_pregame = [list_time[i] - list_turns[i]*turn_time for i in range(n)]
    #print(f"List of estimated pre-game times: {list_pregame}")
    for i in range(len_times):
        list_time_i = [times[i] for times in list_times]
        time_mu_i = sum(list_time_i)/n
        time_sigma_i = np.sqrt( sum([(t-time_mu_i)**2 for t in list_time_i]) /n)
        rel = 100* time_sigma_i/time_mu_i
        print(f"Average time in stage {i}: {time_mu_i} +- {time_sigma_i} seconds. Relative deviation: {rel} %")
        if i == len_times-1:
            total_time = sum(list_time_i)
            total_turns = sum(list_turns)
            turn_time = total_time/total_turns
            print(f"Average turn time: {turn_time} seconds")
