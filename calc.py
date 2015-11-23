import math

from numpy import mean, polyfit as pf, polyval, \
resize, reshape, max, min
from scipy.signal import butter, filtfilt, freqz
from peakdetect import peakdet
from scipy.stats import sem, t


def esimate_noise_amplitude(y,confidence=.95):
    """ Returns high and low estimate of the noise levels.
        we're defining noise as the points that are within 
        the 95% confidence interval of the data. 

        so basically there should be a lot of points centered around one 
        number. anything significantly outside of that interval is different.
        
        Note. This should only be run with adjusted data. i.e. once the polyfit 
        has been removed. 

        if there's drift it'll screw everything up 
        ARGS ----
        y = array of data 
        confidence (defaults to 95). 

        RETURNS ----
        low estimate, high estimate, mean, std error, degrees of freedom
        """
    m = mean(y)
    s = sem(y)
    n = len(y)
    h = s * t.ppf((1+confidence)/2., n-1)
    return m-h,m+h,m,s,n-1


def find_peaks(x,y, delta = .004):
    """ this applies the peak detection algorithm. 
        look at the source code to find out....
        """
    print('x', len(x))
    print('y',len(y))
    print('delta',delta)
    mx,mn= peakdet(y,delta,x=x)
    
    return mx.T,mn.T


def polyfit(x,y,d=3):
    """ Returns an array of the same length as y/x 
        that contains the y values computed from the best fit polynomial 
        of degree = d
        """
    coefs = pf(x,y,d)
    bestfit = polyval(coefs,x)
    return bestfit


def moving_average(a, n=10):
    """ Returns an array filled with moving averages
        The returned array will be the same length as a.
            thererefore you don't need to do anything weird to the x values. 

        moving average is calculated by taking n points and averaging them
        then replace those n points by the average.
        continue for all points. 

        If the array doesn't nicely fall into bins of n points, the array is extended by 
        repeating the last element. thererefore the average for that bin will be close to
        the last number of the bin. This could substatialy change. but probably better than 
        the alternatives.
            the extra indices are then cut off. and the answer returned. 
            probably don't trust the last bin. unless you're sure. 

        args    -> a = array to calculate over (1d)
                -> n = number of datapoints to bin
        """
        # resizes the array
    len_orig = len(a)
    resized = resize(a, math.ceil(float(len(a))/n)*n)
    len_resized = len(resized)
    added_indices = len_resized - len_orig 
    # for any indices added we just want to repeat the last value. 
        # not repeat the whole array
    last_index = a[-1]
    for i in reversed(xrange(added_indices)):
        resized[-1*i - 1] = last_index

    binned = reshape(resized,(-1,n)) 
        # turns 1d array into x rows of n cols.     
    for i,b in enumerate(binned):
        ave = mean(b)
        b = [ave for l in b] # set the whole of b to be the average
        binned[i] = b
    # turn it back into a 1d array
    unfurled = reshape(binned, -1)
    return unfurled[0:len_resized - added_indices] # don't return the extra indeces created during reshaping


def filter(data, order=5, cutoff=.001, btype='high'):
    """ returns a filtered set of data. 
        filtered by applying a butterworth filter
        of order (5),
        with cutoff (.001Hz)
        and type = (high, low, bandpass, bandstop)
        """
    b,a = butter(order,cutoff,btype=btype)
    data = filtfilt(b,a,data)
    return data

def minarray(y):
    ''' returns an array which is a line along the minimum 
    of the array. returns the same dimensions'''
    return [min(y)] * len(y)

def maxarray(y):
    ''' returns an array which is a line along the minimum 
    of the array. returns the same dimensions'''
    return [max(y)] * len(y)

def meanarray(y):
    ''' returns an array which is a line along the minimum 
    of the array. returns the same dimensions'''
    return [mean(y)] * len(y)

