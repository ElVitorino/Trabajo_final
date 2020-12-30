# -*- coding: utf-8 -*-

# File: XXXX
# Author: 
# Date: 18/12/2020
# Description: 
#
#
#

import sys, os, arcpy, pandas


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
def chooseLocation(inputPath):
    """It asks questions to choose 
        - the level of disaggregation (community, province or municipality) 
        - and the location at that level (which community, province or municipality)
    So it checks if the location code is registered in csv files that contains 
    all the communities, provinces and municipalities. If not, it asks again.
    
    INPUT:
        - The path of the csv files with the codes of each community, province or municipality
    OUTPUT: list with 2 elements:
        [0] if the location is in the Iberian Peninsula or Canary Islands
            1 = Iberian Peninsula; 2 = Canary Islands
        [1] SQL expression to select the location
    """
    esp_location = ''
    while (esp_location != '1') and (esp_location != '2'):
        esp_location = raw_input('Are you interested in Iberian Peninsula (1) or Canary Islands data (2)?')
     
    # Read csv files with codes of autonomous communities, provinces and municipalities
    CODNUT2csvPath = os.path.join(inputPath, 'CODNUT2.csv')
    CODNUT2csvFile = pandas.read_csv(CODNUT2csvPath, sep = ';', encoding = 'latin1')
    CODNUT3csvPath = os.path.join(inputPath, 'CODNUT3.csv')
    CODNUT3csvFile = pandas.read_csv(CODNUT3csvPath, sep = ';', encoding = 'latin1')
    NATECODEcsvPath = os.path.join(inputPath, 'NATECODE.csv')
    NATECODEcsvFile = pandas.read_csv(NATECODEcsvPath, sep = ';', encoding = 'latin1')
 
    # Create two variables for the SQL queries.
    field = ''
    fieldValue = ''
    # Firstly, ask for the level of disaggregation (autonomous communities, 
    # provinces or municipalities)
    while (field != '1') and (field != '2') and (field != '3'):
        print 'What is the level of disaggregation you are interested in?'
        print '1 ==> Autonomous Commnunity\n2 ==> Province\n3 ==> Municipality'
        field = raw_input()
        if field == '1': # If autonomous community, choose one of them.
            print 'Which autonomous community would you like to visualize?'
            print CODNUT2csvFile
            while fieldValue not in CODNUT2csvFile.cod.tolist(): # First column of the csv file
                fieldValue = raw_input('Enter one code (cod field) ')
        elif field== '2':
            print 'Which province would you like to visualize?'
            print CODNUT3csvFile
            while fieldValue not in CODNUT3csvFile.cod.tolist(): # First column of the csv file
                fieldValue = raw_input('Enter one code (cod field) ')
        elif field == '3':
            field = '"NATCODE"'
            print 'Which municipality would you like to visualize (34132828005)?'
            while fieldValue not in NATECODEcsvFile.cod.tolist(): # First column of the csv file
                fieldValue = int(raw_input('Enter one code (cod field) '))

    return esp_location, field, fieldValue

def projectSelect(spRef, espBoundariesPath, field, fieldValue):
    #-------------------------------------------------------------------------------
    # Spanish boundaries shapefile is not projected. So it is projected to ETRS_89_UTM_30N
    #-------------------------------------------------------------------------------
    print 'Spanish boundaries shapefile is not projected'
    print 'So it is going to be projected to ETRS_89_UTM_30N'
    raw_input('Press enter to continue\n')
    # Create output folder
    parentPath = os.path.dirname(inputPath)
    outputGISPath = os.path.join(parentPath, 'output\GISFiles')
    try: # Create new output folders
        os.makedirs(outputGISPath)
    except Exception as e:
        if e.args[0] == 183:
            print 'Output folder already exists'
        else:
            print e

    # Output file path
    espBoundaries25830Path = os.path.join(outputGISPath, 'esp_boundaries_25830.shp')

    # Run project tool
    # There is already a spatial reference object for the output coordinate system (spRefCLC18)
    try:
        arcpy.Project_management(espBoundariesPath, espBoundaries25830Path, spRef)
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print e

    print '{} is now projected to {} and located in \n{}'\
    .format(os.path.basename(espBoundaries25830Path), spRefCLC18.name, espBoundaries25830Path)
    
    #-------------------------------------------------------------------------------
    # Select and export the location of interest from Spanish boundaries
    #-------------------------------------------------------------------------------
    print 'The poligon/s of interest is/are going to be selected and export it to another shapefile'
    raw_input('Press enter to continue\n')
    
    # Create a temporary layer to run the selection
    layer = 'temp'
    # Create the output
    outputName = 'esp_boundaries_25830_' + str(fieldValue) + '.shp'
    espBoundaries25830SelectedPath = os.path.join(outputGISPath, outputName)
    # Get the SQL query
    SQLquery = '"' + field + '"' + ' = ' + "'" + fieldValue + "'"
    try:
        #Create temporary layer 
        arcpy.MakeFeatureLayer_management(espBoundaries25830Path, layer)
        print '{} temporary layer has {} features'\
        .format(os.path.basename(espBoundaries25830Path), arcpy.GetCount_management(layer))
        # Run the selection
        arcpy.SelectLayerByAttribute_management(layer, 'NEW_SELECTION', SQLquery)
        print 'Selection in {} temporary layer has {} features'\
        .format(os.path.basename(espBoundaries25830Path), arcpy.GetCount_management(layer))
        # Write the selection in the output
        arcpy.CopyFeatures_management(layer, espBoundaries25830SelectedPath)
        print microlin
        print '{} is located in:\n{}'.format(outputName, espBoundaries25830SelectedPath)
        print macrolin
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print e


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
# Ask what part of Spain is the user interested in and get the field and values
# needed to run the selection 
#-------------------------------------------------------------------------------
location_data = chooseLocation(inputPath)
esp_location = location_data[0] # 1 = Iberian Peninsula; 2 = Canary Islands
field = location_data[1] # Field to run the selection 
fieldValue = location_data[2] # Field value to run the selection
print macrolin
#-------------------------------------------------------------------------------
# Describe CORINE LAND COVER 2018 geodatabase and get (depending of Ib.Peninsula vs Canary Isl.):
# * the CLC18 feature class path of interest and its spatial reference object
# * the Spanish boundaries shapefile path of interest
#-------------------------------------------------------------------------------
if esp_location == '1': # Iberian Peninsula
    descCLC18_output = chooseDescCLC(inputPath, 'CLC18_ES')
    espBoundariesPath = os.path.join(os.path.sep, inputPath,'lineas_limite','SIGLIM_Publico_INSPIRE', 'SHP_ETRS89', 'recintos_municipales_inspire_peninbal_etrs89','recintos_municipales_inspire_peninbal_etrs89.shp')
elif esp_location == '2': # Canary Islands
    descCLC18_output = chooseDescCLC(inputPath, 'CLC18_ES_Canarias')
    espBoundariesPath = os.path.join(os.path.sep, inputPath,'lineas_limite','SIGLIM_Publico_INSPIRE', 'SHP_WGS84', 'recintos_municipales_inspire_canarias_wgs84','recintos_municipales_inspire_canarias_wgs84.shp')

CLC18Path = descCLC18_output[0] # Path of the CLC18 of interest (Ib.Pen vs Canary Isl.)
spRefCLC18 = descCLC18_output[1] # Spatial reference object
print macrolin
#-------------------------------------------------------------------------------
# Select and project location layer
#-------------------------------------------------------------------------------
projectSelect(spRefCLC18, espBoundariesPath, field, fieldValue)


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



































































