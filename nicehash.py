import config

try:
	import time
	import logging  
	import logging.handlers

	LEVEL = logging.DEBUG # Pick minimum level of reporting logging - debug OR info
	
	# Format to include when, who, where, what
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# Name is module name
	logger = logging.getLogger(__name__)  
	logger.setLevel(LEVEL)

	# Create file size limit and file name
	handler = logging.handlers.RotatingFileHandler('debug.log', maxBytes=2000000, backupCount=10)  
	handler.setLevel(LEVEL)  
	handler.setFormatter(formatter)

	# Add handler to logger
	logger.addHandler(handler)  

	logger.info("Starting app")
	
	totalProf = 0.0
	wemoEnabled = False

	def getProf():
		#query the nicehash API and sum the profitibility per day (in BTC)
		import json, requests
		url = 'https://api.nicehash.com/api'

		params = dict(
			method='stats.provider.ex',
			addr= config.btcAddress
		)
		global totalProf
		totalProf = 0.0
		try:
			logger.debug("requesting data from nicehash")
			resp = requests.get(url=url, params=params)
			#logger.debug("nicehash api request response code: "+str(resp.status_code))
		
			stats = json.loads(resp.text)
			#logger.debug(stats["result"]["current"])
			
			for i in stats["result"]["current"]:
				algoProf = float(i["profitability"])
				if "a" in i["data"][0]:
					#there is activity for this algo
					#to get the profitibility per day in BTC, multiply "a" rate by algo profitibility and add to total prof 
					totalProf = totalProf + (algoProf * float(i["data"][0]["a"]))
			logger.info("current total profitibility in BTC/day is " + str(totalProf))
		except KeyError:
			logger.debug("caught exception on request, probably due to api hit frequency, waiting 10 seconds")
			time.sleep(10)
			getProf()

		return totalProf

	def sendAlert(message, alert):
		#trigger IFTTT event
		import requests
		report = {}
		report["value1"] = message
		logger.debug("sending request to: "+"https://maker.ifttt.com/trigger/" + alert + "/with/key/" + config.iftttKey)
		r = requests.post("https://maker.ifttt.com/trigger/" + alert + "/with/key/" + config.iftttKey, data=report)
		logger.debug("request response code: "+str(r.status_code))
		
	def testAlert():
		#test your alert
		logger.debug("sending test alert")
		sendAlert("Testing your alert. " + str(totalProf) + ": BTC/Dday","nicehash")
	
	#testAlert()
	
	def sendWemoPowerToggle():
		#trigger IFTTT wemo event
		import requests
		eventName = "miner_power_toggle"
		url = "https://maker.ifttt.com/trigger/" + eventName + "/with/key/" + config.iftttKey
		logger.debug("sending request to: "+url)
		r = request.post(url)
		logger.debug("request response code: "+str(r.status_code))
	
	timer = 0

	messagesSent = 0	

	getProf()
	
	if totalProf == 0:
		#looks like the miner is off, alert immediately
		logger.warning("The miner is off, sending alert")
		if timer >= config.offTimer and messagesSent == 0:
			#has been below the minProf for greater than the slow alert threshold setting, raise an alert
			sendAlert("NiceHash miner is off. Go fix it.","nicehash")
			messagesSent = 1
		timer = timer + 30
		
	if totalProf < config.minProf:
		#currently making less that min profitability setting
		logger.info("Miner currently less than threshold, monitoring every 30 seconds until recovers")
		#Check again every 30 seconds for 5 minutes
		while totalProf < config.minProf:
			getProf()
		
			if timer >= config.slowAlertTimer and messagesSent == 0:
				#has been below the minProf for greater than the slow alert threshold setting, raise an alert
				sendAlert("NiceHash is running slow.  Current rate is " + str(totalProf) + " BTC/Day","nicehash")
				messagesSent = 1
				logger.info("The miner has been slow for 5 minutes.  Current speed is "  + str(totalProf) + " BTC/Day")
			if timer%900 == 0 and messagesSent ==1:
				#reminder alerts every 15 minutes
				sendAlert("NiceHash is STILL running slow for " + str(timer / 60) +" mins. Current rate is " + str(totalProf) + " BTC/Day","nicehash")
				logger.info("The miner has still running slow after " + str(timer / 60) + " mins. Continuing to check every 30 seconds until it recovers.")
				#if wemo enabled then power the miner
				if wemoEnabled:
					logger.info("sending signal to power the wemo off")
					sendWemoPowerToggle()
					time.sleep(10)
					logger.info("sending signal to power the wemo back on")
					sendWemoPowerToggle()
			logger.debug("sleeping for 30 seconds")
			time.sleep(30)
			timer = timer + 30

	if messagesSent == 1:
		#if it got to this point with a messageSent=1, then it's had an issue and recovered, send recovery message	
		sendAlert("NiceHash is fast again.  Current rate is " + str(totalProf) + " BTC/Day.  It was down for " + str(timer / 60) + " mins","nicehash")
		logger.info("The miner is back to a normal speed.  Current speed is "  + str(totalProf) + " BTC/Day")
	
	logger.info("All is well.  Nicehash is running above expected rate :)  Closing.")
	#if the script ends without entering either while statement, then all is well, it should run again via cron
	
except Exception as e:
    logger.exception("something bad happened")  