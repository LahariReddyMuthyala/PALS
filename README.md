# Pipeline for Analyzing Lesions after Stroke (PALS)
## Contents
1. [Introduction](#intro).
2. [Expected Data Structure](#datastructure)  
3. [Getting started: Installation Guide](#start)  
  3.1. [Direct use](#direct)  
  3.2. [Singularity](#singularity)
   
4. [PALS Configuration File](#config)
   
   4.1 Quickstart files
   
   4.1.2 [Lesion Correction, Load, and Heatmap](#lesionloadcorheat)
   
   4.1.2 [Lesion Correction](#lesioncorrection)
   
   4.1.2 [Lesion Load](#lesionload)
   
   4.1.2 [Heatmap](#heatmap)
   
   4.1.2 [Full Configuration File Breakdown](#fullconfig)
   
6. [Running PALS](#running)

## What is PALS?<a name=intro></a>
PALS is a pipeline for reliably preprocessing images of subjects with stroke lesions. The pipeline is implemented using [Nipype](https://nipype.readthedocs.io/en/latest/), with several modules:
- Reorientation to radiological convention (LAS, left is right)
- Lesion correction for healthy white matter
- Lesion load calculation by ROI

Here is a visualization of the workflow:  
![pals_workflow](img/pals_workflow.png)

For additional information about the original implementation, see the publication in [Frontier in Neuroinformatics](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).

## Expected Data Structure<a name=datastructure></a>
PALS expects its input data to be [BIDS-compatible](https://bids-specification.readthedocs.io/en/stable/) but does not expect any particular values for the BIDS entities. You will need to modify the [configuration file](#config) to set "LesionEntities" and "T1Entities" to match your data. Outputs are provided in BIDS derivatives.

The naming conventions of the input must be as follows:

**Main Image**: 
  * Unregistered: `sub-{subject}_ses-{session}_T1.nii.gz`
  * Registered: `sub-{subject}_ses-{session}_space-{space}_desc_T1.nii.gz`. 
  
**Lesion Mask**: `sub-{subject}_ses-{session}_space-{space}_label-L_desc-T1lesion_mask.nii.gz`. 
  
**White Matter Segmentation File**: `sub-{subject}_ses-{session}_space-{space}_desc-WhiteMatter_mask.nii.gz`. 

Where 'space' should be the name of the reference image or 'orig' if unregistered. For example `sub-01_ses-R001_space-orig_desc_T1.nii.gz`

## Getting Started: Installation Guide <a name=start></a>
There are two ways to use PALS: directly via the pals_workflow.py Python code, or by using the Singularity definition file provided. The first method will require you to install the python packages listed in [requirements.txt](https://github.com/npnl/PALS/blob/main/requirements.txt). The second method only requires that you have [Singularity](https://docs.sylabs.io/guides/3.5/user-guide/introduction.html) installed and will run the code as a container.

### Preparation for Direct Use (recommended)<a name=direct></a>
A walkthrough of the PALS installation is [available on YouTube](https://youtu.be/8PN3tR34L6g). The command prompts for each step below are in gray.
1. PALS is implemented in Python 3.8.16; you will first need to [install Python](https://www.python.org/downloads/release/python-3810/).
2. We recommend that you also install the Python virtual environment [Virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
    `python3.8 -m pip install --user virtualenv`
3. Create a virtual environment in your worksapce for PALS with `python3.8 -m venv pals_venv` and activate the environment with`source pals_venv/bin/activate`. You can deactivate the environment by typing `deactivate` in the command line when not using PALS. You will need to activate the environment every time before use.
4. Install PALS through your terminal using:
`python3.8 -m pip install -U git+https://github.com/npnl/PALS`  

5. Additionally, you will need to download the PALS code to your workspace: `git clone https://github.com/npnl/PALS` 

6. You will also need to install the following software packages on your machine. This is the full list of required neuroimaging packages:
    * [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki)
      * For running FLIRT and FAST.
    * Python packages in [requirements.txt]()
      * These can be installed in your virtual environment with bash command `python3.8 -m pip install -r requirements.txt`. Run this command when you have 'cd'ed, or entered, into the cloned PALS directory on the command line: `~/PALS`. This command MUST be run when you have activated your virtual environment as in step 3.
  
> Note that if your intended pipeline won't use components that are dependent on a particular package, it does not need to be installed. E.g., if you plan to use FLIRT for registration, you don't need to install ANTs.

7. Lastly, you will need to update the configuration settings (`config.json`) to specify your settings in the PALS directory you downloaded in step 5. See [this section](#config) for how to do so. You can download the [sample config file](https://github.com/npnl/PALS/blob/main/config.json) directly from this repo.

### Preparation for Singularity (Optional) <a name=singularity></a>
PALS will run from the command line through the previous installation steps. The following instructions are only for those who wish to run PALS through a Singularity container. Currently, Singularity requires a LINUX operating system to run. A Docker container for PALS, compatible with Windows & OS operating systems, is in development.

You will first need to download the PALS code: `git clone https://github.com/npnl/PALS`  
[Singularity](https://sylabs.io/guides/3.9/user-guide/quick_start.html#quick-installation-steps) also needs to be installed on your system.

Using the provided Singularity file `pals_singularity.def`, you can build the image using:  
`sudo singularity build pals_singularity.sif pals_singularity.def`

Lastly, you will need to update the configuration settings (`config.json) to specify your settings. See [this section](#config) for how to do so.

## PALS Configuration File<a name=config></a> 
PALS can be configured to run similar pipelines that differ in their implementations. The configuration file is located in the PALS main directory. We have also provided [4 quickstart configuration files](https://github.com/npnl/PALS/tree/main/user_files/quickstart) for lesion load calculation and heatmap generation. The relevant lines to edit are hightlighted below:

### 1) LesionLoad,Correction, Heatmap quickstart file: runs lesion load, lesion correction, and heatmap calculations <a name=lesionloadcorheat></a>

![lesionloadcorheat quickstart](img/config_lesionloadcorrectionheatmap_ref.png)

### 2) Lesion Correction quickstart file: runs lesion correction calculations <a name=lesioncorrection></a>

![lesioncorrection quickstart](img/config_lesioncorrection_ref.png)

### 3) Lesion Load quickstart file: runs lesion load calculations <a name=lesionload></a>

![lesionload quickstart](img/config_lesionload_ref.png)

### 4) Lesion Heatmap: created heatmap <a name=heatmap></a>

![lesionheatmap quickstart](img/config_lesionheatmap_ref.png)


### Full Configuration File Breakdown <a name=fullconfig></a>

Here is the default `config.json`, with explanations of each variable:  
```json
{
 "Analysis": {
  "Reorient": true,                             # bool; Whether to standardize the orientation (e.g. radiological, neurological). Options: true, false.
  "Orientation": "LAS",                         # str; Orientation to standardize to. Options: L/R (left/right), A/P (anterior/posterior), I/S (inferior/superior). Default is LAS.
  "Registration": true,                         # bool; Whether to perform registration to a common template. Options: true, false.
  "RegistrationMethod": "FLIRT",                # str; Registration method. Options: FLIRT (default) or leave blank (no registration).
  "BrainExtraction": true,                      # bool; Whether to perform brain extraction. Options: true, false.
  "BrainExtractionMethod": "BET",               # str; Method to use for brain extraction. Options: BET (default) or leave blank (no brain extraction).
  "WhiteMatterSegmentation": true,              # bool; Whether to do white matter segmentation. Options: true, false. If false, and you want to perform LesionCorrection, LesionLoadCalculation, or Lesionheatmap, you must place file in same location as the input files in the BIDS structure. 
  "LesionCorrection": true,                     # bool; Whether to perform lesion correction. Options: true, false. If true, requires white matter segmentation file.
  "LesionLoadCalculation": true,                # bool; Whether to compute lesion load. Options: true, false. If true, requires white matter segmentation file.
  "LesionHeatMap": true                         # bool; Whether to combine the lesions into a heatmap. Options: true, false. If true, requires white matter segmentation file.
 },
 "BrainExtraction": {                           # Settings to pass to brain extraction; structure depends on Analysis['BrainExtractionMethod']
  "frac": 0.5,
  "mask": true
 },
 "Registration": {                              # Settings to pass to registration; structure depends on Analysis['RegistrationMethod']
  "cost_func": "normmi",
  "reference": "/data1/reference.nii"
 },
 "LesionCorrection": {                          # Settings for white matter correction.
  "ImageNormMin": 0,                            # Minimum value for image.
  "ImageNormMax": 255,                          # Maximum value for image
  "WhiteMatterSpread": 0.05                     # The deviation of the white matter intensity as a fraction of the mean white matter intensity.
 },
 "BIDSRoot": "/data1/data",                     # str; Path to the BIDS root directory for the raw data.
 "Subject": "",                                 # str; ID of the subject to run. If blank, runs all subjects. Ex: r001s001
 "Session": "",                                 # str; ID of the session to run. If blank, runs all sessions. Ex: 1
 "LesionRoot": "/data1/",                       # str; Path to the BIDS root directory for the lesion masks.
 "WhiteMatterSegmentationRoot": "",             # str; Path to the BIDS root directory for the white matter segmentation files.
 "ROIDir": "ROIs",                              # str; Path to the directory containing ROI image files.
 "ROIList": [],                                 # list; List of ROI files to use.
 "Multiprocessing": 4,                          # int; Number of threads to use for multiprocessing. Has no effect unless more than 1 subject is being processed.
 "LesionEntities": {                            # BIDS entity:value pairs for identifying the lesion files. 
  "suffix": "mask",
  "space": "MNI152NLin2009aSym",
  "label": "L"
 },
 "T1Entities": {                               # BIDS entity:value pairs for identifying the T1 images.
  "desc": "T1FinalResampledNorm",
  "space": "MNI152NLin2009aSym"
 },
  "HeatMap": {                                 # Settings for generating the heatmap
  "Reference": "/data1/reference.nii",         # str; Overlays the heatmap on this image and creates NIFTI file with overlay and NITFI file with the mask only. Also produces 4 PNGS: 9 slices of the lesions from sagittal, axial, and coronal orientations (3 images) and an image with a cross-section of each orientation. If your images are pre-registered, you MUST use your own reference image used for their registration.
  "Transparency": 0.4                          # int; Transparency to use when mixing the reference image and the heatmap. Smaller values darker reference and lighter heatmap.
  },
"Outputs": {
  "Root": "/data1/pals/",                       # str; Path to directory where to place the output.
  "StartRegistrationSpace": "MNI152NLin2009aSym",   # str; Value to use for "space" entity in BIDS output filename. 
  "OutputRegistrationSpace": "MNI152NLin2009aSym",  # str; Reserved for future use.    
"RegistrationTransform": "",                    # str; Optional. Path for saving registration transform. 
  "Reorient": "",                               # str; Optional. Path for saving reoriented volume.
  "BrainExtraction": "",                        # str; Optional. Path for saving the brain extracted volume.
  "LesionCorrected": ""                         # str; Optional. Path for saving the white matter-corrected lesions.
 },
}
```

## Running PALS<a name=running></a>
Once the configuration file is set, you can run PALS from the command line:  
For direct use:  
`PALS -h`  
`PALS --config config.json`  
  
For Singularity, with the image pals_singularity.sif:  
`singularity run pals_singularity.sif -h`  
`singularity run pals_singularity.sif --config config.json`

PALS will parse the configuration file, apply the desired pipeline, then return the output in a BIDS directory specified by info in the 'Outputs' section of the config file.
The precise output will depend on the analysis flags you set, but here is a list of the output files you would typically expect:  
- `graph.png`, `graph_detailed.png`  
  - Visual representation of the pipeline used to generate the data.
- `sub-X_ses-Y_desc-LAS_T1w.nii.gz`  
  - The input data reoriented to LAS. "LAS" will change to match your requested orientation.
- `sub-X_ses-Y_desc-LesionLoad.csv`
  - A .csv file containing the lesion load in each of the requested regions of interest. Units are in voxels.
  - `UncorrectedVolume` column contains the total number voxels. `CorrectedVolume` subtracts the white matter voxels (if `LesionCorrection` is set to `true` in the config file) from `UncorrectedVolume`.
- `sub-X_ses-Y_space-SPACE_desc-CorrectedLesion_mask.nii.gz`  
  - The lesion mask after white matter correction; note that the quality of the mask depends on the quality of the white matter segmentation.
- `sub-X_ses-Y_space-SPACE_desc-transform.mat`
  - Affine matrix for the transformation used to register the subject images.
- `sub-X_ses-Y_space-SPACE_desc_WhiteMatter_mask.nii.gz`
  - White matter mask generated by the white matter segmentation.
  
Placeholder values:
- X: subject ID
- Y: session ID
- SPACE: String indicating the space the image is in (e.g. MNI152NLin2009aSym)

## Citing PALS<a name=citation></a>
If you use PALS for you paper, please cite the original PALS publication in [Frontier in Neuroinformatics](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).
