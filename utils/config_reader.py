import json
from os import listdir
from os.path import isfile, join

def readConfig(filename):
	with open(filename) as json_data_file:
		data = json.load(json_data_file)
	return data

def readReOrientConfigs(configs, application):
	pass

def readLesionCorrectionConfigs(configs, application):
	try:
		module_settings = configs['module_settings']['Lesion_correction']
		application.b_brain_extraction.set(module_settings['bet_performed'])
		application.sv_bet_id.set(module_settings['bet_identifier'])

		module_settings = configs['module_settings']['Lesion_correction']
		application.b_wm_segmentation.set(module_settings['wms_performed'])
		application.sv_wm_id.set(module_settings['wms_identifier'])

		application.sv_percent.set(str(module_settings["t1_intensity_percent"]))
		application.percent_intensity = module_settings["t1_intensity_percent"]

	except Exception as e:
		application.updateMessage('Failed to load lesion load configs : ' + str(e), 'ERROR')

def readLesionLoadCalculationConfigs(configs, application):
	try:
		module_settings = configs['module_settings']['Lesion_load_calculation']
		application.b_brain_extraction.set(module_settings['bet_performed'])
		application.sv_bet_id.set(module_settings['bet_identifier'])

		for roi in module_settings['roi_names']['default']['corticospinal_tracts']:
			application.b_default_rois.set(True)
			roi_obj = application.buildRoi(roi)
			application.default_corticospinal_tract_roi.append(roi_obj)

		for roi in module_settings['roi_names']['default']['fs_cortical']:
			application.b_default_rois.set(True)
			roi_obj = application.buildRoi(roi)
			application.default_freesurfer_cortical_roi.append(roi_obj)

		for roi in module_settings['roi_names']['default']['fs_sub_cortical']:
			application.b_default_rois.set(True)
			roi_obj = application.buildRoi(roi)
			application.default_freesurfer_subcortical_roi.append(roi_obj)

		for roi in module_settings['roi_names']['free_surfer']['fs_cortical']:
			application.b_freesurfer_rois.set(True)
			roi_obj = application.buildRoi(roi)
			application.freesurfer_cortical_roi.append(roi_obj)

		for roi in module_settings['roi_names']['free_surfer']['fs_sub_cortical']:
			application.b_freesurfer_rois.set(True)
			roi_obj = application.buildRoi(roi)
			application.freesurfer_subcortical_roi.append(roi_obj)

		if module_settings['roi_names']['own']['own_rois']:
			application.b_own_rois.set(True)
			brain_template_file = module_settings['roi_names']['own']["template_brain"]
			application.sv_user_brain_template = application.buildRoi(brain_template_file)
			user_rois= getOwnROIsList(application)
			if brain_template_file in user_rois:
				user_rois.remove(brain_template_file)
			for roi in user_rois:
				roi_obj = application.buildRoi(roi)
				application.user_rois.append(roi_obj)

	except Exception as e:
		application.updateMessage('Failed to load lesion load configs : ' + str(e), 'ERROR')
		
def getOwnROIsList(application):
	own_roi_path = '/own_rois'
	message = ''
	try:
		roi_files = [f for f in listdir(own_roi_path) if isfile(join(own_roi_path, f) and f.endswith('gz'))]
	except Exception as ex:
		roi_files = []
		message = 'Error : ' + str(ex)

	if len(roi_files) == 0:
		application.updateMessage("Unable to find any user's custom ROI file in the specified directory." + message if message != '' else '')
	return roi_files

def readApplicationConfigs(application, config_file):
	configs = readConfig(config_file)
	if 'modules' in configs:
		modules = configs['modules']
		if 'Re_orient_radiological' in modules and modules['Re_orient_radiological']:
			application.b_radiological_convention.set(True)
			readReOrientConfigs(configs, application)

		if 'Lesion_correction' in modules and modules['Lesion_correction']:
			application.b_wm_correction.set(True)
			readLesionCorrectionConfigs(configs, application)

		if 'Lesion_load_calculation' in modules and modules['Lesion_load_calculation']:
			application.b_ll_calculation.set(True)
			readLesionLoadCalculationConfigs(configs, application)
	else:
		application.updateMessage('Module selection is missing', 'ERROR')

	if 'common_settings' in configs:
		common_configs = configs['common_settings']
		if 'input_dir' in common_configs:
			application.sv_input_dir.set(common_configs['input_dir'])
		else:
			application.updateMessage('Input Directory is missing in configs', 'ERROR')

		if 'output_dir' in common_configs:
			application.sv_output_dir.set(common_configs['output_dir'])
		else:
			application.updateMessage('Output Directory is missing in configs', 'ERROR')

		if 't1_id' in common_configs:
			application.sv_t1_id.set(common_configs['t1_id'])
		else:
			application.updateMessage('T1 Anatomical Identifier is missing in configs', 'ERROR')

		if 'lesion_mask_id' in common_configs:
			application.sv_lesion_mask_id.set(common_configs['lesion_mask_id'])
		else:
			application.updateMessage('Lesion Mask Identifier is missing in configs', 'ERROR')

		if 'same_anatomical_space' in common_configs:
			application.b_same_anatomical_space.set(common_configs['same_anatomical_space'])
		else:
			application.updateMessage('Same Anatomical Space flag is missing in configs', 'ERROR')
	else:
		application.updateMessage('Common configs missing', 'ERROR')


	application.b_visual_qc.set(False)
	application.b_pause_for_qc.set(False)


def setApplicationVariables(controller, configs):
	if 'modules' in configs:
		modules = configs['modules']
		if 'Re_orient_radiological' in modules and modules['Re_orient_radiological']:
			application.b_radiological_convention.set(True)
		if 'Lession_correction' in modules and modules['Lession_correction']:
			controller.b_wm_correction.set(True)
		if 'Lesion_load_calculation' in modules and modules['Lesion_load_calculation']:
			controller.b_ll_calculation.set(True)
	else:
		print('Module selection is missing')

	# Set common parameters
	if 'common_settings' in configs:
		common_configs = configs['common_settings']
		if 'input_dir' in common_configs:
			controller.sv_input_dir.set(common_configs['input_dir'])
		else:
			print('Input Directory is missing in configs')

		if 'output_dir' in common_configs:
			controller.sv_output_dir.set(common_configs['output_dir'])
		else:
			print('Output Directory is missing in configs')

		if 't1_id' in common_configs:
			controller.sv_t1_id.set(common_configs['t1_id'])
		else:
			print('T1 Anatomical Identifier is missing in configs')

		if 'lesion_mask_id' in common_configs:
			controller.sv_lesion_mask_id.set(common_configs['lesion_mask_id'])
		else:
			print('Lesion Mask Identifier is missing in configs')

		if 'same_anatomical_space' in common_configs:
			controller.b_same_anatomical_space.set(common_configs['same_anatomical_space'])
		else:
			print('Same Anatomical Space flag is missing in configs')
	else:
		print('Common configs missing')

	controller.b_visual_qc.set(False)
	controller.b_pause_for_qc.set(False)