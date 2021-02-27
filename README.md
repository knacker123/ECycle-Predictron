# ECycle-Predictron
Tool to analyze data of race series. Reads external data, displays the current standings od the race series and predicts results, based on the past results. The tool was mainly written for private use to further analyse the race results od the 2020/2021 E-Cycling-Leaque Austria: https://www.e-cycling-austria.at/

I published the code for the following reasons:
- Feel free to use the program, if you are interested in further statistics
- Feel free to review my Python source code. I am always eager to learn
- Feel free to contribute to the project - either by adding some more features, or by adding further Import Modules for other racing leaques. Maybe, just contact me in advance.

Currently, the tool only supports the result format of the Austrian ECyclingLeaque (https://www.e-cycling-austria.at/).

## Installation
```
Requirements: Python 3.5+ installed.

$ pip3 install -r requirements.txt

# Now you can run the ECycle-Predictron
$ python3 main.py directoryname
```
directoryname is the path to a directory, where all of your race results are stored as PDF.

## Example Usage
Store the program to:
C:\Users\ECycle-Predictron

Create another folder in this directory:
C:\Users\ECycle-Predictron\results

Copy all pdfs of the race results of the E-Cycling-Leaque-Austria into this folder.
Now run
```
$ python3 main.py results
```

All of the results in the PDFs will be imported. Now you can follow the instructions of the command line program.
You have the following options:
* help
* print the current leaderboard
* print a predicted leaderboard
* show stats of a dedicated rider

## License

See the [LICENSE](./LICENSE.md) file for license rights and limitations.
