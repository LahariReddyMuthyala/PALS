import os
import subprocess

class Commands(object):
	def __init__(self, logger, parent):
		self.logger = logger
		self.parent = parent
		self.display = parent.display

	def startExecution(self, cmd, show_error=True):
		self.running = True
		msg = "Running [%s]"%cmd
		self.logger.debug(msg)
		self.running_process = subprocess.Popen('exec ' + cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
		return_code = self.running_process.wait()
		output = ''
		for stdout_line in iter(self.running_process.stdout.readline, ""):
			if not self.running:
				break
			output += stdout_line
		self.running_process.stdout.close()
		if return_code != 0 and show_error:
			output = 'Something went wrong.'
			self.parent.updateGUI(output, log_level='ERROR')
		if len(output.strip()) > 0:
			self.logger.debug(output)
		return output, return_code

	def stopCurrentProcess(self):
		self.running = False
		try:
			self.running_process.kill()
		except:
			pass

	def runGzip(self, input_directory):
		input_directory = os.path.join(input_directory, '*.nii')
		cmd = "gzip %s"%(input_directory)
		output, ret_code = self.startExecution(cmd, show_error=False)
		if ret_code != 0:
			self.logger.error('File was not zipped.')


	def runFslMath(self, arg1, minimum, scalling, arg2):
		cmd_1 = 'fslmaths %s -sub %f -mul %f %s_scaled;'%(arg1, minimum, scalling, arg2)
		cmd_2 = 'fslmaths %s_scaled %s_intNorm.nii.gz -odt char;'%(arg2, arg2)

		output, ret_code = self.startExecution(cmd_1)
		output, ret_code = self.startExecution(cmd_2)

	def runFslBinarize(self, lesion_file_path, output_bin_path):
		cmd = 'fslmaths %s -bin %s;'%(lesion_file_path, output_bin_path)
		output, ret_code = self.startExecution(cmd)

	def runFslOrient(self, original_t1_files, args=''):
		cmd = 'fslorient %s %s'%(args, original_t1_files)
		output, ret_code = self.startExecution(cmd)
		return output.strip()

	def runFslOrient2Std(self, rad_ti_file, output_file):
		cmd = 'fslreorient2std %s %s;'%(rad_ti_file, output_file)
		self.startExecution(cmd)

	def runFslSwapDim(self, original_t1_files, output_bin_path):
		# fslswapdim $origT1 -x y z ${SUBJECTOPDIR}/Intermediate_Files/"${SUBJ}"_"${ANATOMICAL_ID}"_rad;
		cmd = 'fslswapdim %s -x y z %s;'%(original_t1_files, output_bin_path)
		output, ret_code = self.startExecution(cmd)

	# def runBet(self, anatomical_file_path, output_file):
	# 	# bet "${ANATOMICAL}" "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_Brain -R -f 0.5 -g 0;
	# 	cmd = 'bet %s %s -R -f 0.5 -g 0;'%(anatomical_file_path, output_file)
	# 	self.startExecution(cmd)

	def runFslEyes(self, anatomical_file_path, bet_brain_file='', output_image_path='', options='-cm blue -a 50'):
		# fsleyes render --hideCursor -of "$WORKINGDIR"/QC_BrainExtractions/"${SUBJ}"_BET.png "$ANATOMICAL" "$BET_Brain" -cm blue -a 50;
		cmd = 'fsleyes render --hideCursor -of %s %s %s %s;'%(output_image_path, anatomical_file_path, bet_brain_file, options)
		self.startExecution(cmd)

	def runFslEyes2(self, anatomical_file_path, lesion_file, wm_adjusted_lesion, x, y, z, output_image_path):
		# fsleyes render -vl $COG --hideCursor -of "$WORKINGDIR"/QC_Lesions/"${SUBJ}"_Lesion"${counter}".png "$ANATOMICAL" $Lesion -a 40 "$SUBJECTOPDIR"/"${SUBJ}"_WMAdjusted_Lesion"${counter}"_bin -cm blue -a 50;
		cmd = 'fsleyes render -vl %d %d %d --hideCursor -of %s %s %s -a 40 %s -cm blue -a 50;'%(x, y, z, output_image_path, anatomical_file_path, lesion_file, wm_adjusted_lesion)
		self.startExecution(cmd)

	def runFast(self, subject_dir, brain_file):
		# fast -t 1 -n 3 -H 0.1 -I 4 -l 20.0 -g --nopve -o "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}" "${BET_Brain}";
		cmd = 'fast -t 1 -n 3 -H 0.1 -I 4 -l 20.0 -g --nopve -o %s %s;'%(subject_dir, brain_file)
		self.startExecution(cmd)

	def runFslMathToCheckInSameSpace(self, wm_mask_file, lesion_file, output_file):
		# fslmaths "${WM_MASK}" -sub ${LesionFiles[0]} "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_corrWM
		return self.runFslWithArgs(wm_mask_file, lesion_file, output_file, '-sub') == ''

	def runFslMultiply(self, anatomical_file_path, corrected_wm_file, output_file):
		# fslmaths $ANATOMICAL -mul "${corrWM}" "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_NormRangeWM;
		self.runFslWithArgs(anatomical_file_path, corrected_wm_file, output_file, '-mul')

	def runFslWithArgs(self, arg_1, arg_2, arg_3, option):
		# fslmaths arg_1 option arg_2 arg_3;
		cmd = 'fslmaths %s %s %s %s;'%(arg_1, option, arg_2, arg_3)
		output, ret_code = self.startExecution(cmd)
		return output

	def runFslStats(self, input_file, options):
		# WM_Mean=$(fslstats "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_NormRangeWM -options);
		cmd = 'fslstats %s %s'%(input_file, options)
		output, ret_code = self.startExecution(cmd)
		if options == '-C':
			output = ' '.join(map(str, map(int, map(round, map(float, output.strip().split())))))
		if options == '-R':
			output = map(float, output.strip().split())
		if options == '-c':
			output = 'L' if output.startswith('-') else 'R'
		if options == '-M':
			output = float(output.strip())
		return output

	def runBrainVolume(self, bet_brain_file):
		# fslstats "${BET_Brain}" -V | awk '{print $2;}'
		cmd = 'fslstats %s -V'%(bet_brain_file)
		output, ret_code = self.startExecution(cmd)
		return float(output.strip().split()[1])

	def runAppendToCSV(self, data, csv_location):
		text = ''
		for row in data:
			text += ','.join(map(str, row)) + '\n'
		cmd = 'echo "%s" >> %s'%(text, csv_location)
		self.startExecution(cmd)

	def runFlirt(self, bet_brain_file, brain_file, reg_brain_file, reg_file):
		# flirt -in "$BET_Brain" -ref $1 -out $RegBrain -omat $RegFile -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear;
		cmd = 'flirt -in %s -ref %s -out %s -omat %s -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear;'%(bet_brain_file, brain_file, reg_brain_file, reg_file)
		self.startExecution(cmd)

	def runMriConvert(self, t1_mgz, fs_t1):
		cmd = 'mri_convert --in_type mgz --out_type nii --out_orientation RAS %s %s >/dev/null;'%(t1_mgz, fs_t1)
		self.startExecution(cmd)

	def runRawCommand(self, cmd, show_error=True):
		output, ret_code = self.startExecution(cmd, show_error)
		return output

if __name__ == '__main__':
	com = Commands()
	com.runFslMath("/Users/amit/WorkPro/Lily/data/OUTPUTS_FS/subjC/Intermediate_Files/Original_Files/subjC*T1*.nii.gz",0,0.2849162011173184,"/Users/amit/WorkPro/Lily/data/OUTPUTS_FS/subjC/Intermediate_Files/subjC_T1")
