import numpy as np

FEI_MRC_HEADER_SIZE = 1024
FEI_MRC_EXTENDED_HEADER_SIZE = 128
IMAGE_PIXEL_DEPTH = 2

fei_mrc_header_dt = np.dtype(
    [('nx', np.uint32), # image x dimension
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
						   
fei_mrc_extended_header_dt  = np.dtype(
    [('a_tilt', np.float32),
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

class Mrc(object):
    def __init__(self, file):
        self.mrc = None
        self.header = None
        self.extended_header = None
        self.image = None
        self._open_file_(file)
        self._init_header_map_()
        self._init_extended_header_map_()
        self._init_image_map_()

    def _open_file_(self, file):
        # CHECK IF FILE EXISTS!!!
        self.mrc = np.memmap(file, dtype=np.uint8,mode='r', offset=0)
        
    def _init_header_map_(self):
        self.header = self.mrc[0:FEI_MRC_HEADER_SIZE]
        self.header.dtype = fei_mrc_header_dt
        self.header.squeeze() # remove empty array dimension
        
    def _init_extended_header_map_(self):
        self.extended_header = self.mrc[FEI_MRC_HEADER_SIZE:FEI_MRC_HEADER_SIZE + FEI_MRC_EXTENDED_HEADER_SIZE * self.header['nz']]
        self.extended_header.dtype = fei_mrc_extended_header_dt

    def _init_image_map_(self):
        image_start = FEI_MRC_HEADER_SIZE + self.header['next'] # offset to first image
        image_byte_size = self.header['nx'] * self.header['ny'] * IMAGE_PIXEL_DEPTH
        self.image = self.mrc[image_start:image_start + image_byte_size * self.header['nz']]
        self.image.dtype = np.uint16
        self.image.shape = (self.header['nz'], self.header['ny'], self.header['nx'])

    @property
    def number_of_images(self):
        return (self.header['nz'])
    
    @property
    def image_dimensions(self):
        return (self.header['nx'], self.header['ny'])
        
    @property
    def image_pixel_depth(self):
        return(IMAGE_PIXEL_DEPTH)
    
    def get_image(self, image_index):
        return self.image[image_index]
        
    def get_scaled_image(self, image_index, max_image_size): # max_image_size = 256, 512, 1024, ..
        scale_factor = self.header['nx'] / int(max_image_size)
        if scale_factor < 2:
            return self.image[image_index]
        else: 
            return self.image[image_index,::scale_factor,::scale_factor]
            
    def get_image_property(self, image_index, property):
        return self.extended_header[image_index][property]
        
    def get_property_of_all_images(self, property):
        return self.extended_header[::][property]
