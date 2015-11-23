import utils

from parse_file import parse
from plot import plot
from calc import polyfit, find_peaks, mean, moving_average


def process_raw_data(filename = None, 
    maxima = None, 
    binsize=20,
    deg=3,
    delta=.004,
    xlabel='Time (s)',
    title = None,
    **kwargs):
    '''

        Args:
        =======
        -> maxima T/F deteck peaks as maxima or minima
        -> label 

        This function is the main entry point.
        given a file it will do the whole processing... thing...
        this is mainly just to make it easier.

        this is very much dependant on the structuer of the datafile!
        If you change acquisition!!! change this!!!!

    '''
    # ASSUMPTIONS!!!!!! change these. there may be more subtle assumptions
    # further in. 
    inputV = 'Voltage_0'    # input signal, to track phase changes
    outputV = 'Voltage_1'   # output signal, to track particles
    x = 'X_Value'           # time array, 

    r = parse(filename=filename, **kwargs) # parse the datafile
    assert(inputV in r) # __ASSUMPTIONS__ we know this to be the input signal
    assert(outputV in r) # __ASSUMPTIONS__ we know this to be the output signal


    # add some useful info 

    r['input ave'] = [mean(r[inputV])] * len(r[inputV])
    r['output ave'] = [mean(r[outputV])] * len(r[outputV])

    # =============================
    ''' Smooth the output to remove large peaks resulting from rare noise events '''
    r['smoothed output'] = moving_average(r[outputV], n=binsize)
    r['bin size'] = binsize
    
    # =============================
    ''' remove instrumental drift. By fitting a polynomial to the 
        output signal, then subtracting it. '''
    r['polyfit to output'] = polyfit(r[x],r[outputV], d=deg)
    r['deg'] = deg

    r['output adjusted'] = r['smoothed output'] - r['polyfit to output']


    # ==============================
    ''' Run the detect peak algorithm to count the peaks in the datafile. '''
    mx, mn = find_peaks(r[x], r['output adjusted'], delta=delta)
    if maxima: 
        r['particles'] = mx
        r['number of particles'] = len(mx)
    else: 
        r['particles'] = mn 
        r['number of particles'] = len(mn)
    r['max'] = maxima
    r['delta'] = delta


    # =============================
    ''' The hard part is done. just plot the results. 
        I want to produce one summary graph. that displays the processing pipeline
        and one that is just the results. 
    '''
    plots = [
        ('Raw Output', r[outputV]),
        ('Smoothed Output', r['smoothed output']),
        ('Result', r['output adjusted'])
    ]
    plot(r[x], plots, x_title=xlabel, plot_title=title, measurements=[])

    # =============================
    # and we're done. return the results just for goodness sake. 
    return r 





process_raw_data()





