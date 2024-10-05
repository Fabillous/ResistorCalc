# ResistorCalc
Generate arbitrary resistances from a given set of values.

### -t --target
Set the target resistance

### -v --values
Load the csv file containing available resistor values. Accepts units, so values may be written like 33k, 1.2M, etc

### -e --error
Set the tolerance between 0 and 1
Default = 0.01

### -s --series
Set the number of resistances in series in the string.
Default = 2

### -p --parallel
Set the number of resistors in each resistance of the string.
Default = 2

### -n --number
Set the number of combinations sought.
Default = 10
