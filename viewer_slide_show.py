
from chaco.api import ArrayPlotData, Plot, gray
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View
from threading import Thread
from time import sleep
from file.mrc import *

MRC_FILE = 'tomo.mrc'

class ImagePlot(HasTraits):

	plot = Instance(Plot)

	traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       width=500, height=500,
                       resizable=True,
                       title="TOMO Images")

	def __init__(self):
		self.mrc = Mrc(MRC_FILE)
		self.image_size = 256
		self.image_index = 0
		self.nrof_images = self.mrc.number_of_images
		self.plotdata = ArrayPlotData(imagedata = self.mrc.get_scaled_image(self.image_index, self. image_size)/256)
		plot = Plot(self.plotdata)
		plot.img_plot("imagedata",colormap=gray)
		self.plot = plot

	def plot_next(self):
		if self.image_index < self.mrc.number_of_images:
			print 'image: %d' % self.image_index
			self.plotdata.set_data("imagedata", self.mrc.get_scaled_image(self.image_index, self.image_size)/256)
			self.image_index += 1
			sleep(0.2) # Some time needed to plot the image. How to know when ready?
			return True
		else:
			return False

        
class MyThread(Thread):
	def run(self):
		while tomo.plot_next() == True:
			pass

tomo = ImagePlot()
thread = MyThread()

if __name__ == "__main__":
	tomo.configure_traits()
	thread.start()
