:author: Jinook Oh
:email: jinook.oh@univie.ac.at
:institution: Cognitive Biology Dept., University of Vienna


------------------------------------------------
CATOS: Computer Aided Training/Observing System
------------------------------------------------

.. class:: abstract

   In animal behavioral biology, there are several cases in which an autonomous observing/training system would be useful. 1) Observation of certain species continuously, or for documenting specific events, which happen irregularly; 2) Longterm intensive training of animals in preparation for behavioral experiments; and 3) Training and testing of animals without human interference, to eliminate potential cues and biases induced by humans. The primary goal of this study is to build a system named CATOS (Computer Aided Training/Observing System) that could be used in the above situations. As a proof of concept, the system was built and tested in a pilot experiment, in which cats were trained to press three buttons differently in response to three different sounds (human speech) to receive food rewards. The system was built in use for about 6 months, successfully training two cats. One cat learned to press a particular button, out of three buttons, to obtain the food reward with over 70 percent correctness.

.. class:: keywords

   animal training, animal observing, automatic device

Introduction
------------

It is often the case in animal behavioral biology that a large amount of human resources, time, and data storage (such as video recordings) are required in animal observation and training. Some representative examples of these cases are:

• Observation of certain species continuously or monitoring for specific events, which occur irregularly, when behavior of certain species during any time period or specific time period, such as nocturnal behaviors, are investigated.

• Certain experiments require a prolonged training period, sometimes over a year. This type of experiment requires reliable responses, which may not correspond to usual behavior patterns, from animals in tasks. Therefore, training may require a long period of time until the subject is ready to be tested. Additionally, long periods of human supervised training can introduce unintended cues and biases for animals.

In the first case, an autonomous system for observing animals can save human resources and reduce the amount of data storage. The reduced amount of data can also conserve other types of human resources such as investigation and maintenance of large-scale data. There have been attempts to build autonomous observing or surveillance systems in the fields of biology, such as Kritzler et al. [Kri08]_’s work, and security systems, such as Belloto et al. [Bel09]_, Vallejo et al. [Val09]_, for instance. There are also commercial products for surveillance systems with various degrees of automation, or incorporating artificial intelligence. However, the intelligence of each system is case-specific and it is difficult to apply these specific systems to novel situations without considerable adjustments. In the second case, an autonomous system for prolonged, intensive training can also save human resources and eliminate potential cues and biases caused by humans. Training with an autonomous system is an extension of traditional operant conditioning chambers and many modern and elaborated versions have been developed and used, such as in Markham et al. [Mar96]_, Takemoto et al. [Tak11]_, Kangas et al. [Kan12]_, Steurer et al. [Ste12]_, and Fagot & Bonte [Fag09]_. However, many of the previous devices use commercial software. Also, they do not possess the observational features developed in the current project. It would be useful to have an open-source, relatively low-budget, and modularized system which could be customized for the observation, training and the experimentation on animal subjects of various species. CATOS, the system built in the present study, fulfills these necessities. The difference between the previous systems and CATOS (Computer Aided Training/Observing System) in the present work is that the animals do not have to be captured or transported to a separated space at a specific time in order to be trained. The disadvantages of separating animals (e.g., primates) are well-known, and include stress on animals separated from their group or moved from their usual confines, the risky catching procedure for both animal and human (cf. Fagot & Bonte [Fag09]_). Similar arguments apply to most animal species, especially when they are social. The automatic learning device for monkeys (ALDM) described in Fagot & Bonte [Fag09]_ is very similar to the trainer aspect of CATOS described in the present work, but CATOS is different in following features. First of all, it aimed to be open-source based and more modular so that it can be more easily adjusted and adopted to different species and experiments. Another feature is that CATOS is equipped with various observational features, including visual and auditory recording and recognition through video camera and microphone, which make the system able to interact with the subjects, such as reacting immediately to a subject with a motion detection from a camera or a sound recognition from a microphone.
CATOS should offer the following advantages.

• The system should be flexible in terms of its adjustability and the extendibility to various projects and species. The software should be open-source, and both software and hardware components should be modularized as much as possible, thus the system reassembly for researchers in animal behavioral biology is practical.

• The system should have various observational features applicable to a broad range of animal species and observational purposes.

• The system should perform continuous monitoring, and it should record video and/or sound only when a set of particular conditions is fulfilled. This would reduce the amount of data produced during the procedure.

• The system should have actuators to react in certain situations, which allows it to act as a trainer/experimenter. The human trainer/experimenter designs the procedure by adjusting parameters and modules, but the actual performance should be done by the system. In this way, the system could help reducing the amount of time required for training, and eliminating cues/biases which might be induced by the human interferences.

• With this system, the animal should not have to be transported to a certain space, or separated from its group, for training. The animals should be able to choose when to start a trial on their own.

Two CATOS prototypes have been built during this study. The first build of CATOS has 3 pushbuttons as a main input device for cats and the second build has a touch-screen as a main input device. The first build was an initial attempt to build and test such a system. The second build is the final product of the study. The basic structures of these two builds are more or less the same. The differences are that the second version has improved functions and it uses the touch-screen instead of pushbuttons. The first build of CATOS was tested with domestic cats (Felis catus) to train them to press three different buttons differently depending on the auditory stimuli (three different human speech sounds). The final goal of this training is to investigate human speech perception in cats. There is no doubt in that many animal species can recognize some words in human speech. The examples of speech perception in dogs and chimpanzees can be found in the work of Kaminski et al. [Kam04]_ and Heimbauer et al. [Hei11]_ respectively. In some cases, animals can even properly produce words with specific purposes. An example of speech perception and production in a parrot can be found in the work of Pepperberg [Pep87]_. Despite these findings, there is ongoing debate about whether the same perceptual mechanisms are used in speech recognition by humans and animals (Fitch [Fit11]_). To investigate this issue, animals have to be trained to show different and reliable responses to different human speech sounds. Then, we can test which features of human speech are necessary for different animal species to understand it. Thus, the final aim of the training in this study would be to obtain cats showing different responses to different human speech sounds with statistical significance (over 75 percent). Before reaching this final goal, several smaller steps and goals are required.

Brief description of CATOS (Computer Aided Training/Observing System)
---------------------------------------------------------------------
The overall system is composed of a combination of software and hardware components. The software components are mainly composed of the Python script named as ’AA.<version>.py’ and the program for the microcontroller. The ’AA’ runs all of the necessary processes and communicates with the microcontroller program. The microcontroller program operates sensors and actuators as it communicates with the ’AA’ program. The hardware components are composed of various devices, some of which are directly connected to the computer via USB cables. Some other devices only have GPIO (General Purpose Input Output) pins; therefore they are connected to the microcontroller. The microcontroller itself is connected to the computer via a USB cable. The hardware devices, which are directly connected via USB cables, can be accessed using various software modules, which are imported into the ’AA’ program. The access to other devices only using GPIO pins is performed in the microcontroller and the ’AA’ program simply communicates with the microcontroller program via a serial connection for sending commands to actuators and receiving values from sensors.

.. figure:: diagram1.png
   :align: center
   
   Overall system diagram. :label:`dgSystem`

The software for this system is called AA (Agent for Animals). This software was build with helps of many external libraries such as OpenCV [Bra00]_, and NumPy/SciPy [Jon01]_. Once it starts, seven processes were launched using multiprocessing package of Python and it runs until the user terminates the program. The multiprocessing was used because the heavy calculation for image processing from multiple webcams were concerned. The number of processes can be changed as some of them can be turned on or off. These processes include a video-in process for each camera, a video-out process, an audio-in process, an audio-out process, a schema process, and a message-board process. Figure :ref:`dgSystem`. Even though some of these processes have quite simple tasks, they were separated in order to prevent them from interfering with each other and/or becoming the bottleneck. The system has to process the visual, auditory, and other sensory and motor information simultaneously to recognize the change of the environment and respond to it properly. The output data such as captured video input images, recorded WAV files, movement-records, CSV files for trial results, and the log file are temporarily stored in the ’output’ folder. After the daily session is finished, all of these output files go through an archiving process which can include, but is not restricted to, generating movies, generating images with the movement analysis, labeling sound files, and moving different types of files into the categorized subfolders of an archiving folder named with a timestamp.

.. figure:: aa_dataviewer.png
   :align: center
   
   AA_DataViewer :label:`AADataViewer`

Besides combining all the above modules and implementing some common functions, one more Python program was implemented to facilitate the process of analyzing the recorded data. The program is called ”AA DataViewer”, which is based on wxPython GUI toolkit and Matplotlib [Hun07]_ for drawing graphs. Figure :ref:`AADataViewer`. It loads the log file, the result CSV (comma separated values) file containing the results of the trial, the movement-record CSV files, the MP4 movie files, and the WAV files from one folder containing all data collected for one session (day). For each video clip, there is a JPEG image showing the movements of the blobs. The circles in the image represent the positions of the blobs and their color represents the time-flow, with the black corresponding to the beginning of the movie, and the white to the end of the movie. A line connecting multiple circles means that those blobs occurred at the same time. Another feature of this program is its ability to generate a graph with selected sessions. In the ’archive’ folder, there are sub-folders, each of which contains all the data for a session. When the ’select sessions’ button is clicked, a pop-up window appears for selecting multiple folders. The result data from these selected sub-folders of ’archive’ folder is drawn as a graph using Matplotlib [Hun07]_. By visualizing the data for certain period, it helps the trainer or experimenter quickly assess the current status of the training procedure.

.. figure:: Feeder_1.png
   :align: center
   
   Automatic feeder :label:`feeder`

The two feeders used in this study is a device mainly comprising the Arduino microcontroller; (refer http://www.arduino.cc/), a motor-shield for the microcontroller, a servomotor, and a frame encasing the whole feeder. Both Feeder variants work in a similar way, by rotating the servomotor by a certain number of degrees, although the second feeder shows better performance in terms of consistent amount of food released, due to the usage of an Archimedes’ screw. Initially, an estimate of the amount of food left in the food container was obtained using an IR distance sensor, but this feature was discarded in the second build since the distance information from the IR sensor was not accurate enough for this application. The second feeder confirms the emission of a food reward via the piezoelectric sensor, which is positioned right below the Archimedes’ screw. Figure :ref:`feeder`.

.. figure:: circuit2.png
   :align: center
   
   Circuit with a microcontroller :label:`circuit`

Communication between the Arduino chip and the main computer was accomplished by using the Arduino module of the ’AA’ program.
In the circuit, Figure :ref:`circuit`,

• The temperature sensor measures the temperature inside of the protective wooden platform.

• The photocell sensor measures the ambient light level.

• The light bulb can be turned on when the photocell sensor indicates the ambient light level is below a user-defined threshold.

• Two fans are turned on when the temperature sensor indicates the temperature is too high in the platform.

• The piezoelectric sensor is read while the servomotor is actuating, in order to confirm the occurrence of the food reward. This sensor reading is required because occasionally the food dispensing fails due to the combination of the short motor activation time (<0.5 seconds) and the shape of the dry food pieces (which can fit into other pieces easily and then fail to emerge).

• The servomotor is responsible for the food dispense by turning the Archimedes’ screw back and forth.

Results of building CATOS and its testing on 2 domesticated cats
----------------------------------------------------------------

The hardware and software were built and tested. The software is available at https://github.com/jinook0707/CATOS_alpha with GNU General Public License, version 3. Both hardware and software are curretnly in its alpha stage. Although its potential to be used to train and test animal cognition was tested and its usage seemed promising to save human resources in certain situations, both hardware and software should be developed further to be practically used for experimenting animal cognition.

The two web-cams observed the experimental area for 8 to 12 hours per day for about 5 months (from the middle of October 2012 to the middle of March 2013). The movement records, MP4 movie files, JPEG image files, and WAV sound files generated during this period took 37.35 Giga bytes of storage. To obtain a rough idea of the degree of reduction in data storage that was achieved using the system, the number of recorded frames in the video recording was assessed. Data for 15 days were taken to calculate it. The total observation period was 406138 seconds, corresponding to 112.8 hours. The number of frames recorded was 206024 and the average FPS(Frame Per Second) was 7.5, therefore, approximately, the video recordings were stored for 27470 seconds (=7.6 hours), which is about 6.7 percent of entire observation period. These specific numbers are not very meaningful since they can fluctuate with the increase or decrease of the subject’s movements, but the point is that the most of the meaningless recordings were successfully filtered out by CATOS.

Human presence during session is not necessary. Data transfer from one computer to another, maintenance, or modification of the system requires human interaction, but no time and effort is required concerning the training and testing sessions. Because no one attends the sessions, a periodic analysis of the animal’s performance with the system is required. A simple assessment of how much food the animals took, or more specifically, how many correct and incorrect trials occurred, can be done quickly since this information is already stored in result CSV file displaying the number of correct and incorrect trials generated with timestamps at the end of each session. Also, the data-viewer utility program displays all the timestamps and its JPEG image, which presents a brief report on the movement detected in the recorded video-clip. Thus, simply browsing the JPEG images is often enough to assess the session. If it is not enough, then one can obtain a more detailed assessment by playing the video-clips recorded around the trial times.

.. figure:: recent_performance.png
   :align: center
   
   Recent performance of the trained cat on three human speech discrimination task. :label:`recPerf`

Two domesticated cats were trained for testing the system. Both cats learned that approaching the feeder on a playback sound could lead to a food reward. Then one cat further learned that pressing one out of three buttons could lead to a food reward. The training of the association between three different sound stimuli and three different buttons is an ongoing process. The most recent performance data Figure :ref:`recPerf` shows over 70 percent of overall performance and also the performance on each button is significantly higher than 33.3 percent of chance level.


References
----------

.. [Bel09] N. Bellotto, E. Sommerlade, B. Benfold, C. Bibby, I. Reid, D. Roth, C. Fernandez, L.V. Gool and J. Gonzalez. *A distributed camera system for multi-resolution surveillance*, Proc. of the third ACM/IEEE Int. Conf. on Distributed Smart Cameras (ICDSC), 2009.

.. [Bra00] G. Bradski. *The OpenCV Library, Dr. Dobb's Journal of Software Tools*, 25(11):122-125, Nov 2000.

.. [Jon01] E. Jones, T. Oliphant, P. Peterson, and others, *SciPy: Open source scientific tools for Python*, 2001.

.. [Fag09] J. Fagot and D. Paleressompoulle. *Automatic testing of cognitive performance in baboons maintained in social groups*, Behavior Research Methods, 41(2):396-404, May 2009.

.. [Fag10] J. Fagot and E. Bonte. *Automated testing of cognitive performance in monkeys: Use of a battery of computerized test systems by a troop of semi-free-ranging baboons (Papio papio)*, Behavior Research Methods, 42(2):507-516, May 2010.

.. [Fit11] T. Fitch. (2011). *Speech perception: a language-trained chimpanzee weighs in*, Current Biology, 21(14):R543-R546, July 2011.

.. [Hei11] L.A. Heimbauer, M.J. Beran and M.J. Owren. *A chimpanzee recognizes synthetic speech with significantly reduced acoustic cues to phonetic content*, Current Biology, 21(14):1210-1214, June 2011.

.. [Hun07] J. D. Hunter, *Matplotlib: A 2D graphics environment*, Computing In Science & Engineering, 9(3):90-95, 2007.

.. [Kam04] J. Kaminski, J. Call and J. Fischer. *Word learning in a domestic dog: evidence for ’fast mapping’*, Science, 304:1682-1683, June 2004.

.. [Kan12] B.D. Kangas and J. Bergman. *A novel touch-sensitive apparatus for behavioral studies in unrestrained squirrel monkeys*, Journal of Neuroscience Methods, 209(2):331-336, August 2012.

.. [Kri08] M. Kritzler, S. Jabs, P. Kegel and A. Krger. *Indoor tracking of laboratory mice via an RFID-tracking framework*, Proc. of the first ACM international workshop on Mobile entity localization and tracking in GPS-less environments, 25-30, 2008.

.. [Mar96] M.R. Markham, A.E. Butt and M.J. Dougher. *A computer touch-screen apparatus for training visual discriminations in rats*, Journal of the Experimental Analysis of Behavior, 65(1):173-182, 1996.

.. [Pep87] I.M. Pepperberg. *Evidence for conceptual quantitative abilities in the African grey parrot: labeling of cardinal sets*, Ethology, 75(1):37-61, 1987.

.. [Ste12] M.M. Steurer, U. Aust and L. Huber. *The Vienna comparative cognition technology(VCCT): An innovative operant conditioning system for various species and experimental procedures*, Behavior Research Methods, 44(4):909-918, December 2012.

.. [Tak11] A. Takemoto, A. Izumi, M. Miwa and K. Nakamura. *Development of a compact and general-purpose experimental apparatus with a touch-sensitive screen for use in evaluating cognitive functions in common marmosets*, Journal of Neuroscience Methods, 199(1):82-86, July 2011.

.. [Val09] D. Vallejo, J. Albusac, L. Jimenez, C. Gonzalez and J. Moreno. *A cognitive surveillance system for detecting incorrect traffic behaviors*, Expert Systems with Applications, 36(7):10503-10511, September 2009.










