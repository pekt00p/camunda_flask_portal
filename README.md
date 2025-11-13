# Camunda Python UserTask Portal
The goal of this project is to create flexible and feature rich Python based UserTask management console and User Task forms for Camunda BPM. 

- Built with Python and Flask
- REST API integration
- Bootstrap based User Task forms
- Multilanguage support
- RegExp based validations
- File uploads

## Setup

-  Edit **src/app/portal_config.ini**
Set values for url and prot to your Camunda Server location
```
[camunda_server]
url = http://localhost
port = 8080
```
- Execute 
```bash
python run.py
```
- Navigate to http://localhost:5000
If everything is correct you should see this screen:
![](https://raw.githubusercontent.com/pekt00p/camunda_flask_portal/main/screenshots/login_en.jpg)

## Limitations
- Basic Authentication

## License
The source files in this repository are made available under the [Apache License Version 2.0.](https://github.com/camunda/camunda-bpm-platform/blob/master/LICENSE)
