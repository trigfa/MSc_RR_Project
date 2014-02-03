#!/usr/bin/env python

"""Anonymises patient data, creates two copies, performs poisson resampling on one 
to produce a simulated half time image and removes the odd numbered frames in the
other to simulate a half angle image"""

#  Graham Arden, May 2009
# Version 0.9

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                Import the necessary libraries
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import dicom
import os
import shutil 
import time
import numpy
import Tkinter,tkFileDialog

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                    Function to generate a unique UID, based on time
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_new_UID():   
	UID_prefix = "1.2.826.0.1.3680043.8.707" 	# change this if your not me!
	currentTime = (str(time.time()))
	time1, time2 = currentTime.split(".")	
	
	UID = UID_prefix +"."+ time1 + ".1"+time2  	# need to include the .1 to ensure UID element cannot start with 0
	time.sleep(2)							# wait 1 second to ensure ech UID is different
	return UID

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                 Function to generate a simulated half time image using Poisson resampling.
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def half_time(oldImage):
	newImage = numpy.zeros_like(oldImage)
	for i in range(0, oldImage.shape[0]):
		for j in range(0, oldImage.shape[1]):
			for k in range(0, oldImage.shape[2]):
				origValue = oldImage[i,j,k]
				newValue=(origValue/2)
				Value = numpy.random.poisson(newValue)
				newImage[i,j,k] = Value		# write the value to newImage
	return newImage

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Anonymises all the other headers which may identify the patient
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def anonymise_other_headers(ds):
	if "AccessionNumber" in ds:
		ds.AccessionNumber=""
        if "PatientsBithDate" in ds:
                ds.PatientsBirthDate=""
	if "PatientsBirthTime" in ds:
		ds.PatientsBirthTime=""
        if "PatientsSex" in ds:
                ds.PatientsSex=""
        if "OtherPatientIDs" in ds:
                ds.OtherPatientIDs=""
        if "OtherPatientNames" in ds: 
                ds.therPatientNames=""
        if "PatientsSize" in ds:
                ds.PatientsSize=""
        if "PatientsWeight" in ds:
                ds.PatientsWeight=""
        if "EthnicGroup" in ds:
                ds.EthnicGroup=""
        if "Occupation" in ds:
                ds.Occupation=""
	if "ReferringPhysiciansName" in ds:
		ds.ReferringPhysiciansName=""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Select the directory containing our files:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


root = Tkinter.Tk()
root.withdraw()
fileDirectory = tkFileDialog.askdirectory(parent=root, title='Select the directory to save files in..', initialdir="~")

detailsFile=os.path.join(fileDirectory,'File_details_WMH_cardiac.txt')



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Check if the file File_Details.txt exists, if not create it
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                              Create directories we wish to save the modified images into
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

halfTimeImageDirectory=os.path.join(fileDirectory,patientNumber,"Half_time")
halfAngleImageDirectory=os.path.join(fileDirectory,patientNumber,"Half_angle")
os.makedirs(halfTimeImageDirectory)
os.makedirs(halfAngleImageDirectory)






#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#				NON-GATED IMAGE STUFF STARTS HERE
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Select the SPECT image (origSPECTImage)
root = Tkinter.Tk()
root.withdraw()
origNonGatedSPECTImage = tkFileDialog.askopenfilename(title='Choose the non gated SPECT file', initialdir="C:\Documents and Settings\ardeng\My Documents\RR_Project\Cardiac")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                      Modified Half Time SPECT image
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

newHalfTimeNonGatedSPECTFileName_modified=newImageID_HT+"_"+fi # These will be our modified files
newHalfTimeNonGatedSPECTFile_modified=os.path.join(halfTimeImageDirectory,newHalfTimeNonGatedSPECTFileName_modified)
shutil.copy(origNonGatedSPECTImage, newHalfTimeNonGatedSPECTFile_modified)
ds = dicom.ReadFile(newHalfTimeNonGatedSPECTFile_modified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
anonymise_other_headers(ds)
ds.ImageID=newImageID_HT
ds.StudyInstanceUID=HT_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "....."


oldSPECT = ds.PixelArray
print "Poisson sampling image - This may take some time!"
newSPECT = half_time(oldSPECT)
maximumValue = int(newSPECT.max())

# need to change some other headers to reflect the fact we have halved the time

if "LargestImagePixelValue" in ds:	
	ds.LargestImagePixelValue = maximumValue

if "LargestPixelValueinSeries" in ds:
	ds.LargestPixelValueinSeries = maximumValue

if "ActualFrameDuration" in ds:
	newFrameDuration = int((ds.ActualFrameDuration/2))
	ds.ActualFrameDuration = newFrameDuration

ds.PixelData = newSPECT.tostring()   # need to write values back to PixelData reather than PixelArray
ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfTimeNonGatedSPECTFile_modified)



print "...................Finished!"

# Close the text file
textFile.close
