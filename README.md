# Cost
This Python program analyses the CSV file created by SolisManager and produces estimated daily costs for power.
It was created for use with Octopus Intelligent Go tariff, but shoudl work for Agile tariffs as well.
It is only a rough guide for several reasons

1. The power consumption figures and rate information used only have 2 decimal places leading to inaccuracies in the calculated cost.
2. Stading charges are not accounted for
3. Daytime car charging sessions on Intelligent Go may have the wrong price recorded as the notification system from Octopus seems somewhat unreliable
   
It has been used a Raspi 3. It may work on other Architectures

The entire Python code has been created by Google AI Studio using some simple prompts.
I've never written any Python code so the fact that this works was fairly surprising to me!


