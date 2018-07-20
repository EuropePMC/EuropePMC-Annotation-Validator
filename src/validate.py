#!/usr/bin/env python
'''
Created on 18 June 2018

@author: Aravind Venkatesan
@contact: avenkat@ebi.ac.uk
@version: 1.0
@summary: The script uses the Europe PMC Annotation Validator to validate all incoming (textmined or/and curated) annotations
@param: filename, provider name and Annotation type. For more information refer to README

'''
#import pprint
import os
import sys 
from AnnotationValidator import AnnotationValidator

#pp = pprint.PrettyPrinter(indent=4)

def main(agrv):
    inputfile = agrv[0]
    provider = agrv[1]
    annotation = agrv[2]
    outputdir = agrv[3]        
    
    val = AnnotationValidator()
    print("...Validating the annotations...")
    errors = val.validateFile(inputfile, provider, annotation)
    
    filename = os.path.splitext(os.path.basename(inputfile))[0]
        
    if len(errors['log-errors']) != 0:
        log_errors =  filename + "_log-errors.txt"
        log_error_file = os.path.join(outputdir, log_errors)
        with open(log_error_file, "wb") as logFH:
            for l_err in errors['log-errors']:
                logFH.write(l_err)
                logFH.write("\n")
    
    if len(errors['schema-errors']) != 0:
        schema_errors = filename + "_schema-errors.txt"
        schema_error_file = os.path.join(outputdir, schema_errors)                        
        with open(schema_error_file, "wb") as schFH:
            for sch_err in errors['schema-errors']:
                schFH.write(sch_err)
                schFH.write("\n")            
    print("Validation process completed, please check the corresponding files in the supplied: %s" % outputdir)
    print("If no files were generated the submitted annotations were valid, Please upload the file(s) to the submission system.")

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print "Usage: python %s <inputFile> <providerName> <AnntationType> <outputDirectory>" % str(sys.argv[0])
        sys.exit(1)
    else:
        main(sys.argv[1:])
