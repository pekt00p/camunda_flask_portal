__author__ = 'Oleg Ladizhensky'

import json
import codecs 
import sys
from pathlib import Path
import re

class Translations:
    pattern = '{{translations\..*}}'
    translation_data = {} #common translations dict
    translation_raw_data = '' #output of translations file
    def __init__(self):
        
        try:
            with codecs.open('app/static/translations/translations.json', 'r', 'utf-8') as translations_data_file:
                self.translation_raw_data = json.load(translations_data_file) 	         
            translations_data_file.close()
            #Making common translation dict
            for translation in self.translation_raw_data:
                self.translation_data[translation['key']] = translation['translations']
            
        except:
            print ('Translation file exception:'+ str(sys.exc_info()[0]))
    
    def parse_template(self, template, language):
        translation_dict = {} #local translations dict
        try:
            template_text = Path(template).read_text()
            tags = re.findall(self.pattern, template_text)
            tags = list(map(lambda x : x[15:-2], tags)) #remove Ninja template symbols
        except Exception as e:
            print ('Template file exception: '+ + str(e))
        
        for tag in tags:          
            translation_dict[tag] = self.translation_data[tag][language]
        return translation_dict
        
    

class Validations:
    pattern = '{{validations\..*}}'
    validation_data = {} #common translations dict
    validation_raw_data = '' #output of translations file
    def __init__(self):
        
        try:
            with codecs.open('app/static/validations/validations.json', 'r', 'utf-8') as validation_data_file:
                self.validation_raw_data = json.load(validation_data_file) 	         
            validation_data_file.close()
            #Making common translation dict
            for validation in self.validation_raw_data:
                self.validation_data[validation['key']] = validation['validation_pattern']
            
        except Exception as e:
            print ('Validation file exception: '+ str(e))
    
    def parse_template(self, template):
        #Get fields for validation
        validation_dict = {} #local validation dict
        try:
            template_text = Path(template).read_text()
            tags = re.findall(self.pattern, template_text)
            tags = list(map(lambda x : x[14:-2], tags)) #remove Ninja template symbols
        except:
            print ('Template file exception:'+ str(sys.exc_info()[0]))
        for tag in tags:          
            validation_dict[tag] = self.validation_data[tag]
        return validation_dict
    def validate_input(self, user_form, validation_dict):
        #Check user input on server side. Prevent XSS
        for key, value in user_form.items():
            if re.search(value, validation_dict[key]): pass
            else:
                return False
        return True
            
        