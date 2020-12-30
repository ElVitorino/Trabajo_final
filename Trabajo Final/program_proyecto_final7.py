# -*- coding: utf-8 -*-

# File: XXXX
# Author: 
# Date: 18/12/2020
# Description: 
#
#
#

import sys, os, arcpy

def chooseDescCLC(inputPath, target_fc):
    """It describes a Corine Land Cover geodatabase and detects the Spanish CLC18 
    feature class (CLC18_ES) extracting its path and spatial reference
    
    INPUTS: 
      inputPath: path where the CLC18 folder is located 
      target_fc: name of the feature class of interest 
    OUTPUTS:
      Printed information about CLC18 gdb and feature class of interest
      CLC18path: returns the path of the feature class of interest (CLC18_ES)
      spRefCLC18: spatial reference object of the feature class of interest (CLC18_ES)
    """
    microlin = '-' * 20
    
    # Set the workspace
    arcpy.env.overwriteOutput = True
    wksp = os.path.join(inputPath, 'CLC2018_GDB\CLC2018_ES.gdb')
    arcpy.env.workspace = wksp
    
    # Describe it
    descrGDB = arcpy.Describe(arcpy.env.workspace)
    print 'Current workspace: {}'.format(wksp)
    print '\n\t\t SOME INFORMATION ABOUT CORINE LAND COVER 2018 GEODATABASE\n'
    print '{} named {}'.format(descrGDB.workspaceType, descrGDB.baseName)
    
    datasets = arcpy.ListDatasets(feature_type ='feature')

    CLC18Path = ''
    for ds in datasets: # Describe structure and contents of CLC18
        print ('  Feature Dataset: '), ds
        for fc in arcpy.ListFeatureClasses(feature_dataset = ds):
            print '    Feature class: ', fc
            if fc == target_fc: # Extract the path of the target feature class
                CLC18Path = os.path.join(arcpy.env.workspace, ds, fc) 
        
    print microlin
    print '\nFeature class of interest is {}. It is located in:\n {}'\
            .format(target_fc, CLC18Path)
     
    # Get spatial reference of the feature class of interest
    descCLC18 = arcpy.Describe(CLC18Path)
    spRefCLC18 = descCLC18.spatialReference
    print '\n  Spatial Reference: ', spRefCLC18.name
     
    # Get field list of the feature class of interest
    field_list = arcpy.ListFields(CLC18Path)
    fieldnumber = 0
    print '  ' + target_fc + ' fields:'
    for fld in field_list:
        fieldnumber += 1
        print '    Field {0} ==> name: {1}, Type: {2}, Length: {3}'\
        .format(fieldnumber, fld.name, fld.type, fld.length)
    
    return CLC18Path, spRefCLC18

# Line types
microlin = '-' * 20
lin = '-' * 65
macrolin = '=' * 80

#-------------------------------------------------------------------------------
# Brief description of the script
#-------------------------------------------------------------------------------
print macrolin
print 'This script will extract data from CLC 2018 and print some of its contents'
print macrolin
#-------------------------------------------------------------------------------
# Get the folder with the input data
#-------------------------------------------------------------------------------
inputPath = sys.argv[1]

#-------------------------------------------------------------------------------
# Ask what part of Spain is the user interested in
#-------------------------------------------------------------------------------
esp_location = ''
while (esp_location != 1) and (esp_location != 2):
    esp_location = int(raw_input('Are you interested in Iberian Peninsula (1) or Canary Islands data (2)?'))
    print 'You must insert 1 or 2'
#-------------------------------------------------------------------------------
# Describe CORINE LAND COVER 2018 geodatabase and get the feature class path of interest
#-------------------------------------------------------------------------------
if esp_location == 1:
    descCLC18_output = chooseDescCLC(inputPath, 'CLC18_ES') # Uses descCLC18 function
elif esp_location == 2:
    descCLC18_output = chooseDescCLC(inputPath, 'CLC18_ES_Canarias')

CLC18Path = descCLC18_output[0]
spRefCLC18 = descCLC18_output[1]
print macrolin
#-------------------------------------------------------------------------------
# Ask the kind of output
#-------------------------------------------------------------------------------
def chooseProjectClip():
    CODNUT = ''
    CODNUTValue = ''
    print 'What is the level of disaggregation you are interested in?'
    print '1 ==> Autonomous Commnunity\n2 ==> Province\n3 ==> Municipality'
    CODNUT_raw = raw_input()
    if CODNUT_raw == 1:
        CODNUT = '"CODNUT2"'
        CODNUTValue = raw_input('Which Autonomous Community would you like to visualize?')
    elif CODNUT_raw == 2:
        CODNUT = '"CODNUT3"'
    elif CODNUT_raw == 3:
        CODNUT = '"NATCODE"'


# print 'Madrid polygon is going to be selected and export it to another shapefile'
# raw_input('Press enter to continue\n')
#    
# # Create a temporary layer to run the selection
# layer = 'temp'
# # Create the output
# madrid_25830 = r'D:\Drive\proyecto_programacion\output\shapefiles\madrid_25830.shp'
#     
# try:
#     arcpy.MakeFeatureLayer_management(espBoundaries25830Path, layer)
#     print '{} temporary layer has {} features'\
#     .format(os.path.basename(espBoundaries25830Path), arcpy.GetCount_management(layer))
#        
#     arcpy.SelectLayerByAttribute_management(layer, 'NEW_SELECTION','{0} = {1}'\
#                                             .format('"CODNUT2"',"'ES30'"))
#     print 'Selection in {} temporary layer has {} features'\
#     .format(os.path.basename(espBoundaries25830Path), arcpy.GetCount_management(layer))
# except arcpy.ExecuteError:
#     print(arcpy.GetMessages(2))
# except Exception as ex:
#     print(ex.args[0])
#    
# # Write the selection in the output
# arcpy.CopyFeatures_management(layer, madrid_25830)
# print microlin
# print '{} is located in:\n{}'.format(os.path.basename(madrid_25830), madrid_25830)
# print macrolin

#-------------------------------------------------------------------------------
# Spanish boundaries shapefile is not projected. So it is projected to ETRS_89_UTM_30N
#-------------------------------------------------------------------------------
print 'Spanish boundaries shapefile is not projected'
print 'So it is going to be projected to ETRS_89_UTM_30N'
raw_input('Press enter to continue\n')
# Input data
espBoundariesPath = os.path.join(os.path.sep, inputPath,'lineas_limite','SIGLIM_Publico_INSPIRE', 'SHP_ETRS89', 'recintos_autonomicas_inspire_peninbal_etrs89','recintos_autonomicas_inspire_peninbal_etrs89.shp')
 
# Create output folder
parentPath = os.path.dirname(inputPath)
outputGISPath = os.path.join(parentPath, 'output\GISFiles')
try: # Create new
    os.makedirs(outputGISPath)
except Exception as e:
    if e.args[0] == 183:
        print 'Output folder already exists'
    else:
        print e
 
# Output path
espBoundaries25830Path = os.path.join(outputGISPath, 'esp_boundaries_25830.shp')
 
# Run project tool
# There is already a spatial reference object for the output coordinate system (spRefCLC18)
try:
    arcpy.Project_management(espBoundariesPath, espBoundaries25830Path, spRefCLC18)
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
except Exception as ex:
    print(ex.args[0])
 
print '{} is now projected to {} and located in \n{}'\
.format(os.path.basename(espBoundaries25830Path), spRefCLC18.name, espBoundaries25830Path)
print macrolin
    
# #-------------------------------------------------------------------------------
# # Clip CLC18 using Madrid extent
# #-------------------------------------------------------------------------------
# print 'CLC18 is going to be clipped with Madrid extent'
# raw_input('Press enter to continue\n')
#   
# # Create the output and tolerance
# CLC18Madrid = r'D:\Drive\proyecto_programacion\output\shapefiles\CLC18Madrid.shp'
# xy_tolerance = ''
#   
# # Execute Clip
# try:
#     arcpy.Clip_analysis(CLC18path, madrid_25830, CLC18Madrid, xy_tolerance)
# except arcpy.ExecuteError:
#     print(arcpy.GetMessages(2))
#   
# print '{} is now located in {}'.format(os.path.basename(CLC18Madrid), CLC18Madrid)
# print macrolin
#   
# print 'Script finished'



#-------------------------------------------------------------------------------
# Get unique values from CODE_18 field
#-------------------------------------------------------------------------------

# CLC18Madrid = r'D:\Drive\proyecto_programacion\output\shapefiles\CLC18Madrid.shp'
# fields = ['ID','CODE_18']
# CODE_18Values = []
# with arcpy.da.SearchCursor(CLC18Madrid, fields) as cursor:
#     for row in cursor:
#         print 'FID #{}# ==> CODE_18 value: {:}'.format(row[0], row[1])
#         CODE_18Values.append(int(row[1])) # row[1] is unicode so it´s converted to int
#         del(row)
# del (cursor)
# CODE_18Values = list(set(CODE_18Values)) # Delete duplicates with a set
# CODE_18Values.sort() # Get values ordered
# print CODE_18Values

#-------------------------------------------------------------------------------
# Create as many shapefiles as unique values are in CODE_18 field
#-------------------------------------------------------------------------------

# layerOut = r'D:\Drive\proyecto_programacion\output\shapefiles\prueba'
# madrid_25830 = r'D:\Drive\proyecto_programacion\output\shapefiles\madrid_25830.shp'
# # Choose the ArcGIS project file
# mxd = arcpy.mapping.MapDocument(r'D:\Drive\proyecto_programacion\output\maps\CLC18Madrid_map.mxd')
# df = arcpy.mapping.ListDataFrames(mxd)[0]
# lyrfile = arcpy.mapping.Layer(madrid_25830) # Reference the layer
# arcpy.mapping.AddLayer(df, lyrfile)
# mxd.save()

# CODE_18Values = CODE_18Values[0:5]
# for value in CODE_18Values:
#     try:
#         mxd = arcpy.mapping.MapDocument(r'D:\Drive\proyecto_programacion\output\maps\CLC18Madrid_map.mxd')
#         df = arcpy.mapping.ListDataFrames(mxd)[0]
#         # Export each selection as a shapefile
#         layer = 'CLC18Madrid_' + str(value)
#         shpName = 'CLC18Madrid_' + str(value) + '.shp'
#         lyrName = shpName.replace('shp', 'lyr')
#         pdfName = shpName.replace('shp', 'pdf')
#         shpOutUnique = os.path.join(layerOut, shpName)
#         lyrOutUnique = shpOutUnique.replace('shp', 'lyr')
#         pdfOutUnique = shpOutUnique.replace('shp', 'pdf')
# 
#         arcpy.MakeFeatureLayer_management(CLC18Madrid, layer)
#         arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION","{0} = '{1}'"\
#                                         .format('CODE_18', str(value)))
#         arcpy.CopyFeatures_management(layer, shpOutUnique)
#         print 'Layer {} created'.format(shpName)
#         
#         # Transform selected shapefiles to layers
#         arcpy.MakeFeatureLayer_management(shpOutUnique, layer)
#         arcpy.SaveToLayerFile_management(layer, lyrOutUnique)
# 
#         # Add layer to the project
#         lyrfile = arcpy.mapping.Layer(lyrOutUnique) # Reference the layer
#         arcpy.mapping.AddLayer(df, lyrfile)
#         arcpy.mapping.ExportToPDF(mxd, pdfOutUnique)
# 
#         print '{} created'.format(pdfName)
#     except arcpy.ExecuteError:
#         print(arcpy.GetMessages(2))
#     except Exception as ex:
#         print(ex.args[0])
# 
# print 'script finished'



































































