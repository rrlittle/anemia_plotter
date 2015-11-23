import time

from matplotlib import pyplot as plt
from calc import meanarray, maxarray , minarray, polyfit

def plot(x, y_list, x_title = 'Time', plot_title = None, measurements=['ave']):
    """ This plots x vs y. it supports multiple y lists, 
        but they all must be of the same length. 
        args    -> y_list should be a list of tuples. 
                    [(title, [values]), (title, [values]),...]
                -> x_title defaults to 'Time'
                -> plot_title defaults to filename '_summary'
                -> measurements is an array of strings. of additional calculations to 
                        plot on each graph
                    - ave  - -
                    - max  ^ / min V
                    - bestfit,deg o
        """

    print('Plotting : ', ','.join([y[0] for y in y_list]))
    # plt.ion()   # make plotting interactive
    
    #CHECK THE ARGS
    # ensure they supplied some y_vals
    assert(y_list)
    assert(len(y_list) >= 1)
    assert(type(y_list[0]) is tuple) # ensure it's a list of tuples. 

    #ensure all the arrays are of the same length
    data_lengths = [len(v[1]) for v in y_list] # get the lengths of all the datasets
    data_length_set = set(data_lengths) # make a set out of it, which has unique elems 
    assert(len(data_length_set) == 1) # ensure there is only one unique length.
    
    assert(len(y_list[0][1]) == len(x)) # ensure x and y's match as well. 


    # plot them!
    plt.figure() # start a new figure
    if(not plot_title): # set a title, default to current time. 
        plot_title = time.strftime('%d %H:%M')
    plt.title(plot_title)
    cur_plot = 1

    print('y_list is: {}'.format(y_list))
    for y in y_list:
        y_title = y[0] # the y title 
        y_vals = y[1] # the list of y values to be plotted
        plt.subplot(len(y_list),1,cur_plot) # initialize the plot
        plt.plot(x,y_vals)  # plot the data
        
        for m in measurements: # plot stuff about each plot
            print(m)
            if(m is 'ave'): 
                plt.plot(x, meanarray(y_vals), 'm--')
            if(m is 'max'): 
                plt.plot(x, maxarray(y_vals), 'k^')
            if(m is 'min'): 
                plt.plot(x, minarray(y_vals), 'kv')
            if('bestfit' in m): 
                deg = m.split(',')[1]
                plt.plot(x, polyfit(x, y_vals, d=deg), 'mo')

        plt.ylabel(y_title)   # set the title. I've had enough of unlabeled charts
        cur_plot = cur_plot +1  # go to the next chart
    plt.show()
    

plt.ion()