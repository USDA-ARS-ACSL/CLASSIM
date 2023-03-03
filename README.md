# CLASSIM
Interface program for our crop models
This is the interface for our crop models. it is written in Python, version 10.0.8 and utilizes QT for the interface
We use Anaconda Python
use the yml file to create the environment. 
Conda env create -f classim2022.yml -p /your/path/here

The interface requires a database for input (crop.db) and output (cropoutput.db) as well as the crop models
The databases are in the database folder. The models are in the CLASSIMDirectoryStructure.zip file

You must create a folder called Classim_v3 in your documents folder. Copy the databases from databases.zip and 
all the files in the CLASSIMDIrectoryStructure.zip file to this folder

open a command window in the environment created above. Run the model as --  Python Classim_rb.py

