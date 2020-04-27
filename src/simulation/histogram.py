import numpy
from matplotlib import pyplot


class Histogram(object):

    """
    Histogram can take values for statistics and plot a histogram from them.

    Values are added to the internal array. The class is able to generate a histogram and plot it using pyplot.
    This class is an abstract class and contains some methods, that need to be implemented in subclass.
    """

    # colors for plotting multiple plots in one figure
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    def __init__(self, server, typestr):
        """
        Constructor for a simple histogram
        :param sim: simulation, the histogram object belongs to
        :param typestr is mainly for the sake of distinguishing between multiple histograms but information can also
        be used for configuring the plot
        """
        self.server = server
        self.sim = server.slicesim
        self.values = []
        self.histogram = None
        self.bins = []
        self.bin_mids = []
        self.type = typestr

    def count(self, value):
        """
        Add a value to the histogram.
        Abstract method - implemented in subclass.
        """
        raise NotImplementedError("Please implement method")

    def reset(self):
        """
        Reset all values to their initial state.
        """
        self.values = []
        self.histogram = None
        self.bins = []
        self.bin_mids = []

    def report(self, filename=''):
        """
        Show the histogram to the viewer.
        Abstract method - implemented in subclass.
        """
        raise NotImplementedError

    def plot(self, filename='', diag_type="histogram", show_plot=False):
        """
        Plot function for histogram.
        :param diag_type: string can be "histogram" for a standard bar plot (default), "side-by-side" for a
        side by side histogram or "line" for a line plot
        :param show_plot: display plot after generating it. Can be set to False, if the figure contains multiple plots.
        """
        width = self.bins[1] - self.bins[0]
        self.bin_mids = [x+(width/2.) for x in self.bins[0:len(self.bins)-1]]
        fig = pyplot.figure()

        if diag_type == "line":
            """
            Plot line plot - mainly thought for mean waiting time
            """
            pyplot.plot(self.bin_mids, self.histogram, "+-", label='S=' + str(self.sim.slice_param.S))

        elif diag_type == "side-by-side":
            """
            Plot side-by-side histogram plot - mainly thought for mean queue length
            """
            num_of_plots = len(self.sim.slice_param.S_VALUES)
            total_width = .8
            width = total_width/float(num_of_plots)
            index = -1
            for i in range(len(self.sim.slice_param.S_VALUES)):
                if self.sim.slice_param.S_VALUES[i] == self.sim.slice_param.S:
                    index = i
                    break
            if index == -1:
                raise SystemError("ERROR GENERATING BAR PLOT")
            ind = self.bins[0:len(self.bins)-1] + .1 + index*width
            pyplot.bar(ind, self.histogram, width=width, label='S='+str(self.sim.slice_param.S), color=Histogram.colors[index])

        else:
            """
            Plot histogram - mainly thought for mean queue length
            (easier but worse interpretation than side-by-side)
            """
            weights = numpy.full(len(self.values), 1.0 / float(len(self.values)))
            pyplot.hist(self.values, self.bins, alpha=0.5, label='S='+str(self.sim.slice_param.S), rwidth=.7, weights=weights)

        pyplot.legend(loc='upper right')
        if show_plot:
            pyplot.show(fig)

        #filename = "plots/hist_user%d_slice%d.png" % (self.server.user.user_id, self.sim.slice_param.SLICE_ID)
        pyplot.savefig(filename)
        pyplot.close(fig)


class TimeIndependentHistogram(Histogram):

    """
    Histogram for plotting values independent of their duration.
    """

    def __init__(self, server, typestr):
        """
        Initialize histogram with the simulation it belongs to and a typestring for better distinction
        :param sim: simulation object, the histogram belongs to
        :param typestr: typestring for better distinction and selection of plot type
        q stands for queue length and will default to a side-by-side plot type
        bp stands for blocking probability and will default to a normal histogram plot type
        else, the plot type defaults to a line plot
        """
        super(TimeIndependentHistogram, self).__init__(server, typestr)

    def count(self, value):
        """
        Add new value to histogram, i.e., the internal array.
        """
        self.values.append(value)

    def report(self, filename=''):
        """
        Make report, i.e., calculate histogram and bins using numpy.

        Calculation depends on type (makes results easier to read.
        "q" stands a queue length histogram resulting in a limited number of bins (only few possible values)
        After generating the report, the plot function is called (see this function in super class).
        """
        if len(self.values) != 0:
            weights = numpy.full(len(self.values), 1.0 / float(len(self.values)))
            if self.type == "q":
                # for queue length a different resolution is chosen than for other values
                self.histogram, self.bins = numpy.histogram(self.values, weights=weights, bins=self.sim.slice_param.S_MAX + 1,
                                                            range=(-.5, self.sim.slice_param.S_MAX + .5))
                self.plot(diag_type="side-by-side")
            elif self.type == "bp":
                # for queue length a different resolution is chosen than for other values
                self.histogram, self.bins = numpy.histogram(self.values, weights=weights, bins=25,
                                                            range=(0, 1))
                self.plot(diag_type="histogram")
            elif self.type == "s":
                # for system time
                self.histogram, self.bins = numpy.histogram(self.values, weights=weights)
                self.plot(filename, diag_type="histogram")
            else:
                self.histogram, self.bins = numpy.histogram(self.values, weights=weights, bins=50, range=(0, 3500))
                #self.histogram, self.bins = numpy.histogram(self.values, weights=weights)
                self.plot(filename, diag_type="line" )

        else:
            raise ValueError("Can't plot histogram with no values.")


class TimeDependentHistogram(Histogram):

    """
    Histogram for plotting values considering their duration.
    """

    def __init__(self, server, typestr):
        """
        Initialize histogram with the simulation it belongs to and a typestring for better distinction
        :param sim: simulation object, the histogram belongs to
        :param typestr: typestring for better distinction
        """
        super(TimeDependentHistogram, self).__init__(server, typestr)
        self.first_timestamp = 0
        self.last_timestamp = 0
        self.weights = []

    def count(self, value):
        """
        Add new value to histogram, i.e., the internal array.
        Consider the duration of this value as well.
        """
        dt = self.sim.sim_state.now - self.last_timestamp
        self.values.append(value)
        self.weights.append(dt)
        self.last_timestamp = self.sim.sim_state.now

    def reset(self):
        self.first_timestamp = self.sim.sim_state.now
        self.last_timestamp = self.sim.sim_state.now
        self.weights = []
        Histogram.reset(self)

    def report(self, filename=''):
        """
        Make report, i.e., calculate histogram and bins using numpy.

        Plotting is not optimized, since not explicitly used in this assignment.
        After generating the report, the plot function is called (see this function in super class).
        """
        if len(self.values) != 0:
            self.histogram, self.bins = numpy.histogram(self.values, weights=self.weights, bins=50)
            self.plot(filename, diag_type="histogram")
        else:
            raise ValueError("Can't plot histogram with no values.")
