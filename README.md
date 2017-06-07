# NiceHashPythonMonitor
This is a simple Python NiceHash script I created to monitor one BTC address & rig.  
The script can be modified to monitor more addresses or rigs.  
The script was made to run on Linux in Python 2.7.  

At a high level, it does the following:

1. Check to see if the application is already running
2. Query nicehash API to get the current sum of the btc/day profitibility rates for all algos
3. If the sum = 0, send an alert that the miner is off.
4. If the sum is below the min threshold set in the config, send an alert
5. Alert when back above the set threshold then exit script

The the script uses the IFTTT Maker chanel to do the alerting.  To configure and run:

1. Configure an IFTTT Maker applet. Name the event "nicehash".  Take note of your Maker service key.  
   I configured mine to send both a text and an email
2. Setup the config.py settings.  Add your BTC address and IFTTT key
3. Run nicehash_start.py (should probably configure through cron to run at regular intervals). Sample crontab config below runs every 3 minutes.
		# NHM Status
		*/3 * * * * cd /location/of/pythonscript && /usr/bin/python ./nicehash_start.py
