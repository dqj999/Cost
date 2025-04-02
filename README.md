# Cost
This Python program analyses the CSV file created by SolisManager and produces estimated daily costs for power.
It was created for use with the Octopus Intelligent Go tariff, but should work for Agile tariffs as well.

It enables me to work out how much power I am using at the lower rate and what the balance of cost is between
low rate, high rate and exported pwoer. You can then check your bills at a later date for any major discrepancies.

It is only a rough guide for several reasons:

1. The power consumption figures and rate information used only have 2 decimal places leading to inaccuracies in the calculated cost.
2. Standing charges are not accounted for
3. Daytime car charging sessions on Intelligent Go may have the wrong price recorded as the notification system from Octopus seems somewhat unreliable
   
   
This was tested on a Raspberry PI 3. It might work om other architectures as well. YMMV.

The entire Python code has been created by Google AI Studio using some simple prompts.
I've never written any Python code so the fact that this works was fairly surprising to me! 
Look in the prompts.txt file for the prompts that I gave AI studio to creat this program.
I tested the suggested code at each step between the prompts.

Here's some sample output:

```
 python3 bill.py

--- Solis Data Analysis (Daily Summary) ---
Expecting data file at: /home/dqj999/Solis/config/SolisManagerExecutionHistory.csv
Using column indices: Date=0, Price=2, Import_kWh=8, Export_kWh=9
Low price threshold: < £0.10/kWh
Data file found.
Enter Start Date (dd-Mon-yyyy or dd-Mon-yyyy HH:MM): 01-mar-2025
Enter End Date (dd-Mon-yyyy or dd-Mon-yyyy HH:MM):   31-mar-2025

Analyzing data from 01-Mar-2025 00:00 to 31-Mar-2025 23:59...
Attempting to read file: /home/dqj999/Solis/config/SolisManagerExecutionHistory.csv
File opened successfully.
Skipped header: ['21-Jan-2025 05:30', ' 22-Jan-2025 00:30', ' 27.10', ' DoNothing', ' Average', ' 20%', ' 0.00', ' 0.00', ' 0.08', ' 0.00', ' 0.16', ' 25.95', ' " "']

--- Processing Summary ---
Period Analyzed: 01-Mar-2025 to 31-Mar-2025
Total Rows Processed:      3056
Total Rows In Date Range:  1483
Rows Skipped (Errors):   0
Rows Skipped (Date):     1573
------------------------------

--- Daily Summaries ---
Date        |  Rows |   ImpTot |    ImpLo |    ImpHi |  CostTot |   CostLo |   CostHi |   ExpTot |  ExpCred |  NetCost
----------------------------------------------------------------------------------------------------------------------
01-Mar-2025 |    48 |    15.84 |    15.36 |     0.48 |     1.21 |     1.08 |     0.13 |     5.68 |     0.85 |     0.35
02-Mar-2025 |    48 |     7.12 |     6.88 |     0.24 |     0.55 |     0.48 |     0.07 |     5.92 |     0.89 |    -0.34
03-Mar-2025 |    48 |     4.96 |     4.80 |     0.16 |     0.38 |     0.34 |     0.04 |     8.40 |     1.26 |    -0.88
04-Mar-2025 |    48 |    18.00 |     5.60 |    12.40 |     3.75 |     0.39 |     3.36 |     7.68 |     1.15 |     2.60
05-Mar-2025 |    48 |     3.64 |     3.40 |     0.24 |     0.30 |     0.24 |     0.07 |     7.84 |     1.18 |    -0.87
06-Mar-2025 |    48 |    26.76 |    26.36 |     0.40 |     1.95 |     1.85 |     0.11 |     8.32 |     1.25 |     0.71
07-Mar-2025 |    48 |     5.52 |     5.20 |     0.32 |     0.45 |     0.36 |     0.09 |     6.96 |     1.04 |    -0.59
08-Mar-2025 |    48 |     2.72 |     1.44 |     1.28 |     0.45 |     0.10 |     0.35 |     1.36 |     0.20 |     0.24
09-Mar-2025 |    48 |     7.76 |     6.88 |     0.88 |     0.72 |     0.48 |     0.24 |     6.08 |     0.91 |    -0.19
10-Mar-2025 |    48 |    21.12 |    20.96 |     0.16 |     1.51 |     1.47 |     0.04 |     3.60 |     0.54 |     0.97
11-Mar-2025 |    44 |     7.56 |     7.24 |     0.32 |     0.59 |     0.51 |     0.09 |     3.48 |     0.52 |     0.07
12-Mar-2025 |    48 |     5.64 |     5.32 |     0.32 |     0.46 |     0.37 |     0.09 |     2.88 |     0.43 |     0.03
13-Mar-2025 |    48 |     6.10 |     5.78 |     0.32 |     0.49 |     0.40 |     0.09 |     1.60 |     0.24 |     0.25
14-Mar-2025 |    48 |    16.78 |    16.28 |     0.50 |     1.28 |     1.14 |     0.14 |     3.78 |     0.57 |     0.71
15-Mar-2025 |    48 |     2.96 |     2.40 |     0.56 |     0.32 |     0.17 |     0.15 |     0.54 |     0.08 |     0.24
16-Mar-2025 |    48 |     3.78 |     2.20 |     1.58 |     0.58 |     0.15 |     0.43 |     0.32 |     0.05 |     0.53
17-Mar-2025 |    48 |     6.94 |     6.56 |     0.38 |     0.56 |     0.46 |     0.10 |     1.76 |     0.26 |     0.30
18-Mar-2025 |    48 |     0.00 |     0.00 |     0.00 |     0.00 |     0.00 |     0.00 |     9.52 |     1.43 |    -1.43
19-Mar-2025 |    48 |     0.00 |     0.00 |     0.00 |     0.00 |     0.00 |     0.00 |     8.08 |     1.21 |    -1.21
20-Mar-2025 |    48 |     0.08 |     0.00 |     0.08 |     0.02 |     0.00 |     0.02 |     7.68 |     1.15 |    -1.13
21-Mar-2025 |    48 |    12.00 |    11.44 |     0.56 |     0.95 |     0.80 |     0.15 |     2.64 |     0.40 |     0.56
22-Mar-2025 |    48 |     2.00 |     1.76 |     0.24 |     0.19 |     0.12 |     0.07 |     0.24 |     0.04 |     0.15
23-Mar-2025 |    48 |    19.60 |    11.10 |     8.50 |     3.08 |     0.78 |     2.30 |     0.24 |     0.04 |     3.04
24-Mar-2025 |    48 |     2.00 |     1.84 |     0.16 |     0.17 |     0.13 |     0.04 |     4.24 |     0.64 |    -0.46
25-Mar-2025 |    48 |     3.76 |     3.12 |     0.64 |     0.39 |     0.22 |     0.17 |     0.80 |     0.12 |     0.27
26-Mar-2025 |    48 |     1.20 |     1.12 |     0.08 |     0.10 |     0.08 |     0.02 |     9.76 |     1.46 |    -1.36
27-Mar-2025 |    48 |     2.48 |     2.32 |     0.16 |     0.21 |     0.16 |     0.04 |     8.80 |     1.32 |    -1.11
28-Mar-2025 |    48 |     2.56 |     2.32 |     0.24 |     0.23 |     0.16 |     0.07 |     2.64 |     0.40 |    -0.17
29-Mar-2025 |    48 |    14.96 |     5.32 |     9.64 |     2.98 |     0.37 |     2.61 |     4.96 |     0.74 |     2.24
30-Mar-2025 |    47 |     8.19 |     3.64 |     4.55 |     1.49 |     0.25 |     1.23 |     4.68 |     0.70 |     0.79
31-Mar-2025 |    48 |    19.20 |    18.16 |     1.04 |     1.55 |     1.27 |     0.28 |    10.40 |     1.56 |    -0.01
----------------------------------------------------------------------------------------------------------------------
TOTALS      |  1483 |   251.23 |   204.80 |    46.43 |    26.92 |    14.34 |    12.58 |   150.88 |    22.63 |     4.29

--- End of Report ---


```
