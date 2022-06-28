# Instructions

## General descriptions

In this program, we developed the GUI interface to make easier users for using hypoDD. There are the main tabs consisting of ph2dt and hypoDD and log panels to see the processes. On the other side, we have Quick and Web help panels (in the future stable versions, we will support the full version of a Web help panel).

In order to use the program, we need to fully understand how hypoDD program works. Ph2dt and HypoDD have two steps, compiling and running the program. Parameters for both them can be seen on the parameter table. Please use the proper values for each parameter before compiling and running.

## General procedures

1. Create a folder so that we can put our project files there.
2. If we have BMKG or ISC catalog, we have to convert them to PHA by using options in `Convert` menu. Plase make sure `phase.dat` placed to our project folder.
3. If we have other PHA files, please select one of them and rename it to `phase.dat`.
4. Copy `station.dat` to our project folder.
5. Select `ph2dt` tab and open our project folder in `Target Directory`.
6. Press `check` button, see that the unchecked files have been checked.
7. Insert the value for each parameter.
8. Press `Compile` button to compile the program and press `Run` button to run it by using the existed compiled program. We can use `Compile and Run` to do both.
9. After checking the output files, we can continue to `HypoDD` tab.

## Tips

1. We can ignore the errors found in `Log: Standard Error` after compiling because they are basically from the source codes.
2. If we found the errors in `Log: Standard Error` after running, check the parameters. Please make sure that the parameters are suitable for our data.