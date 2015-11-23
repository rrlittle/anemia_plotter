'''
    This script contains accessing routines for lvm datafiles 
    produced by the `acquisition.vi` labview program.

'''
import numpy as np
from os import popen2 # to use os' tail command 
from utils import prettify  # pretty printing 
from errors import noFileException  # error if no file is given. 
from Tkinter import Tk # 
from tkFileDialog import askopenfilename

def parse(filename = None, 
    lines = 100000, 
    grab_from = 'front', 
    offset = 0, 
    exclusions=['Comment'],
    header_lines=24,
    header_scheme={
        'start_time':11,
        'delta_x':21,
        'column_titles':23
    },
    output=True,
    **kwargs):
    
    """ Parses the lvm file produced by the acquisition vi. 
        args (all optional)
        -----------
        -> filename if none provided you will be prompted by a gui
        -> lines. limits file size by grabbing only the first N lines. 
                defaults to 100,000 lines
        -> grabFrom. do we grab N lines from the front or the back?
            ('front' or 'back')
        -> offset. skip N lines from either the back or the front
        -> exclusions:
        -> header_lines: used to specify the schema for the header.
                        if you update the script you should be able to
                        make this work by respecifying the header info here.
                        the header is 24 lines long by default.
        -> header_scheme: a dictionary that contains the locations of the
                    useful things.
                    There should be:
                    - start_time
                    - delta_x
        -> output : True/False, print things. or not... up to you. 

        Throws noFileException
        returns a bunch of stuff in a dict. they all have descriptive 
            key names
        {   sampling frequency
            delta x
            input/output ave array
            input/output array
            output binned with 20 datapoints
            time array
            manual_particle_detector, a list of 1 or zero. }

        also plots some summary data i.e. particels, out, & input
        
        Notes
        =========
            This does assume some things about the datafiles structures.
            
            1. there should be a comment consisting with a timestamp & 
            the result from the manual_particle_detector button within the 
            acquisition.vi program. you can press it to mark specific parts of the 
            datafile. Mainly used to mark particles passing. 

            2. the comment should be the last column. this DOES NOT CARE how often 
            the comment is filled in. This will replace any empty comment rows with the 
            most recent filled one. you'll have repeats, but that's fine. Most of the 
            functions in this package require consistant list lengths for x/y values.    


        """

    seprator = '\t' # we assume these are tab seprated values.

    # open the file
    f = getfile(filename)

    # read the header                                          
    header = [next(f).strip() for x in xrange(header_lines)]   
    if output: print('\n'.join([str(i) + ':\t' +x  for i,x in enumerate(header)]))

    # ================
    # Parse the header
    # ================
    
    ## === start_time ========================
    start_time_line = header[header_scheme['start_time']]
    # start time line looks like: "Time \t timestr \t timestr"
    start_time_line_split = start_time_line.split(seprator) 
    # ----------
    start_time = start_time_line_split[1][:15] # grab HH:MM:SS.SSSSSSSSSSS

    
    ## === sampling frequency ================
    delta_x_line = header[header_scheme['delta_x']]
    delta_x_line_split = delta_x_line.split(seprator)
    # ---------
    delta_x = float(delta_x_line_split[2])
    sampling_freq = 1/ delta_x

    
    # === column titles =====================
    column_title_line = header[header_scheme['column_titles']]
    column_title_line_split = column_title_line.split(seprator)
    # ---------
    column_titles = column_title_line_split # grab all the column names
    num_cols = len(column_titles) # the number of columns in the file.  


    # ================
    # Parse the files
    # ================

    # === Grab the file ================
    datalines = None # container to hold the lines read from the file. 
    if grab_from == 'back':
        datalines = tail(lines, f=f, output=output, offset=offset)
    else:
        [next(f) for x in xrange(offset)]               # eat the offset lines
        datalines = f

    # === prep the columns ============
    columns = {}    # dict to hold column vars
    columns_map = {} # dict with same keys, but with column index in dat file.

    for i,col in enumerate(column_titles):
        columns[col] = [] # initialize a list to hold the column
        columns_map[col] = i # remember what index the column is
    columns['manual_particle_detector'] = [] 
        # assuming the datafile contains the manual patricle detector button.
        # which is recorded within the comment.  

    # === read the file =============
    for i,l in enumerate(datalines):
        dataline_split = l.strip().split(seprator)
        # if this row has no comment, get it from the previous line
        if len(dataline_split) != num_cols:
            dataline_split.append(columns['Comment'][-1])

        for k in columns:
            if k == 'manual_particle_detector':
                particle_present = dataline_split[-1].split(',')[-1]
                columns[k].append(particle_present)
            else:
                columns[k].append(dataline_split[columns_map[k]])
            if k != 'Comment':
                columns[k][-1] = float(columns[k][-1]) # convert to float

    for k in columns:
        columns[k] = np.array(columns[k])

    f.close() # we have read the file. close it now.

    # ============
    # Return stuff
    # ============
    to_ret = {k:columns[k] for k in columns if k not in exclusions}
    to_ret['numcols'] = num_cols
    to_ret['delta_x'] = delta_x
    to_ret['start_time'] = start_time
    to_ret['sampling frequency'] = sampling_freq
    to_ret['filename'] = filename

    if output: print(prettify(to_ret))
    return to_ret



def tail(n, filename=None, offset=0, output=True): # returns the last n lines of the file. 
    """ This grabs the last N lines from a file. 
        if filename is unspecified you'll be prompted for a file.

        this is kind of interesting. we're running the shell command:
        `tail -n n filename` if your os doesn't support tail then this may not work.
        I developed this on linux and updated it on windows 7.  
        """
    if filename is None:
        filename = getfile(filename, o=False)
    filename = '\'' + filename + '\''
    string = "tail -n " + str(n + offset) + " " + filename 
    if output: print(string)
    stdin,stdout = os.popen2(str(string))
    lines = stdout.readlines()
    stdin.close()
    stdout.close()
    return lines[:lines.__len__() - offset]


def getfile(filename, o=True): # Manages opening the datafile to parse 
    '''
        returns a file object or raises noFileException with text 
        describing the cause
        o: True/False, if true returns file object, else filename

        if filename is None:
            opens up a gui to prompt the user for a filename
        else:
            tries to open the file
    '''
    if filename is None:
        filename = askopenfilename()
    if filename is None:
        raise noFileException('No File selected')

    try:
        f = open(filename)
        return f
    except Exception as e:
        raise noFileException('Exception while trying to open {}. \
            Error: {}'.format(filename, e))

Tk().withdraw()