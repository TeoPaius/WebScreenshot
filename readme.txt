Other dependencies: opencv
To run this firstly it needs and active rabbitmq service. I included the chrome driver for selenium
Firstly the main from the db module needs to be run, which creates the db instance
And then the main from the core which provides a series of queries for the web module
The web module can be used separately too just need the apropriate command line arguments
Of course all modules need to run with the venv activated, otherwise they wont have the required dependencies
The screenshots are located in db/screenshots and the input is in core/input.in
When using read commands it will open an opencv image display, the bad part is i havent found a way to add a scrollbar
to it for big images, i tried with matplotlib's pyplot but that scales the image very ugly