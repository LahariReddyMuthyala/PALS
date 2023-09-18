try:
	import Tkinter as tk
	from Tkinter import *
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog as tkFileDialog


import os, subprocess
import logging
from datetime import datetime
import argparse

from pages import WelcomePage
from pages import SettingsInput
from pages import DirectoryInputPage
from pages import DirectoryOutputPage
from pages import BrainExtractionInputPage
from pages import RegistrationInputPage
from pages import HeatmapInputPage
from pages import RunningOperationsPage
from pages import LesionCorrInputPage
from pages import LesionLoadCalculationInputPage
from pages.stores import Descriptions

LARGE_FONT = ("Verdana", 12)

class MainWindow(tk.Tk):
	def __init__(self, logger, project_dir, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title("Pipeline for Analyzing Lesions after Stroke")
		# self.geometry("1200x800")

		# Silent Mode Settings
		self.silent = False
		self.need_display = False

		self.logger = logger
		self.project_dir = project_dir

		# Tooltip descriptions
		self.desc = Descriptions()

		# Text area to show the logs of running operations
		self.display = None
		self.progressbar = None

		#Welcome page
		self.b_radiological_convention = BooleanVar(self)
		self.b_registration = BooleanVar(self)
		self.sv_brain_extraction_method = StringVar(self)
		self.sv_orientation_method = StringVar(self)
		self.sv_registration_method = StringVar(self)
		self.b_brain_extraction = BooleanVar(self)
		self.b_wm_segmentation = BooleanVar(self)
		self.b_wm_correction = BooleanVar(self)
		self.b_ll_calculation = BooleanVar(self)
		self.b_lesion_heatmap = BooleanVar(self)
		#self.b_visual_qc = BooleanVar(self)
		self.b_pause_for_qc = BooleanVar(self)

		self.b_radiological_convention.set(False)
		self.sv_orientation_method.set('LAS')
		self.b_registration.set(False)
		self.sv_registration_method.set('FLIRT')
		self.b_brain_extraction.set(False)
		self.sv_brain_extraction_method.set('BET')
		self.b_wm_segmentation.set(False)
		self.b_wm_correction.set(False)
		self.b_ll_calculation.set(False)
		self.b_lesion_heatmap.set(False)
		#self.b_visual_qc.set(False)
		self.b_pause_for_qc.set(True)

		#Directory Input Page
		self.sv_input_dir = StringVar(self)
		self.sv_roi_dir = StringVar(self)
		self.sv_t1_desc = StringVar(self)
		self.sv_t1_space = StringVar(self)
		self.sv_lesion_mask_suffix = StringVar(self)
		self.sv_lesion_mask_space = StringVar(self)
		self.sv_lesion_mask_label = StringVar(self)
		self.sv_subject = StringVar(self)
		self.sv_session = StringVar(self)
		self.sv_wm_seg_root = StringVar(self)
		self.sv_lesion_root = StringVar(self)
		self.sv_multiprocessing = StringVar(self)
		self.b_same_anatomical_space = BooleanVar(self)

		self.sv_t1_desc.set('')
		self.sv_t1_space.set('')
		self.sv_lesion_mask_suffix.set('')
		self.sv_lesion_mask_space.set('')
		self.sv_lesion_mask_label.set('')
		self.sv_subject.set('')
		self.sv_session.set('')
		self.sv_wm_seg_root.set('')
		self.sv_lesion_root.set('')
		self.sv_multiprocessing.set('1')
		self.b_same_anatomical_space.set(False)

		#Directory Output Page
		self.sv_output_dir = StringVar(self)
		self.sv_out_start_reg_space = StringVar(self)
		self.sv_output_reg_space = StringVar(self)
		self.sv_out_reg_transform = StringVar(self)
		self.sv_out_reorient = StringVar(self)
		self.sv_out_brain_registration = StringVar(self)
		self.sv_out_lesion_corr = StringVar(self)

		self.sv_output_reg_space.set('')
		self.sv_out_reg_transform.set('')
		self.sv_out_reorient.set('')
		self.sv_out_brain_registration.set('')
		self.sv_out_lesion_corr.set('')

		#Brain Extraction Page
		self.sv_brain_ext_frac = StringVar(self)
		self.b_brain_ext_mask = BooleanVar(self)

		self.sv_brain_ext_frac.set('0.5')
		self.b_brain_ext_mask.set(True)

		#Registration Page
		self.sv_reg_cost_func = StringVar(self)
		self.sv_reg_reference = StringVar(self)

		self.sv_reg_cost_func.set('normmi')
		self.sv_reg_reference.set('')

		#White Matter Correction Page
		self.sv_bet_id = StringVar(self)
		self.sv_wm_id = StringVar(self)
		self.sv_percent = StringVar(self)
		self.b_brain_extraction = BooleanVar(self)
		self.b_wm_segmentation_lc = BooleanVar(self)
		self.sv_bet_id.set('')
		self.sv_wm_id.set('')
		self.b_brain_extraction.set(False)
		self.b_wm_segmentation_lc.set(False)
		self.sv_percent.set('5.0')
		self.percent_intensity = 5.0
		self.sv_img_norm_min = StringVar(self)
		self.sv_img_norm_max = StringVar(self)
		self.sv_wm_spread = StringVar(self)

		self.sv_img_norm_min.set('0')
		self.sv_img_norm_max.set('255')
		self.sv_wm_spread.set('0.05')

		#Lesion Load Calculation Page
		self.b_default_rois = BooleanVar(self)
		self.b_freesurfer_rois = BooleanVar(self)
		self.b_own_rois = BooleanVar(self)
		self.b_default_rois.set(False)
		self.b_freesurfer_rois.set(False)
		self.b_own_rois.set(False)

		#Heatmap Input Page
		self.sv_heatmap_transparency = StringVar(self)
		self.sv_heatmap_reference = StringVar(self)

		self.sv_heatmap_transparency.set('0.4')
		self.default_roi_paths = None

		self.fs_roi_paths = None
		self.fs_roi_codes = None

		#User ROIs
		self.user_rois = []
		self.user_roi_paths = None
		self.sv_user_brain_template = StringVar(self)
		self.sv_user_brain_template.set('')
		self.user_agreed = BooleanVar(self)
		self.user_agreed.set(False)

		#Running Operations
		self.selected_subjects = StringVar(self)
		self.selected_subjects.set('')

		#Settings Page
		self.sv_fsl_binaries_msg = StringVar(self)
		self.sv_fsl_binaries_msg.set('')

		# this container contains all the pages
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		self.frames = {}
		self.parent_frames_stack = []

		frame_number = 0
		for PageType in self.getApplicationPages():
			frame = PageType(container, self, frame_number)
			self.frames[frame_number] = frame
			frame_number += 1
			frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)

		self.show_frame(0)

		self.bind_class("Text","<Control-a>", self.selectAll)
		self.bind_class("Text","<Command-v>", self.pasteAll)

	def updateMessage(self, text, log_level='DEBUG'):
		self.display.insert(END, text + '\n')
		self.display.see(END)
		if log_level == 'DEBUG':
			self.logger.debug(text)
		if log_level == 'ERROR':
			self.logger.error(text)
		self.update()

	def getProjectDirectory(self):
		return self.project_dir

	def updateProgressBar(self, value):
		self.progressbar['value'] = value

	def selectAll(self, event):
		event.widget.tag_add("sel","1.0","end")

	def pushFrameToStack(self, frame_number):
		self.parent_frames_stack.append(frame_number)

	def getParentFrame(self):
		try:
			return self.parent_frames_stack.pop()
		except:
			return 0

	def pasteAll(self, event):
		clipboard = self.clipboard_get()
		clipboard = clipboard.replace("\n", "\\n")
		try:
			start = event.widget.index("sel.first")
			end = event.widget.index("sel.last")
			event.widget.delete(start, end)
		except TclError as e:
			pass

		event.widget.insert("insert", clipboard)

	def setupLogger(self):
		project_path = os.path.dirname(os.path.realpath(__file__))
		logs_dir = os.path.join(project_path, 'logs')
		if not os.path.exists(logs_dir):
			os.makedirs(logs_dir)
		logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)s %(message)s',
					filename=os.path.join(logs_dir, datetime.now().strftime('logfile_%Y%m%d_%H_%M.log')),
					filemode='w')
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)
		self.logger = logging.getLogger(__name__)

	def show_frame(self, frame_number):
		if frame_number >= len(self.frames) or frame_number < 0:
			return
		frame = self.frames[frame_number]
		frame.tkraise()
		frame.update()
		frame.event_generate("<<ShowFrame>>")

	def getApplicationPages(self):
		pages = [WelcomePage, DirectoryInputPage, DirectoryOutputPage, BrainExtractionInputPage, RegistrationInputPage, LesionCorrInputPage, HeatmapInputPage, RunningOperationsPage]
		if not self.checkFslInstalled():
			pages = [SettingsInput]
		return pages

	def checkFslInstalled(self, bypass_mri_convert=True):
		commands = ['fslmaths', 'fsleyes', 'flirt', 'fslstats', 'fast', 'bet', 'fslswapdim', 'fslreorient2std', 'fslorient', 'gzip']
		if not bypass_mri_convert:
			commands += ['mri_convert']
		flag = True
		msg = ''
		FNULL = open(os.devnull, 'w')
		for cmd in commands:
			cmd_to_exe = 'which ' + cmd
			try:
				exit_code = subprocess.call([cmd_to_exe], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
				if exit_code != 0:
					raise
			except Exception as e:
				flag = False
				msg += cmd + '\n'
		msg = 'The following binaries location are not set in the path:\n' + msg if len(msg) != 0 else ''
		self.sv_fsl_binaries_msg.set(msg)
		return flag

if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()