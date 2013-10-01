from wx.lib.pubsub import Publisher as pub
from SPE_module import SPE_File
import os.path
import numpy as np
import random
import scipy.interpolate as ip
from scipy.optimize import curve_fit

from T_Rax_Data import ROI, Spectrum, black_body_function, gauss_curve_function


class TraxRubyData(object):
    def __init__(self):
        self.roi_data_manager =  ROIRubyManager()
        self._create_dummy_img()
        self.click_pos=694.15
        self.ruby_reference_pos=694.15

    def _create_dummy_img(self):
        self.exp_data=DummyImg(self.roi_data_manager)
        self.roi = self.exp_data.roi

    def load_ruby_data(self, filename):
        self.exp_data = self.read_exp_image_file(filename)
        self.roi = self.exp_data.roi
        pub.sendMessage("EXP RUBY DATA CHANGED", self)

    def load_next_ruby_file(self):
        new_file_name, new_file_name_with_leading_zeros = self.exp_data.get_next_file_names()
        if os.path.isfile(new_file_name):
            self.load_ruby_data(new_file_name)
        elif os.path.isfile(new_file_name_with_leading_zeros):
            self.load_ruby_data(new_file_name_with_leading_zeros)

    def load_previous_ruby_file(self):
        new_file_name, new_file_name_with_leading_zeros = self.exp_data.get_previous_file_names()
        if os.path.isfile(new_file_name):
            self.load_ruby_data(new_file_name)
        elif os.path.isfile(new_file_name_with_leading_zeros):
            self.load_ruby_data(new_file_name_with_leading_zeros)
        pub.sendMessage("EXP RUBY DATA CHANGED", self)

    def read_exp_image_file(self, file_name):
        img_file= SPE_File(file_name)
        return ExpRubyData(img_file, self.roi_data_manager)

    def calculate_wavelength(self,channel):
        if isinstance(channel,list):
            result = []
            for c in channel:
                result.append(self.exp_data.x_whole[c])
            return np.array(result)
        else:
            return self.exp_data.x_whole[channel]

    def calculate_ind(self, wavelength):
        result = []
        xdata = np.array( self.exp_data.x_whole)
        try:
            for w in wavelength:
                try:
                    base_ind = max(max(np.where(xdata <= w)))
                    if base_ind < len(xdata)-1:
                        result.append(int(np.round((w - xdata[base_ind]) / \
                            (xdata[base_ind + 1] - xdata[base_ind]) \
                            + base_ind)))
                    else:
                        result.append(base_ind)
                except:
                    result.append(0)
            return np.array(result)
        except TypeError:
            base_ind = max(max(np.where(xdata <= wavelength)))
            return int(np.round((wavelength - xdata[base_ind]) / \
                    (xdata[base_ind + 1] - xdata[base_ind]) \
                    + base_ind))
    
    def calc_spectra(self):
        self.exp_data.calc_spectra()

    def get_exp_file_name(self):
        return self.exp_data.filename

    def get_exp_img_data(self):
        return self.exp_data.get_img_data()

    def get_exp_graph_data(self):
        return self.exp_data.get_ds_spectrum()
             
    def get_spectrum(self):
        return self.exp_data.get_spectrum()

    def get_roi_max(self):
        return self.exp_data.calc_roi_max(self.exp_data.roi.roi)

    def get_us_spectrum(self):
        if self.us_calib_data == None:
            return self.exp_data.us_spectrum
        else:
            x=self.exp_data.us_spectrum.x
            corrected_spectrum = self.exp_data.calc_corrected_us_spectrum(self.us_calib_data.us_spectrum, 
                                                self.us_calib_param.get_calibrated_spec(x))
            self.us_fitted_spectrum = FitSpectrum(corrected_spectrum)
            return [corrected_spectrum, self.us_fitted_spectrum]

    def get_roi_max(self):
        return self.exp_data.calc_roi_max(self.exp_data.roi.us_roi)

    def get_whole_spectrum(self):
        return self.exp_data.x, self.exp_data.y_whole_spectrum

    def save_roi_data(self):
        np.savetxt('roi_data.txt', self.roi.get_roi_data(), delimiter=',', fmt='%.0f')     
        
    def get_x_limits(self):
        return self.exp_data.get_x_limits()

    def get_x_roi_limits(self):
        return self.calculate_wavelength(self.exp_data.roi.get_x_limits())

    def set_x_roi_limits_to(self, limits):
        limits_ind=self.calculate_ind(limits)
        self.roi.set_x_limit(limits_ind)
#********************RUBY STUFF HERE***********************
#
    
    def set_click_pos(self, pos):
        self.click_pos = pos
        pub.sendMessage("RUBY POS CHANGED", self)

    def set_ruby_reference_pos(self, pos):
        self.ruby_reference_pos=pos

    def get_pressure(self):
        A=19.04
        B=7.665
        delta_pos=self.click_pos-self.ruby_reference_pos
        P_in_Mbar=A/B*((1+delta_pos/self.ruby_reference_pos)**B-1)
        return P_in_Mbar*100




class ExpRubyData(object):
    def __init__(self, img_file, roi_data_manager):
        self._img_file= img_file
        self.roi=roi_data_manager.get_roi_data(img_file.get_dimension())
        self.read_parameter()        
        self._get_file_number()
        self._get_file_base_str()
    
    def read_parameter(self):
        self.filename = self._img_file.filename
        self.img_data = self._img_file.img
        self.x_whole = self._img_file.x_calibration

    def get_img_data(self):
        return self.img_data

    def get_roi_img(self):
        return self.img_data[self.roi.y_min : self.roi.y_max+1, 
                             self.roi.x_min : self.roi.x_max+1]

    def get_spectrum(self):
        roi_img = self.get_roi_img()
        x=self.x_whole[self.roi.x_min:self.roi.x_max+1]
        y=np.sum(roi_img,0)/np.float(np.size(roi_img,0))

        return Spectrum(x, np.sum(roi_img,0)/np.float(np.size(roi_img,0)))

    def _get_file_number(self):
        file_str = ''.join(self.filename.split('.')[0:-1])
        num_str = file_str.split('_')[-1]
        try:
            self._file_number = int(num_str)
            self._num_char_amount = len(num_str) #if number has leading zeros
        except ValueError:
            self._file_number = 0
            self._num_char_amount = 1

    def _get_file_base_str(self):
        file_str = ''.join(self.filename.split('.')[0:-1])
        self._file_base_str = '_'.join(file_str.split('_')[0:-1])
        self._file_ending = self.filename.split('.')[-1]

    def get_next_file_names(self):
        new_file_name = self._file_base_str + '_' + str(self._file_number + 1) + \
                        '.' + self._file_ending
        format_str='0'+str(self._num_char_amount)+'d'
        number_str=("{0:"+format_str+'}').format(self._file_number + 1)
        new_file_name_with_leading_zeros = self._file_base_str + '_' + \
                    number_str + '.' + self._file_ending
        return new_file_name, new_file_name_with_leading_zeros

    def get_previous_file_names(self):
        new_file_name = self._file_base_str + '_' + str(self._file_number - 1) + \
                        '.' + self._file_ending
        format_str='0'+str(self._num_char_amount)+'d'
        number_str=("{0:"+format_str+'}').format(self._file_number - 1)
        new_file_name_with_leading_zeros = self._file_base_str + '_' + \
                    number_str + '.' + self._file_ending
        return new_file_name, new_file_name_with_leading_zeros

    def get_x_limits(self):
        return np.array([min(self.x_whole), max(self.x_whole)])


class DummyImg(ExpRubyData):
    def __init__(self, roi_data_manager):
        self.roi=roi_data_manager.get_roi_data([1300,100])
        self.create_img()
        self.filename = 'dummy_img.spe'

    def create_img(self):
        x=np.linspace(645,750,1300)
        y=np.linspace(0,101, 100)
        X,Y = np.meshgrid(x,y)

        Z=np.ones((len(y),len(x)))
        random.seed()
        T1=random.randrange(1700,3000,1)
        T2=T1+ random.randrange(-200,200,1)

        lorenz1 = lorentz_curve(x,4,1,700)+lorentz_curve(x,3,1,695)
        gauss1 = gauss_curve_function(y,2,80,3)
        lorenz2 = lorentz_curve(x,4,1,700)+lorentz_curve(x,3,1,695)
        gauss2 = gauss_curve_function(y,2,15,3)

        for x_ind in xrange(len(x)):
            for y_ind in xrange(len(y)):
                Z[y_ind,x_ind] = lorenz1[x_ind]*gauss1[y_ind] +lorenz2[x_ind]*gauss2[y_ind]
        self.img_data=Z+np.random.normal(0,.01*max(lorenz1),(len(y),len(x)))
        self.x_whole = x



class ROIRubyManager():
    def __init__(self):
        self._img_dimensions_list = []
        self._roi_data_list = []
        self._num=0
        self._current=None

    def _exists(self, dimension):
        if self._get_dimension_ind(dimension) is not None:
            return True
        else:
            return False

    def _add(self, img_dimension, roi):
        self._img_dimensions_list.append(img_dimension)
        self._roi_data_list.append(roi)
        self._num+=1

    def _get_dimension_ind(self,img_dimension):
        for ind in range(self._num):
            if self._img_dimensions_list[ind]==img_dimension:
                self._current = ind
                return ind
        self._current=None
        return None

    def get_roi_data(self, img_dimension):
        if self._exists(img_dimension):
            return self._roi_data_list[self._get_dimension_ind(img_dimension)]
        else:
            limits = np.array([0.1*(img_dimension[0]-1), 0.9*(img_dimension[0]-1),
                               0.1*(img_dimension[1]-1), 0.2*(img_dimension[1]-1)])
            limits = np.round(limits)

            self._add(img_dimension, ROI(limits))
            return self._roi_data_list[self._get_dimension_ind(img_dimension)]

    def get_current_roi(self):
        return self._roi_data_list[self._current]


def lorentz_curve(x, int, fwhm, center):
    return int/np.pi * (fwhm/((x-center)**2+fwhm**2))