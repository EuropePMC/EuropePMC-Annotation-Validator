# EuropePMC-Annotation-Validator
A python program to validate annotations to be submitted to the Europe PMC annotation platform.

# Requirements
Provide name - Supplied by the Europe PMC Annotation team.   
  
Annotation type - Named_entity or Sentence.

For help please send email to annotations[at]europepmc.org.

# Dependency
Python jsonschema module: <https://pypi.org/project/jsonschema/>.
 
# Usage

	python validate.py <inputFile> <providerName> <AnntationType> <outputDirectory>

InputFile - Path to the annotation file.   

Output directory - Path to the directory the error files will be written.   

# Output

The script will produces two files:   
   
Schema error file - errors raised during validation process.   
  
Example of schema errors   

	File: my_annotation.json, Line: 6, Message: ValueError('Expecting , delimiter: line 1 column 223 (char 222)',)
	File: my_annotation.json, Line: 10, Message: ValueError('No JSON object could be decoded',)
	File: my_annotation.json, Line: 13, Message: ValueError('Expecting , delimiter: line 1 column 223 (char 222)',)

Log error file - system based errors.   
  
Example of log errors   

	IOError(21, 'Is a directory')

The files will be generated only when errors exists in the annotation file. Once the validation process is completed, please proceed with the uploading of the annotation file to the submission system using the Access and Secret Key provided by the Annotation team.

	
 