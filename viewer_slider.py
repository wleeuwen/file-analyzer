
from numpy import exp, linspace, meshgrid

from chaco.api import ArrayPlotData, Plot, jet
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance, Enum, Range
from traitsui.api import Item, View
import numpy as np
import time

FEI_MRC_HDR_SIZE = 1024
FEI_MRC_EXT_HDR_SIZE = 128
IMAGE_PIXEL_DEPTH = 2

fei_mrc_hdr_dt = np.dtype([('nx', np.uint32), # image x dimension
                           ('ny', np.uint32), # image y dimension
						   ('nz', np.uint32), # nrof images
						   ('mode', np.uint32),
						   ('nxstart', np.uint32),
						   ('nystart', np.uint32),
						   ('nzstart', np.uint32),
						   ('mx', np.uint32),
						   ('my', np.uint32),
						   ('mz', np.uint32),
						   ('xlen', np.float32),
						   ('ylen', np.float32),
						   ('zlen', np.float32),
						   ('alpha', np.float32),
						   ('beta', np.float32),
						   ('gamma', np.float32),
						   ('mapc', np.uint32),
						   ('mapr', np.uint32),
						   ('maps', np.uint32),
						   ('amin', np.float32),
						   ('amax', np.float32),
						   ('amean', np.float32),
						   ('ispg', np.uint16),
						   ('nsymbt', np.uint16),
						   ('next', np.uint32), # offset from eof header to start of images
						   ('dvid', np.uint16),
						   ('extra', 'S30'),
						   ('numintegers', np.uint16),
						   ('numfloat', np.uint16),
						   ('sub', np.uint16),
						   ('zfac', np.uint16),
						   ('min2', np.float32),
						   ('max2', np.float32),
						   ('min3', np.float32),
						   ('max3', np.float32),
						   ('min4', np.float32),
						   ('max4', np.float32),
						   ('idtype', np.uint16),
						   ('lens', np.uint16),
						   ('nd1', np.uint16),
						   ('nd2', np.uint16),
						   ('vd1', np.uint16),
						   ('vd2', np.uint16),
						   ('tiltangles', 'S36'),
						   ('zorg', np.float32),
						   ('xorg', np.float32),
						   ('yorg', np.float32),
						   ('nlabl', np.uint32),
						   ('labl', 'S800')])
						   
fei_mrc_ext_hdr_dt  = np.dtype([('a_tilt', np.float32),
                                ('b_tilt', np.float32),
								('x_stage', np.float32),
								('y_stage', np.float32),
								('z_stage', np.float32),
								('x_shift', np.float32),
								('y_shift', np.float32),
								('defocus', np.float32),
								('exp_time', np.float32),
								('mean_int', np.float32),
								('tilt_axis', np.float32),
								('pixel_size', np.float32),
								('magnification', np.float32),
								('ht', np.float32),
								('binning', np.float32),
								('appliedDefocus', np.float32),
								('remainder', 'S64')])


class ImagePlot(HasTraits):

	plot = Instance(Plot)

	data_name = Range(0,1024,0,mode='slider')

	traits_view = View(Item('data_name', label="imagedata"),
						Item('plot', editor=ComponentEditor(),
                            show_label=False),
                       width=500, height=500,
                       resizable=True,
                       title="Chaco Plot")

	def __init__(self):
		mrc = np.memmap('C:\\Tomo\\tomo.mrc', dtype=np.uint8,mode='r', offset=0)

		hdr = mrc[0:FEI_MRC_HDR_SIZE]
		hdr.dtype = fei_mrc_hdr_dt

		offset = FEI_MRC_HDR_SIZE # offset to extended header
		ext_hdr = mrc[offset:offset + FEI_MRC_EXT_HDR_SIZE * hdr[0]['nz']]
		ext_hdr.dtype = fei_mrc_ext_hdr_dt

		offset = FEI_MRC_HDR_SIZE + hdr[0]['next'] # offset to first image
		image_size = hdr[0]['nx'] * hdr[0]['ny'] * IMAGE_PIXEL_DEPTH
		self.image = mrc[offset:offset + image_size * hdr[0]['nz']]
		self.image.dtype = np.uint16
		self.image.shape = (hdr[0]['nz'], hdr[0]['ny'], hdr[0]['nx'])

		self.data = {"0": 0,
					 "1": 1,
					 "2": 2}

		self.plotdata = ArrayPlotData(imagedata=1.0*self.image[self.data["0"],::4,::4]/self.image.max())
		plot = Plot(self.plotdata)
		plot.img_plot("imagedata", colormap=jet)
		self.plot = plot

	def _data_name_changed(self):
		self.plotdata.set_data("imagedata", 1.0*self.image[int(self.data_name),::4,::4]/self.image.max())


demo = ImagePlot()
if __name__ == "__main__":
    demo.configure_traits()
