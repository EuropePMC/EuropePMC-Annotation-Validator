#!/usr/bin/env python
'''
Created on 18 June 2018

@author: Aravind Venkatesan
@contact: avenkat@ebi.ac.uk
@version: 1.0
@summary: Annotation Validator
@param: filename, provider name and Annotation type

'''

import json
from jsonschema import Draft4Validator, FormatChecker
import requests
import os


class AnnotationValidator():
    def validateFile(self, filename, providerName, annotationsType):
        annotationData = list() 
        errorsMap = {'log-errors' : list(), 'schema-errors': list()}       
        fn = ''.join(os.path.splitext(os.path.basename(filename)))
        max_length = 10000
        error_length = 100
        ann_type_by_provider = {'PheneBank': ['phenotype','diseases','cell','molecule','anatomy','gene_mutations','gene_proteins'],
                                'OGER': ['gene_ontology','cell','cell_line','chemicals','clinical_drug','diseases','gene_proteins','molecular_process','organ_tissue','organisms','sequence']
                                }
        flag = False
        
        if providerName in ann_type_by_provider.keys():
            flag = True
         
        try:
            with open(filename, "rb") as annFH:
                lineno = None
                for index, line in enumerate(annFH):
                    lineno = index + 1
                    try:
                        annotationData.append(json.loads(line))
                    except ValueError, jsonerr:
                        sch_message = "File: " + fn + ", Line: " + str(lineno) + ", Message: " +  repr(jsonerr)
                        errorsMap['schema-errors'].append(str(sch_message)) 
                                                    
                    if lineno > max_length:
                        len_message = "NOTE: The annotation file %s contains over %d lines. Please consider splitting the file before submission" % (fn, lineno) 
                        errorsMap['schema-errors'].append(str(len_message))
                         
                        return errorsMap
                                                                                             
        except Exception, annfileerr:
            errorsMap['log-errors'].append(repr(annfileerr))
            
        if len(errorsMap['schema-errors']) != 0:
            return errorsMap    
        else:
            annotation_type = annotationsType.upper()
            if annotation_type == 'NAMED_ENTITY':
                ne_jsonSchema, logerrors = self.getSchema(annotation_type)
                errorsMap['log-errors'].extend(logerrors)
                
                for jsonObject in annotationData:
                    line = annotationData.index(jsonObject) + 1
                    try:                        
                        for key in jsonObject:
                            if key == "provider":
                                if jsonObject[key] != providerName:
                                    provider_message =  "File: " + fn + ", Line number: " + str(line) + ", JSON path : " + "/" + key + \
                                    ", Message: Supplied provider name: '%s' and 'provider': '%s' in the annotation do not match" % (providerName, jsonObject[key])
                                    errorsMap['schema-errors'].append(str(provider_message))
                            try:
                                if key == "anns":
                                    for annotation in jsonObject[key]:
                                        if not (annotation['prefix'] or annotation['postfix']):
                                            #print(annotation)
                                            prefix_message =  "File: " + fn + ", Line number: "+ str(line) + ", JSON path : " + "/" + key + "/" + str(jsonObject[key].index(annotation)) + \
                                            ", Message: Either 'prefix' or 'postfix' is a required field. Alternatively, for validating sentence based annotations use the corresponding json schema"
                                            errorsMap['schema-errors'].append(str(prefix_message))
                                    
                                        if flag == True:
                                            if annotation['type'] not in ann_type_by_provider[providerName]:
                                                ann_type_message = "File: " + fn + ", Line number: "+ str(line) + ", JSON path : " + "/" + key + "/" + str(jsonObject[key].index(annotation)) + \
                                            ", Message: The value for 'type' field does not match our records. Please provide the appropriate annotation type as registered."
                                            errorsMap['schema-errors'].append(str(ann_type_message))
                                            
                     
                                            
                            except KeyError, keyerr:
                                key_message =  "File: " + fn + ", Line number: " + str(line) + ", JSON path : " + "/" + key + \
                                ", Message: " + repr(keyerr)
                                errorsMap['schema-errors'].append(str(key_message))
                                                
                        for error in sorted(ne_jsonSchema.iter_errors(jsonObject), key=lambda e: e.path):                   
                            location = '/' + '/'.join([str(c) for c in error.relative_path])
                            error_message = "File: " + fn + ", Line number: "+ str(line) + ", JSON path : " + location + ", Message: " + str(error.message)
                            errorsMap['schema-errors'].append(str(error_message))


                    except Exception, nedataerr:
                        errorsMap['log-errors'].append(repr(nedataerr)) 
                    
            elif annotation_type == 'SENTENCE': 
                sent_jsonSchema, logerrors = self.getSchema(annotation_type)
                errorsMap['log-errors'].extend(logerrors)
                for jsonObject in annotationData:
                    line = annotationData.index(jsonObject) + 1 
                    try: 
                        for key in jsonObject:
                            if key == "provider":
                                if jsonObject[key] != providerName:
                                    provider_message =  "File: " + fn + ", Line number: "+ str(line) + ", JSON path : " + "/" + key + \
                                    ", Message: Supplied provider name: %s and 'provider': %s in the annotation do not match" % (providerName, jsonObject[key])
                                    errorsMap['schema-errors'].append(str(provider_message))

                            if key == "anns":
                                for annotation in jsonObject[key]:
                                    if ('position' in annotation or 'prefix' in annotation or 'postfix' in annotation): 
                                        warning_message =  "File: " + fn + ", Line number: "+ str(line) + ", JSON path : " + "/" + key + "/" + str(jsonObject[key].index(annotation)) + \
                                        ", Message: Found 'position'|'prefix'|'postfix' field(s). For validating Named Entity annotations use the corresponding json schema"
                                        errorsMap['schema-errors'].append(str(warning_message))
                                    
                                               
                        for error in sorted(sent_jsonSchema.iter_errors(jsonObject), key=lambda e: e.path):
                            location = '/' + '/'.join([str(c) for c in error.relative_path])
                            error_message = "File: " + fn + ", Line number: "+ str(line) + ", JSON path : " + location + ", Message: " + str(error.message)
                            errorsMap['schema-errors'].append(str(error_message))
                            
                    except Exception, sentdataerr:
                        errorsMap['log-errors'].append(repr(sentdataerr))
                        
            if len(errorsMap['schema-errors']) >= error_length:
                len_error = "NOTE: The annotation validator has raised %d errors in the annotation file: %s, Please check the errors before re-submission."\
                 % (len(errorsMap['schema-errors']), fn)
                del errorsMap['schema-errors'][100:]
                errorsMap['schema-errors'].append(str(len_error))  
            
            return errorsMap
               
                    
    @staticmethod
    def getSchema(inputtype):
        errorLog = list()
        validSchema = None
        if inputtype == 'NAMED_ENTITY':
            try:
                request_schema = requests.get('http://europepmc.org/docs/ne_annotation_schema.json') 
                ne_schemaObj = request_schema.json()
                validSchema =  Draft4Validator(ne_schemaObj, format_checker=FormatChecker())
                    
            except Exception, nescherr:
                errorLog.append(repr(nescherr))

        elif inputtype == 'SENTENCE':
            try:
                request_schema = requests.get('http://europepmc.org/docs/sentence_annotation_schema.json')
                sent_schemaObj = request_schema.json()
                validSchema =  Draft4Validator(sent_schemaObj, format_checker=FormatChecker())

            except Exception, sentscherr:
                errorLog.append(repr(sentscherr))

        return (validSchema, errorLog)
        