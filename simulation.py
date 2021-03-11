#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# simulation.py:

from game import run
import numpy as np
from player import AICom
from actor import AIIndie

#from collections import Counter
from matplotlib import pyplot as plt

def mu_sigma_rel(list_):
    n = len(list_)
    mu = sum(list_)/n
    sigma = np.sqrt( sum([(t-mu)**2 for t in list_]) /n)
    rel = 100*sigma/mu
    return mu, sigma, rel

def corr(list1, mu1, sigma1, list2, mu2, sigma2):
    if not (len(list1) == len(list2)):
        raise Error
    n = len(list1)
    cov = sum([(list1[i]-mu1) * (list2[i] - mu2) for i in range(n)])/n
    corr = cov/ (sigma1 * sigma2)
    return corr

def print_mu_sigma_rel(variable, mu, sigma, rel):
    print(f"{variable}: {mu} +- {sigma} s, (+- {rel} %)")

def round_list(list_, digit=3):
    return [round(item, digit) for item in list_]

def bucket_time(number):
    r = round(number, 1)
    if r<0:
        r=0.0
    elif r>5:
        r=5.0
    return r

def bucket_turns(number):
    r= 5* (number//5)
    if r<60:
        r=60
    elif r>200:
        r=200
    return r

def test(ui, players=None):
    # Initiate players
    if players is None:
        #players = [AICom(i) for i in range(4)]
        players = [AIIndie(i) for i in range(4)]

    # Number of games
    try:
        n = int(input("Number of tests? "))
    except:
        n = 100

    # Simulate games
    list_turns = []
    list_time = []
    for i in range(n):
        turn, total_time = run(ui, players)
        list_turns.append(turn)
        list_time.append(total_time)
        print(f"Total time of game {i}: {round(total_time,3)},", end=" ")
        print(f"Number of rounds: {turn/4}")
        #if i == 0:
            #list_times.pop()

    # Calculate stats
    time_mu, time_sigma, time_rel = round_list(mu_sigma_rel(list_time))
    turns_mu, turns_sigma, turns_rel = round_list(mu_sigma_rel(list_turns))

    #cov_time_turns = sum([(list_time[i]-time_mu) * (list_turns[i] - turns_mu) for i in range(n)])/n
    #corr_time_turns = cov_time_turns/ (time_sigma * turns_sigma)
    corr_time_turns = corr(list_time, time_mu, time_sigma, list_turns, turns_mu, turns_sigma)
    corr_time_turns = round(corr_time_turns, 3)

    # Print stats
    print_mu_sigma_rel("time per game", time_mu, time_sigma, time_rel)
    print_mu_sigma_rel("turns per game", turns_mu, turns_sigma, turns_rel)
    print(f"Correlation between time and number of turns: {corr_time_turns}.")

    #counter_times = Counter([bucket(time_) for time_ in list_times])
    #plt.bar([x for x in growths.keys()], [g/size for g in growths.values()], bar_width)
    time_dict = {(i/10):0 for i in range(51)}
    for time_ in list_time:
        time_dict[bucket_time(time_)] += 1

    plt.bar(list(time_dict.keys()),  list(time_dict.values()), 0.08)
    plt.title("Verteilung der Spieldauer")
    plt.show()

    turns_dict = {(5*i):0 for i in range(12,41)}
    for turns in list_turns:
        turns_dict[bucket_turns(turns)] += 1

    plt.bar(list(turns_dict.keys()),  list(turns_dict.values()), 4)
    plt.title("Verteilung der Zugzahl")
    plt.show()

    plt.scatter(list_time, list_turns)
    plt.title("Verhaeltnis von Zugzahl und Spieldauer")
    plt.show()

