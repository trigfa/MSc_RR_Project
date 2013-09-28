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
#                       Function to generate a simulated half angle image by stripping out odd numbered frames.
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def half_angle(oldImage):
	print "Old image was.....", oldImage.shape
	originalNumberOfFrames=oldImage.shape[0]
	newNumberOfFrames=originalNumberOfFrames/2
	numberOfRows=oldImage.shape[1]
	numberOfColumns=oldImage.shape[2]
	index = range(0,originalNumberOfFrames,2)
	newImage=numpy.zeros((newNumberOfFrames,numberOfRows,numberOfColumns), int)
	newImage = numpy.take(oldImage, index, axis=0)
	print "New image is......", newImage.shape
	return newImage

# Same again, this time for gated images which are in groups of 16, this isn't actually needed can use half_angle as above

#def half_angle_gated(oldImage):
#	print "Old image was.....", oldImage.shape
#	originalNumberOfFrames=oldImage.shape[0]
#	newNumberOfFrames=originalNumberOfFrames/2
#	numberOfRows=oldImage.shape[1]
#	numberOfColumns=oldImage.shape[2]
#	completeIndex=range(0,oldImage.shape[0])
#	gatedindex = []
#	[gatedindex.extend(completeIndex[i:i + 16]) for i in range (0, len(completeIndex), 32)]
#	newImage=numpy.zeros((newNumberOfFrames,numberOfRows,numberOfColumns), int)
#	newImage = numpy.take(oldImage, gatedindex, axis=0)
#	print "New image is......", newImage.shape
#	return newImage


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                   Generate a random order for the suffix
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def random_suffix(numberOfChoices):
	from random import shuffle
	choices=numberOfChoices
	possibleSuffixList = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
	suffixList=possibleSuffixList[0:choices]
	shuffle(suffixList)
	return suffixList

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

if os.path.isfile(detailsFile):
	print "File_details.txt exists, appending details"
	textFile = open(detailsFile, "r")   #open the details file in read-only mode
	#Read the last patient number in the file and add 1 to it
	allLines=textFile.readlines()
	lastLine=allLines[-1]
	allLastLine=lastLine.split()
	lastNumber = int(allLastLine[0])
	patientNumber=str(lastNumber + 1).zfill(4)
	textFile.close()
else:
	print "File_details.txt does not exist, I will create it"
	patientNumber="0001"  # Set the patient number to 0001
	textFile = open(detailsFile, "w", 1)
	textFile.write("Details of files   ")
	textFile.write("\n")
	textFile.write("----------------   ")
	textFile.write("\n")
	textFile.write("\n")
	textFile.write ("%-15s%-15s%-14s%-14s%-14s%-14s" %("Patient No.", "Original ID", "Original", "Half Angle", "Original", "Half Time"))
	textFile.write("\n")
	textFile.write("\n")
	textFile.close()

textFile = open(detailsFile, "a") # open the details file in append mode in order to add new information at the end.

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                              Create directories we wish to save the modified images into
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

halfTimeImageDirectory=os.path.join(fileDirectory,patientNumber,"Half_time")
halfAngleImageDirectory=os.path.join(fileDirectory,patientNumber,"Half_angle")
os.makedirs(halfTimeImageDirectory)
os.makedirs(halfAngleImageDirectory)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                        Generate new names and patient IDs (giving them random suffixes).
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

suffixList_HT = random_suffix(2) # generates random order

# Half time files
newPatientID_HT = "ZZX" + patientNumber
newPatientName_HT = "ZZX_Patient" + patientNumber
HT_UID = generate_new_UID()


# unmodified half time files
newImageID_HT_orig = "ZZX" + patientNumber + suffixList_HT[0]
newImageID_HT_orig_G = newImageID_HT_orig +"_Gated"

# modified half time files
newImageID_HT = "ZZX" + patientNumber + suffixList_HT[1]
newImageID_HT_G = newImageID_HT + "_Gated"

# attenuation map for half time study

newImageID_A = "Attenuation Map"


print ".."

#---------------------------------------------------------------------------------------------------------------------------------------------

suffixList_HA = random_suffix(2) # generates random order

# Half angle files
newPatientID_HA = "ZZXW" + patientNumber
newPatientName_HA = "ZZW_Patient" + patientNumber
HA_UID = generate_new_UID()


# unmodified half time files
newImageID_HA_orig = "ZZW" + patientNumber + suffixList_HA[0]
newImageID_HA_orig_G = newImageID_HT_orig +"_Gated"

# modified half time files
newImageID_HA = "ZZW" + patientNumber + suffixList_HA[1]
newImageID_HA_G = newImageID_HA + "_Gated"

# attenuation map for half time study

newImageID_A = "Attenuation Map"




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#				NON-GATED IMAGE STUFF STARTS HERE
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Select the SPECT image (origSPECTImage)
root = Tkinter.Tk()
root.withdraw()
origNonGatedSPECTImage = tkFileDialog.askopenfilename(title='Choose the non gated SPECT file', initialdir="C:\Documents and Settings\ardeng\My Documents\RR_Project\Cardiac")


path,fi=os.path.split(origNonGatedSPECTImage)

dsOrig = dicom.ReadFile(origNonGatedSPECTImage)

# write these details to file
textFile.write ("%-15s%-15s%-14s%-14s%-14s%-14s" %(str(patientNumber), str(dsOrig.PatientID), str(newImageID_HA_orig), str(newImageID_HA), str(newImageID_HT_orig), str(newImageID_HT) ))
textFile.write("\n")
textFile.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                  Unmodified version for half time study
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

newHalfTimeNonGatedSPECTFileName_unmodified=newImageID_HT_orig+"_"+fi # These will be our unaltered files
newHalfTimeNonGatedSPECTFile_unmodified=os.path.join(halfTimeImageDirectory,newHalfTimeNonGatedSPECTFileName_unmodified)
shutil.copy(origNonGatedSPECTImage, newHalfTimeNonGatedSPECTFile_unmodified)
ds = dicom.ReadFile(newHalfTimeNonGatedSPECTFile_unmodified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
anonymise_other_headers(ds)
ds.ImageID=newImageID_HT_orig
ds.StudyInstanceUID=HT_UID
ds.SeriesInstanceUID=generate_new_UID()
ds.SOPInstanceUID=generate_new_UID()

print "....Unmodified half time study created...."
print " "

ds.save_as(newHalfTimeNonGatedSPECTFile_unmodified)

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


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                              Unmodified version for half angle study
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

newHalfAngleNonGatedSPECTFileName_unmodified=newImageID_HA_orig+"_"+fi # These will be our unaltered files
newHalfAngleNonGatedSPECTFile_unmodified=os.path.join(halfAngleImageDirectory,newHalfAngleNonGatedSPECTFileName_unmodified)
shutil.copy(origNonGatedSPECTImage, newHalfAngleNonGatedSPECTFile_unmodified)
ds = dicom.ReadFile(newHalfAngleNonGatedSPECTFile_unmodified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
anonymise_other_headers(ds)
ds.ImageID=newImageID_HA_orig
ds.StudyInstanceUID=HA_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "......."
ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfAngleNonGatedSPECTFile_unmodified)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                      Modified Half Angle SPECT image
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

newHalfAngleNonGatedSPECTFileName_modified=newImageID_HA+"_"+fi # These will be our modified files
newHalfAngleNonGatedSPECTFile_modified=os.path.join(halfAngleImageDirectory,newHalfAngleNonGatedSPECTFileName_modified)
shutil.copy(origNonGatedSPECTImage, newHalfAngleNonGatedSPECTFile_modified)
ds = dicom.ReadFile(newHalfAngleNonGatedSPECTFile_modified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
anonymise_other_headers(ds)
ds.ImageID=newImageID_HA_orig
ds.StudyInstanceUID=HA_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "........"

# now create the actual half time image....
print "Creating the half angle image"
oldSPECT = ds.PixelArray
newSPECT=half_angle(oldSPECT)
ds.PixelData = newSPECT.tostring()   # need to write values back to PixelData reather than PixelArray

#need to modify some other headers to reflect fact we have taken out half the frames

maximumValue = int(newSPECT.max())
countsAccumulated = int(newSPECT.sum())

if "CountsAccumulated" in ds:
	ds.CountsAccumulated = countsAccumulated
	
if "LargestImagePixelValue" in ds:	
	ds.LargestImagePixelValue = maximumValue

if "LargestPixelValueinSeries" in ds:
	ds.LargestPixelValueinSeries = maximumValue
ds.NumberofFrames=ds.NumberofFrames/2

# Edit EnergyWindowVector, DetctorVector and RotationVector to take out every second frame
# Note, all need to be list rather than arrays, hence use of 'tolist()'

headerIndex = range(0, len(ds.EnergyWindowVector), 2)

ds.EnergyWindowVector= (numpy.take(ds.EnergyWindowVector, headerIndex)).tolist()
ds.DetectorVector=(numpy.take(ds.DetectorVector, headerIndex)).tolist()
ds.RotationVector=(numpy.take(ds.RotationVector, headerIndex)).tolist()

# Philips system uses Radial Position, need to take out every second value as above.

radialPosition = ds[0x0054,0x0052][0][0x0018,0x1142].value
ds[0x0054,0x0052][0][0x0018,0x1142].value=(numpy.take(radialPosition, headerIndex)).tolist()

# Edit AngularStep and NumberOfFramesInRotation

angularStep = ds[0x0054, 0x0052][0][0x0018, 0x1144].value
angularStep = angularStep*2
ds[0x0054, 0x0052][0][0x0018, 0x1144].value = angularStep

numberOfFramesInRotation = ds[0x0054, 0x0052][0][0x0054, 0x0053].value
numberOfFramesInRotation = numberOfFramesInRotation/2
ds[0x0054, 0x0052][0][0x0054, 0x0053].value = numberOfFramesInRotation

# Edit AngularViewVector (runs form 1 to 64, therfore need to take the first half of the values, NOT ALTERNATE VALUES)
 
angularViewVectorIndex = range(0,(len(ds.AngularViewVector))/2)
newAngularViewVector = (numpy.take(ds.AngularViewVector, angularViewVectorIndex)).tolist()
ds.AngularViewVector = newAngularViewVector

ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfAngleNonGatedSPECTFile_modified)






#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#				GATED IMAGE STUFF STARTS HERE
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Select the  Gated SPECT image (origGatedSPECTImage)
root = Tkinter.Tk()
root.withdraw()
origGatedSPECTImage = tkFileDialog.askopenfilename(title='Choose the gated SPECT file', initialdir="~/Documents")


path,fi=os.path.split(origGatedSPECTImage)
dsOrig = dicom.ReadFile(origGatedSPECTImage)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                              Unmodified version for half time study
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

newHalfTimeGatedSPECTFileName_unmodified=newImageID_HT_orig+"_"+fi # These will be our unaltered files
newHalfTimeGatedSPECTFile_unmodified=os.path.join(halfTimeImageDirectory,newHalfTimeGatedSPECTFileName_unmodified)
shutil.copy(origGatedSPECTImage, newHalfTimeGatedSPECTFile_unmodified)
ds = dicom.ReadFile(newHalfTimeGatedSPECTFile_unmodified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
anonymise_other_headers(ds)
ds.ImageID=newImageID_HT_orig_G
ds.StudyInstanceUID=HT_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "...."
ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfTimeGatedSPECTFile_unmodified)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  Modified Half Time SPECT image

newHalfTimeGatedSPECTFileName_modified=newImageID_HT+"_"+fi # These will be our modified files
newHalfTimeGatedSPECTFile_modified=os.path.join(halfTimeImageDirectory,newHalfTimeGatedSPECTFileName_modified)
shutil.copy(origGatedSPECTImage, newHalfTimeGatedSPECTFile_modified)
ds = dicom.ReadFile(newHalfTimeGatedSPECTFile_modified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
anonymise_other_headers(ds)
ds.ImageID=newImageID_HT_G
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
ds.save_as(newHalfTimeGatedSPECTFile_modified)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Unmodified version for half angle study

newHalfAngleGatedSPECTFileName_unmodified=newImageID_HA_orig+"_"+fi # These will be our unaltered files
newHalfAngleGatedSPECTFile_unmodified=os.path.join(halfAngleImageDirectory,newHalfAngleGatedSPECTFileName_unmodified)
shutil.copy(origGatedSPECTImage, newHalfAngleGatedSPECTFile_unmodified)
ds = dicom.ReadFile(newHalfAngleGatedSPECTFile_unmodified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
anonymise_other_headers(ds)
ds.ImageID=newImageID_HA_orig_G
ds.StudyInstanceUID=HA_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "......."
ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfAngleGatedSPECTFile_unmodified)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Modified Half Angle SPECT image

newHalfAngleGatedSPECTFileName_modified=newImageID_HA+"_"+fi # These will be our modified files
newHalfAngleGatedSPECTFile_modified=os.path.join(halfAngleImageDirectory,newHalfAngleGatedSPECTFileName_modified)
shutil.copy(origGatedSPECTImage, newHalfAngleGatedSPECTFile_modified)
ds = dicom.ReadFile(newHalfAngleGatedSPECTFile_modified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
anonymise_other_headers(ds)
ds.ImageID=newImageID_HA_G
ds.StudyInstanceUID=HA_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "........"

# now create the actual half angle image....

print "Creating the half angle image"
oldSPECT = ds.PixelArray
newSPECT=half_angle(oldSPECT)
ds.PixelData = newSPECT.tostring()   # need to write values back to PixelData reather than PixelArray

#need to modify some other headers to reflect fact we have taken out half the frames

maximumValue = int(newSPECT.max())
countsAccumulated = int(newSPECT.sum())

if "CountsAccumulated" in ds:
	ds.CountsAccumulated = countsAccumulated
	
if "LargestImagePixelValue" in ds:	
	ds.LargestImagePixelValue = maximumValue

if "LargestPixelValueinSeries" in ds:
	ds.LargestPixelValueinSeries = maximumValue
ds.NumberofFrames=ds.NumberofFrames/2

# Edit EnergyWindowVector, DetctorVector and RotationVector to take out every second frame
# Note, all need to be list rather than arrays, hence use of 'tolist()'

headerIndex = range(0, len(ds.EnergyWindowVector), 2)

ds.EnergyWindowVector= (numpy.take(ds.EnergyWindowVector, headerIndex)).tolist()
ds.DetectorVector=(numpy.take(ds.DetectorVector, headerIndex)).tolist()
ds.RotationVector=(numpy.take(ds.RotationVector, headerIndex)).tolist()

# Philips system uses Radial Position, need to take out every second value as above.

radialHeaderIndex = range(0, len(ds[0x0054,0x0052][0][0x0018,0x1142].value), 2)
radialPosition = ds[0x0054,0x0052][0][0x0018,0x1142].value
ds[0x0054,0x0052][0][0x0018,0x1142].value=(numpy.take(radialPosition, radialHeaderIndex)).tolist()

# Edit AngularStep and NumberOfFramesInRotation

angularStep = ds[0x0054, 0x0052][0][0x0018, 0x1144].value
angularStep = angularStep*2
ds[0x0054, 0x0052][0][0x0018, 0x1144].value = angularStep

numberOfFramesInRotation = ds[0x0054, 0x0052][0][0x0054, 0x0053].value
numberOfFramesInRotation = numberOfFramesInRotation/2
ds[0x0054, 0x0052][0][0x0054, 0x0053].value = numberOfFramesInRotation

# Edit AngularViewVector (runs from 1 to 64, therfore need to take the first half of the values, NOT ALTERNATE VALUES)
 
angularViewVectorIndex = range(0,(len(ds.AngularViewVector))/2)
newAngularViewVector = (numpy.take(ds.AngularViewVector, angularViewVectorIndex)).tolist()
ds.AngularViewVector = newAngularViewVector

ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfAngleGatedSPECTFile_modified)





#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#             ATTENUATION MAP IMAGE STUFF STARTS HERE
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Select the Attenuation Map images (origCTImages)
root = Tkinter.Tk()
root.withdraw()

origAttMapImage = tkFileDialog.askopenfilename(title='Choose the Attenuation Map file', initialdir="~/Documents")

# copy to half time directory

path,fi=os.path.split(origAttMapImage)
newHalfTimeFileName_unmodified=newImageID_HT+"_"+fi # These will be our unaltered files
newHalfTimeFile_unmodified=os.path.join(halfTimeImageDirectory,newHalfTimeFileName_unmodified)
shutil.copy(origAttMapImage, newHalfTimeFile_unmodified)
ds = dicom.ReadFile(newHalfTimeFile_unmodified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
ds.StudyInstanceUID=HT_UID
ds.ImageID="Attenuation_Map"
anonymise_other_headers(ds)
ds.SeriesInstanceUID=generate_new_UID()
ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfTimeFile_unmodified)

# copy to half angle directory

newHalfAngleFileName_unmodified=newImageID_HA+"_"+fi # These will be our unaltered files
newHalfAngleFile_unmodified=os.path.join(halfAngleImageDirectory,newHalfAngleFileName_unmodified)
shutil.copy(origAttMapImage, newHalfAngleFile_unmodified)
ds = dicom.ReadFile(newHalfAngleFile_unmodified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
ds.StudyInstanceUID=HA_UID
ds.ImageID="Attenuation_Map"
anonymise_other_headers(ds)
ds.SeriesInstanceUID=generate_new_UID()
ds.SOPInstanceUID=generate_new_UID()
ds.save_as(newHalfAngleFile_unmodified)




print "...................Finished!"

# Close the text file
textFile.close
