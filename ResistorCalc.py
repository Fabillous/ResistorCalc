import argparse
import csv
import sys
import math
from itertools import combinations_with_replacement as combinations


numple = 0

numsr = 0

def load_resistor_values(file_path):
    """Load resistor values from a CSV file and return as a list of floats."""
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            resistor_values = []
            for row in reader:
                for value in row:
                    try:
                        # Convert to float and handle units like 'k', 'M'
                        value = value.strip().lower().replace('k', 'e3').replace('m', 'e6')
                        #formatvalue = f"{float(value):.2e}"
                        resistor_values.append(value)
                    except ValueError:
                        print(f"Invalid value {value} in CSV, skipping...", file=sys.stderr)
            return resistor_values
    except FileNotFoundError:
        print(f"File {file_path} not found.", file=sys.stderr)
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Find resistor pairings to match a target resistance.")
    
    # Target resistance argument
    parser.add_argument('-t', '--target', type=str, required=True, 
                        help="Target resistance (e.g., '10k', '1M').")
    
    # Resistor values CSV file argument
    parser.add_argument('-v', '--values', type=str, default = "SMD.csv", 
                        help="Path to CSV file containing resistor values.")
    
    parser.add_argument('-e', '--error', type=float, default = 0.005, 
                        help="Allowed error 0-1.")
                        
    parser.add_argument('-s', '--series', type=int, default = 2, 
                        help="Number of resistances in series.")
    parser.add_argument('-p', '--parallel', type=int, default = 2, 
                        help="Number of resistances in parallel.")
    parser.add_argument('-n', '--number', type=int, default = 10, 
                        help="Number of combos to find.")
    
    args = parser.parse_args()
    
    # Convert target resistance to float, handling 'k', 'M'
    target_resistance = args.target.strip().lower().replace('k', 'e3').replace('m', 'e6')
    try:
        target_resistance = float(target_resistance)
    except ValueError:
        print(f"Invalid target resistance {args.target}", file=sys.stderr)
        sys.exit(1)
    
    return target_resistance, args.values, args.error, args.series, args.parallel, args.number

def parallel(resistors):
    global numple
    numple += 1
    total = 0
    for value in resistors:
        total += (1/float(value))
    return (1/total)

def series(resistors):
    global numsr
    numsr += 1
    total = 0
    for value in resistors:
        total += float(value)
    return total
    

#find all series combinations (with replacement) of size num in resistors   
#returns dictionary of tuple (resistor combos), float (equivalent resistance) pairs
def seriesSingleCombo(resistors, num):
    tups = combinations(resistors, num)
    series_sets = {}
    for tup in tups:
        #convert tuple to array, find series / parallel value, append to array
        series_sets[tup] = series(list(tup))
    return series_sets

#find all parallel combinations (with replacement) of size num in resistors
def parallelSingleCombo(resistors, num):
    tups = combinations(resistors, num)
    parallel_sets = {}
    for tup in tups:
        #convert tuple to array, find series / parallel value, append to array
        parallel_sets[tup] = parallel(list(tup))
    return parallel_sets


def seriesAllCombos(resistors,num):
    series_all = {}
    for i in range(1, num+1):
        temp = seriesSingleCombo(resistors, i)
        series_all.update(temp)
    return series_all

#for every combo length between 1 and num (inclusive) find all the combos
#then combine into one big dictionary    
def parallelAllCombos(resistors,num):
    parallel_all = {}
    for i in range(1, num+1):
        temp = parallelSingleCombo(resistors, i)
        parallel_all.update(temp)
    return parallel_all


def findCombo(resistors, targ, error, numsers, numprl, numcombo):
    pal_val = parallelAllCombos(resistors, numprl) #find all parallel combos of resistors between 1 resistor and numprl resistors
    allCombos = {}
    tolerance = targ * error
    numchecked = 0
    numfound = 0
    for i in range(1, numsers+1):
        for combo in combinations(pal_val.keys(), i): #find series combinations of those parallel resistances
            result = sum(pal_val[key] for key in combo)
            numchecked += 1
            if (abs(result - targ) < tolerance):
                numfound += 1
                allCombos[combo] = result
            if (numfound >= numcombo ):
                return allCombos
    if (numfound == 0):
        print(f"Of {numchecked} combinations checked, none were in tolerance.")
    return allCombos

def format_resistors(resistor_tuple):
    formatted_resistors = []
    
    for svalue in resistor_tuple:
        value = float(svalue)
        num_digits = math.floor(math.log10(abs(value))) + 1
        if num_digits > 6:
            formatted_resistors.append(f"{value / 1_000_000:.1f}M")
        elif num_digits > 3:
            formatted_resistors.append(f"{value / 1_000:.1f}k")
        else:
            formatted_resistors.append(f"{value:2.1f}")
    
    return "(" + " || ".join(formatted_resistors) + ")"

def format_single(res):
    if res >= 1_000_000:
        return(f"{res / 1_000_000:.3f}M")
    elif res >= 1_000:
        return(f"{res / 1_000:.3f}k")
    else:
        return(f"{res:2.3f}")


def main():
    # Parse arguments from command line

    target_resistance, resistor_file, err, ser, pll, numcoms = parse_arguments()
    
    # Load resistor values from CSV
    resistor_values = load_resistor_values(resistor_file)
    
    print(f"\nTarget resistance: {target_resistance} ohms")
    print(f"Loaded {len(resistor_values)} resistor values.")
    print()
    comboids = findCombo(resistor_values,target_resistance,err, ser, pll, numcoms)
    for key in comboids:
        nomkey = len(key)
        while(nomkey > 0):
            nomkey -= 1
            if (nomkey == 0):
                print(format_resistors(key[nomkey]), " = ", format_single(comboids[key]))
                break
            print(format_resistors(key[nomkey]), f" +", end=' ')
        #print(key, comboids[key], nomkey)
        

    # Here, you will add the logic to find resistor pairings.
    # ...

if __name__ == "__main__":
    main()
