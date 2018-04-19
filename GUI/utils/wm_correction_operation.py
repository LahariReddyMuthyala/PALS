import os
from qc_page import generateQCPage
from base_operation import BaseOperation

class WMCorrectionOperation(BaseOperation):
	def runWMCorrection(self):
		# Skip this step if user has not selected to perform wm correction
		if self.controller.b_wm_correction.get() == False or self.skip: return False

		for subject in self.subjects:
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			if not self.com.runFslMathToCheckInSameSpace(wm_mask_file, lesion_file[0], os.path.join(self.getIntermediatePath(subject), subject + '_corrWM')):
				self.logger.info('Check Image Orientations for T1 and Lesion Mask. Skipping Subject: %s'%subject)
				# Need to add equivivalent code
				# printf "${SUBJ} Skipped\n" >> "$WORKINGDIR"/lesion_data.csv;
				continue

			# assign the new wm seg file (with lesion removed) to corrWM
			corrected_wm_file = os.path.join(self.getIntermediatePath(subject), subject + '_corrWM.nii.gz')
			output_file = os.path.join(self.getIntermediatePath(subject), subject + '_NormRangeWM')
			# set values for healthy WM removal
			# multiply WM mask by intensity normalized T1
			self.com.runFslMultiply(anatomical_file_path, corrected_wm_file, output_file)
			self.com.runFslMean(output_file)



	for SUBJ in $SUBJECTS; do

		cd $INPUTDIR/$SUBJ || exit;

		# this assigns subject specific file paths for dependent files (e.g., BET)
		subj_set_path $SUBJ;

		# this step removes the lesion mask from the white matter segmentation so we don't calculate values from the lesion mask in getting the wm seg mean.
		# fslmaths checks that the lesion mask and the wm seg are in the same space. If not, the subject is skipped, and noted in CSV file.
		if $(fslmaths "${WM_MASK}" -sub ${LesionFiles[0]} "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_corrWM); then
			:
		else
			printf "\nCheck Image Orientations for T1 and Lesion Mask. Skipping Subject: ${SUBJ}.";
			printf "${SUBJ} Skipped" >> "$WORKINGDIR"/lesion_data.csv;
			printf '\n' >> "$WORKINGDIR"/lesion_data.csv;
			cd "$INPUTDIR" || exit;
			continue;
		fi

		corrWM=$SUBJECTOPDIR/Intermediate_Files/"${SUBJ}"_corrWM.nii.gz;

		fslmaths $ANATOMICAL -mul "${corrWM}" "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_NormRangeWM;

		WM_Mean=$(fslstats "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_NormRangeWM -M);

		# accounting for potential multiple lesions for this subject

		# updating number of max lesions (we need this to create the csv later)
		NumLesionFiles=$(find -d "${SUBJ}"*"${LESION_MASK}"*.nii* | wc -l);

		if (( maxlesions < NumLesionFiles )); then
			maxlesions=$NumLesionFiles;

			echo "updated num of max lesions: " "$maxlesions";
		fi

		counter=1;

		#create subject info array

		declare -a SubjInfoArray;

		TotalNativeBrainVol=$(fslstats "${BET_Brain}" -V | awk '{print $2;}');

		SubjInfoArray=($SUBJ $TotalNativeBrainVol ${WM_Mean});

		for Lesion in ${LesionFiles[@]}; do

			#calculate original and white matter adjusted lesion volumes
			OrigLesionVol=$(fslstats "$Lesion" -V | awk '{print $2;}');

			CorrLesionVol=$( wmCorrection );

			VolRemoved=$(awk "BEGIN {printf \"%.9f\",${OrigLesionVol}-${CorrLesionVol}}");

			PercentRemoved=$(awk "BEGIN {printf \"%.9f\",${VolRemoved}/${TotalNativeBrainVol}}");

			#determine side of lesion
			#this gets the center of gravity of the lesion using the mni coord and then extracts the first char of the X coordinate
			LesionCOG=$(fslstats ${Lesion} -c | awk '{print substr($0,0,1)}');

			if [ $LesionCOG == '-' ]; then
				LesionSide='L';
			else
				LesionSide='R';
			fi

			#concatenate onto array with all lesion volumes and percentage:
			SubjInfoArray+=(${LesionSide});
			SubjInfoArray+=(${OrigLesionVol});
			SubjInfoArray+=(${CorrLesionVol});
			SubjInfoArray+=(${VolRemoved});
			SubjInfoArray+=(${PercentRemoved});


			COG=$(fslstats $Lesion -C);
			COG=$( printf "%.0f\n" $COG );

			fsleyes render -vl $COG --hideCursor -of "$WORKINGDIR"/QC_Lesions/"${SUBJ}"_Lesion"${counter}".png "$ANATOMICAL" $Lesion -a 40 "$SUBJECTOPDIR"/"${SUBJ}"_WMAdjusted_Lesion"${counter}"_bin -cm blue -a 50;

			counter=$((counter+1));

		done

		printf '%s,' ${SubjInfoArray[@]} >> "$WORKINGDIR"/lesion_data.csv;
		printf '\n' >> "$WORKINGDIR"/lesion_data.csv;

		cd "$INPUTDIR" || exit;

	done

#################################[ ADD HEADER TO DATAFILE ]###############################

	cd $WORKINGDIR;
	declare -a HeaderArray;
	HeaderArray=(Subject "Total_Native_Brain_Volume" "Mean_White_Matter_Intensity");

	for i in $(seq 1 $maxlesions); do
		HeaderArray+=(Lesion${i}_Hemisphere);
		HeaderArray+=(Lesion${i}_Original_Lesion_Volume);
		HeaderArray+=(Lesion${i}_Corrected_Lesion_Volume);
		HeaderArray+=(Lesion${i}_Volume_Removed);
		HeaderArray+=(Lesion${i}_Percent_Removed);
	done

	StringArray=$(IFS=, ; echo "${HeaderArray[*]}")

	awk -v env_var="${StringArray}" 'BEGIN{print env_var }{print}' lesion_data.csv > lesion_database.csv;

	rm $WORKINGDIR/lesion_data.csv;