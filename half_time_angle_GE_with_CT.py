#!/usr/bin/env python

"""Anonymises patient data, creates two copies, performs poisson resampling on one 
to produce a simulated half time image and removes the odd numbered frames in the
other to simulate a half angle image"""

#  Graham Arden, May 2009

# import the necessary libraries

import dicom
import os
import shutil 
import time
import numpy
import Tkinter,tkFileDialog

# Function to generate a unique UID, based on time

def generate_new_UID():   
	UID_prefix = "1.2.826.0.1.3680043.8.707" 	# change this if your not me!
	currentTime = (str(time.time()))
	time1, time2 = currentTime.split(".")	
	
	UID = UID_prefix +"."+ time1 + ".1"+time2  	# need to include the .1 to ensure UID element cannot start with 0
	time.sleep(2)							# wait 1 second to ensure ech UID is different
	return UID

# Function to generate a simulated half time image using Poisson resampling.

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
	
# Function to generate a simulated half angle image by stripping out odd numbered frames.

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

# Same again, this time for gated images

#def half_angle_gated(oldImage):
#	newImage = numpy.zeros(len(oldImage[0]/2), len(oldImage[1], len(oldImage[2], int)
#	a = range(0,512)
#	b = []
#	[b.extend(a[i:i + 8]) for i in range (0, len(a), 16)]	

# Generate a random order for the suffix

def random_suffix(numberOfChoices):
	from random import shuffle
	choices=numberOfChoices
	possibleSuffixList = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
	suffixList=possibleSuffixList[0:choices]
	shuffle(suffixList)
	return suffixList

# Anonymises all the other headers which may identify the patient

def anonymise_other_headers(ds):
        if "PatientsBithDate" in ds:
                ds.PatientsBirthDate=""
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
        if (0x0009, 0x1040) in ds:
                ds[0x0009,0x1040].value = ""

# Select the directory containing our files:
root = Tkinter.Tk()
root.withdraw()
fileDirectory = tkFileDialog.askdirectory(parent=root, title='Select the directory to save files in..', initialdir="C:\Documents and Settings\ardeng\My Documents\RR_Project\Bone")

detailsFile=os.path.join(fileDirectory,'File_details_YGC_bone.txt')



# Check if the file File_Details.txt exists, if not create it

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
	textFile.write ("%-15s%-15s%-14s%-14s%-14s%-14s" %("Patient No.", "Original ID", "Original", "Half Time", "Original", "Half Angle"))
	textFile.write("\n")
	textFile.write("\n")
	textFile.close()

textFile = open(detailsFile, "a") # open the details file in append mode in order to add new information at the end.

# Create directories we wish to save the modified images into
halfTimeImageDirectory=os.path.join(fileDirectory,patientNumber,"Half_time")
halfAngleImageDirectory=os.path.join(fileDirectory,patientNumber,"Half_angle")
os.makedirs(halfTimeImageDirectory)
os.makedirs(halfAngleImageDirectory)

# Generate new names and patient IDs (giving them random suffixes).

suffixList_HT = random_suffix(2) # generates random order

# Original half time files
newPatientID_HT_orig = "ZZT" + patientNumber + suffixList_HT[0]
newPatientName_HT_orig = "ZZT_Patient" + patientNumber + suffixList_HT[0]
HT_orig_UID = generate_new_UID()
time.sleep(2)	
print "wait, generating UIDs!"
#modified half time files
newPatientID_HT = "ZZT" + patientNumber + suffixList_HT[1]
newPatientName_HT = "ZZT_Patient" + patientNumber + suffixList_HT[1]
HT_UID = generate_new_UID()
time.sleep(2)	
print ".."
#---------------------------------------------------------------------------------------------------------------------------------------------
suffixList_HA = random_suffix(2) # generates random order

# Original half angle files
newPatientID_HA_orig = "ZZS" + patientNumber + suffixList_HA[0]
newPatientName_HA_orig = "ZZS_Patient" + patientNumber + suffixList_HA[0]
HA_orig_UID = generate_new_UID()
time.sleep(2)	
print "..."

# modifed half angle files
newPatientID_HA = "ZZS" + patientNumber + suffixList_HA[1]
newPatientName_HA = "ZZS_Patient" + patientNumber + suffixList_HA[1]
HA_UID = generate_new_UID()

#----------------------------------------------------------------------------------------------------------------------------------------------


# Select the SPECT image (origSPECTImage)
root = Tkinter.Tk()
root.withdraw()
origSPECTImage = tkFileDialog.askopenfilename(title='Choose the SPECT file', initialdir="C:\Documents and Settings\ardeng\My Documents\RR_Project\Bone")


path,fi=os.path.split(origSPECTImage)

dsOrig = dicom.ReadFile(origSPECTImage)

# write these details to file
textFile.write ("%-15s%-15s%-14s%-14s%-14s%-14s" %(str(patientNumber), str(dsOrig.PatientID),str(newPatientID_HT_orig), str(newPatientID_HT), str(newPatientID_HA_orig), str(newPatientID_HA)))
textFile.write("\n")
textFile.close()
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Unmodified version for half time study

newHalfTimeSPECTFileName_unmodified=newPatientID_HT_orig+"_"+fi # These will be our unaltered files
newHalfTimeSPECTFile_unmodified=os.path.join(halfTimeImageDirectory,newHalfTimeSPECTFileName_unmodified)
shutil.copy(origSPECTImage, newHalfTimeSPECTFile_unmodified)
ds = dicom.ReadFile(newHalfTimeSPECTFile_unmodified)
ds.PatientsName=newPatientName_HT_orig
ds.PatientID=newPatientID_HT_orig
anonymise_other_headers(ds)
ds.StudyInstanceUID=HT_orig_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "...."
ds.save_as(newHalfTimeSPECTFile_unmodified)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  Modified Half Time SPECT image

newHalfTimeSPECTFileName_modified=newPatientID_HT+"_"+fi # These will be our modified files
newHalfTimeSPECTFile_modified=os.path.join(halfTimeImageDirectory,newHalfTimeSPECTFileName_modified)
shutil.copy(origSPECTImage, newHalfTimeSPECTFile_modified)
ds = dicom.ReadFile(newHalfTimeSPECTFile_modified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
anonymise_other_headers(ds)
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

ds.save_as(newHalfTimeSPECTFile_modified)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Unmodified version for half angle study

newHalfAngleSPECTFileName_unmodified=newPatientID_HA_orig+"_"+fi # These will be our unaltered files
newHalfAngleSPECTFile_unmodified=os.path.join(halfAngleImageDirectory,newHalfAngleSPECTFileName_unmodified)
shutil.copy(origSPECTImage, newHalfAngleSPECTFile_unmodified)
ds = dicom.ReadFile(newHalfAngleSPECTFile_unmodified)
ds.PatientsName=newPatientName_HA_orig
ds.PatientID=newPatientID_HA_orig
anonymise_other_headers(ds)
ds.StudyInstanceUID=HA_orig_UID
ds.SeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "......."
ds.save_as(newHalfAngleSPECTFile_unmodified)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Modified Half Angle SPECT image

newHalfAngleSPECTFileName_modified=newPatientID_HA+"_"+fi # These will be our modified files
newHalfAngleSPECTFile_modified=os.path.join(halfAngleImageDirectory,newHalfAngleSPECTFileName_modified)
shutil.copy(origSPECTImage, newHalfAngleSPECTFile_modified)
ds = dicom.ReadFile(newHalfAngleSPECTFile_modified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
anonymise_other_headers(ds)
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

ds.NumberofFrames=ds.NumberofFrames/2

# Edit EnergyWindowVector, DetctorVector and RotationVector to take out every second frame
# Mote, all need to be list rather than arrays, hence use of 'tolist()'

headerIndex = range(0, len(ds.EnergyWindowVector), 2)

ds.EnergyWindowVector= (numpy.take(ds.EnergyWindowVector, headerIndex)).tolist()
ds.DetectorVector=(numpy.take(ds.DetectorVector, headerIndex)).tolist()
ds.RotationVector=(numpy.take(ds.RotationVector, headerIndex)).tolist()

# Edit AngularStep and NumberOfFramesInRotation

angularStep = ds[0x0054, 0x0052][0][0x0018, 0x1144].value
angularStep = angularStep*2
ds[0x0054, 0x0052][0][0x0018, 0x1144].value = angularStep

numberOfFramesInRotation = ds[0x0054, 0x0052][0][0x0054, 0x0053].value
numberOfFramesInRotation = numberOfFramesInRotation/2
ds[0x0054, 0x0052][0][0x0054, 0x0053].value = numberOfFramesInRotation

# Edit AngularViewVector
 
angularViewVectorIndex = range(0,(len(ds.AngularViewVector))/4)
angularViewVectorIndex.extend(angularViewVectorIndex)
newAngularViewVector = (numpy.take(ds.AngularViewVector, angularViewVectorIndex)).tolist()
ds.AngularViewVector = newAngularViewVector

# Assume Tomo View Offsets are in groupd of six and removes every alternate group of six

completeIndex=range(0,len(ds[0x0055, 0x1022][0][0x0013, 0x101e].value))
index=[]
[index.extend(completeIndex[i:i + 6]) for i in range (0, len(completeIndex), 12)]
tomoViewOffset = ds[0x0055, 0x1022][0][0x0013, 0x101e].value
newTomoViewOffset = (numpy.take(tomoViewOffset, index)).tolist()
ds[0x0055, 0x1022][0][0x0013, 0x101e].value=newTomoViewOffset

ds.save_as(newHalfAngleSPECTFile_modified)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Select the CT images (origCTImages)
root = Tkinter.Tk()
root.withdraw()


origCTImages = tkFileDialog.askopenfilenames(title='Choose the CT files', initialdir="C:\Documents and Settings\ardeng\My Documents\RR_Project\Bone")

print ".........."
halfTimeUnmodifiedSeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "..........."
halfTimeModifiedSeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "............"
halfAngleUnmodifiedSeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "............."
halfAngleModifiedSeriesInstanceUID=generate_new_UID()


for i in range(0, len(origCTImages)):
	path,fi=os.path.split(origCTImages[i])
	newHalfTimeFileName_unmodified=newPatientID_HT_orig+"_"+fi # These will be our unaltered files
	newHalfTimeFile_unmodified=os.path.join(halfTimeImageDirectory,newHalfTimeFileName_unmodified)
	shutil.copy(origCTImages[i], newHalfTimeFile_unmodified)
	ds = dicom.ReadFile(newHalfTimeFile_unmodified)
	ds.PatientsName=newPatientName_HT_orig
	ds.PatientID=newPatientID_HT_orig
	ds.StudyInstanceUID=HT_orig_UID
	anonymise_other_headers(ds)
	ds.SeriesInstanceUID=halfTimeUnmodifiedSeriesInstanceUID
	ds.save_as(newHalfTimeFile_unmodified)
	
	newHalfTimeFileName_modified=newPatientID_HT+"_"+fi # These will be our modified files
	newHalfTimeFile_modified=os.path.join(halfTimeImageDirectory,newHalfTimeFileName_modified)
	shutil.copy(origCTImages[i], newHalfTimeFile_modified)
	ds = dicom.ReadFile(newHalfTimeFile_modified)
	ds.PatientsName=newPatientName_HT
	ds.PatientID=newPatientID_HT
	ds.StudyInstanceUID=HT_UID
	anonymise_other_headers(ds)
	ds.SeriesInstanceUID=halfTimeModifiedSeriesInstanceUID
	ds.save_as(newHalfTimeFile_modified)

	newHalfAngleFileName_unmodified=newPatientID_HA_orig+"_"+fi # These will be our unaltered files
	newHalfAngleFile_unmodified=os.path.join(halfAngleImageDirectory,newHalfAngleFileName_unmodified)
	shutil.copy(origCTImages[i], newHalfAngleFile_unmodified)
	ds = dicom.ReadFile(newHalfAngleFile_unmodified)
	ds.PatientsName=newPatientName_HA_orig
	ds.PatientID=newPatientID_HA_orig
	ds.StudyInstanceUID=HA_orig_UID
	anonymise_other_headers(ds)
	ds.SeriesInstanceUID=halfAngleUnmodifiedSeriesInstanceUID
	ds.save_as(newHalfAngleFile_unmodified)
	
	newHalfAngleFileName_modified=newPatientID_HA+"_"+fi # These will be our modified files
	newHalfAngleFile_modified=os.path.join(halfAngleImageDirectory,newHalfAngleFileName_modified)
	shutil.copy(origCTImages[i], newHalfAngleFile_modified)
	ds = dicom.ReadFile(newHalfAngleFile_modified)
	ds.PatientsName=newPatientName_HA
	ds.PatientID=newPatientID_HA
	ds.StudyInstanceUID=HA_UID
	anonymise_other_headers(ds)
	ds.SeriesInstanceUID=halfAngleModifiedSeriesInstanceUID
	ds.save_as(newHalfAngleFile_modified)

# Select the Attenuation Map images (origCTImages)
root = Tkinter.Tk()
root.withdraw()

origAttMapImage = tkFileDialog.askopenfilename(title='Choose the Attenuation Map file', initialdir="C:\Documents and Settings\ardeng\My Documents\RR_Project\Bone")

print "..............."
halfTimeUnmodifiedSeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "................"
halfTimeModifiedSeriesInstanceUID=generate_new_UID()
time.sleep(2)
print "................."
halfAngleUnmodifiedSeriesInstanceUID=generate_new_UID()
time.sleep(2)
print ".................."
halfAngleModifiedSeriesInstanceUID=generate_new_UID()

path,fi=os.path.split(origAttMapImage)
newHalfTimeFileName_unmodified=newPatientID_HT_orig+"_"+fi # These will be our unaltered files
newHalfTimeFile_unmodified=os.path.join(halfTimeImageDirectory,newHalfTimeFileName_unmodified)
shutil.copy(origAttMapImage, newHalfTimeFile_unmodified)
ds = dicom.ReadFile(newHalfTimeFile_unmodified)
ds.PatientsName=newPatientName_HT_orig
ds.PatientID=newPatientID_HT_orig
ds.StudyInstanceUID=HT_orig_UID
anonymise_other_headers(ds)
ds.SeriesInstanceUID=halfTimeUnmodifiedSeriesInstanceUID
ds.save_as(newHalfTimeFile_unmodified)
	
newHalfTimeFileName_modified=newPatientID_HT+"_"+fi # These will be our modified files
newHalfTimeFile_modified=os.path.join(halfTimeImageDirectory,newHalfTimeFileName_modified)
shutil.copy(origAttMapImage, newHalfTimeFile_modified)
ds = dicom.ReadFile(newHalfTimeFile_modified)
ds.PatientsName=newPatientName_HT
ds.PatientID=newPatientID_HT
ds.StudyInstanceUID=HT_UID
anonymise_other_headers(ds)
ds.SeriesInstanceUID=halfTimeModifiedSeriesInstanceUID
ds.save_as(newHalfTimeFile_modified)

newHalfAngleFileName_unmodified=newPatientID_HA_orig+"_"+fi # These will be our unaltered files
newHalfAngleFile_unmodified=os.path.join(halfAngleImageDirectory,newHalfAngleFileName_unmodified)
shutil.copy(origAttMapImage, newHalfAngleFile_unmodified)
ds = dicom.ReadFile(newHalfAngleFile_unmodified)
ds.PatientsName=newPatientName_HA_orig
ds.PatientID=newPatientID_HA_orig
ds.StudyInstanceUID=HA_orig_UID
anonymise_other_headers(ds)
ds.SeriesInstanceUID=halfAngleUnmodifiedSeriesInstanceUID
ds.save_as(newHalfAngleFile_unmodified)

newHalfAngleFileName_modified=newPatientID_HA+"_"+fi # These will be our modified files
newHalfAngleFile_modified=os.path.join(halfAngleImageDirectory,newHalfAngleFileName_modified)
shutil.copy(origAttMapImage, newHalfAngleFile_modified)
ds = dicom.ReadFile(newHalfAngleFile_modified)
ds.PatientsName=newPatientName_HA
ds.PatientID=newPatientID_HA
ds.StudyInstanceUID=HA_UID
anonymise_other_headers(ds)
ds.SeriesInstanceUID=halfAngleModifiedSeriesInstanceUID
ds.save_as(newHalfAngleFile_modified)


print "...................Finished!"

# Close the text file
textFile.close
