import math
import re

import mechanize
from lxml import html

from data import *

'''
----- setupCalc -----
Setup Calc takes the user information for accessing GPRO and calculates the entire car setup
for the weekend, including session weather and temperature.
'''


def setupCalc(username, password, weather, sessionTemp):
	browser = mechanize.Browser()
	browser.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
	browser.open("https://gpro.net/gb/Login.asp")
	browser.select_form(id="Form1")
	browser.form["textLogin"] = username
	browser.form["textPassword"] = password
	browser.submit()
	
	# Verifica se o login foi bem-sucedido
	current_url = browser.geturl()
	
	if "Login.asp" in current_url:
		raise Exception("Login falhou - ainda na página de login")
	
	# Debug: mostra todos os links disponíveis
	all_links = list(browser.links())
	print(f"setupCalc - Total de links na página: {len(all_links)}")
	for i, link in enumerate(all_links[:10]):  # Mostra os primeiros 10 links
		print(f"  Link {i}: '{link.text}' -> {link.url}")
	
	# Procura especificamente por links que contenham "Driver" ou "Profile"
	driver_links = [link for link in all_links if "Driver" in link.url or "Profile" in link.url]
	print(f"setupCalc - Links com 'Driver' ou 'Profile': {len(driver_links)}")
	for link in driver_links:
		print(f"  - '{link.text}' -> {link.url}")

	# Request the driver information page and scrape the driver data
	try:
		browser.follow_link(url_regex=re.compile("DriverProfile\\.asp"))
		tree = html.fromstring(browser.response().get_data())
		browser.back()
	except Exception as e:
		print(f"Erro ao acessar DriverProfile.asp: {e}")
		# Tenta outros padrões possíveis
		try:
			browser.follow_link(url_regex=re.compile("Driver"))
			tree = html.fromstring(browser.response().get_data())
			browser.back()
			print("Conseguiu acessar usando regex 'Driver'")
		except Exception as e2:
			print(f"Erro ao acessar com regex 'Driver': {e2}")
			raise Exception("Não foi possível acessar o perfil do piloto")

	driverConcentration = int(tree.xpath("normalize-space(//td[contains(@id, 'Conc')]/text())"))
	driverTalent = int(tree.xpath("normalize-space(//td[contains(@id, 'Talent')]/text())"))
	driverAggressiveness = int(tree.xpath("normalize-space(//td[contains(@id, 'Aggr')]/text())"))
	driverExperience = int(tree.xpath("normalize-space(//td[contains(@id, 'Experience')]/text())"))
	driverTechnicalInsight = int(tree.xpath("normalize-space(//td[contains(@id, 'TechI')]/text())"))
	driverWeight = int(tree.xpath("normalize-space(//tr[contains(@data-step, '14')]//td/text())"))

	# Request the track information page and scrape the track data
	try:
		browser.follow_link(url_regex=re.compile("TrackDetails\\.asp"))
		tree = html.fromstring(browser.response().get_data())
		browser.back()
	except Exception as e:
		print(f"Erro ao acessar TrackDetails.asp: {e}")
		raise Exception("Não foi possível acessar os detalhes da pista")

	trackName = str(tree.xpath("normalize-space(//h1[contains(@class, 'block')]/text())"))
	trackName = trackName.strip()

	# Request race strategy pace and scrape the race weather data
	try:
		browser.follow_link(url_regex=re.compile("RaceSetup\\.asp"))
		tree = html.fromstring(browser.response().get_data())
		browser.back()
	except Exception as e:
		print(f"Erro ao acessar RaceSetup.asp: {e}")
		raise Exception("Não foi possível acessar a configuração da corrida")

	rTempRangeOne = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[2]/td[1]/text())"))
	rTempRangeTwo = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[2]/td[2]/text())"))
	rTempRangeThree = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[4]/td[1]/text())"))
	rTempRangeFour = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[4]/td[2]/text())"))
	# This returns results like "Temp: 12*-17*", but we want just integers, so clean up the values
	rTempMinOne = int((re.findall(r"\d+", rTempRangeOne))[0])
	rTempMaxOne = int((re.findall(r"\d+", rTempRangeOne))[1])
	rTempMinTwo = int((re.findall(r"\d+", rTempRangeTwo))[0])
	rTempMaxTwo = int((re.findall(r"\d+", rTempRangeTwo))[1])
	rTempMinThree = int((re.findall(r"\d+", rTempRangeThree))[0])
	rTempMaxThree = int((re.findall(r"\d+", rTempRangeThree))[1])
	rTempMinFour = int((re.findall(r"\d+", rTempRangeFour))[0])
	rTempMaxFour = int((re.findall(r"\d+", rTempRangeFour))[1])
	# Find the averages of these temps for the setup
	rTemp = ((rTempMinOne + rTempMaxOne) + (rTempMinTwo + rTempMaxTwo) + (rTempMinThree + rTempMaxThree) + (
		rTempMinFour + rTempMaxFour)) / 8
	# Using the race strategy page requested earlier, scrape the qualifying weather data
	qOneTemp = str(tree.xpath("normalize-space(//img[contains(@name, 'WeatherQ')]/../text()[contains(., 'Temp')])"))
	qOneTemp = int((re.findall(r"\d+", qOneTemp))[0])
	qTwoTemp = str(tree.xpath("normalize-space(//img[contains(@name, 'WeatherR')]/../text()[contains(., 'Temp')])"))
	qTwoTemp = int((re.findall(r"\d+", qTwoTemp))[0])

	# Check the user selected session and assign the relevant temperature
	if (sessionTemp == "Race"):
		sessionTemp = rTemp
	elif (sessionTemp == "Q1"):
		sessionTemp = qOneTemp
	elif (sessionTemp == "Q2"):
		sessionTemp = qTwoTemp

	# Request the car information page and scrape the car character and part level and wear data
	browser.follow_link(url_regex=re.compile("UpdateCar\\.asp"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	# Level
	carLevelChassis = int(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[2]/text())"))
	carLevelEngine = int(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[2]/text())"))
	carLevelFrontWing = int(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[2]/text())"))
	carLevelRearWing = int(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[2]/text())"))
	carLevelUnderbody = int(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[2]/text())"))
	carLevelSidepod = int(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[2]/text())"))
	carLevelCooling = int(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[2]/text())"))
	carLevelGears = int(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[2]/text())"))
	carLevelBrakes = int(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[2]/text())"))
	carLevelSuspension = int(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[2]/text())"))
	carLevelElectronics = int(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[2]/text())"))
	# And wear. The IF statements here are because if a part is over 90% worn, it's get a "font" container that breaks the normal check
	carWearChassis = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/text())"))
	if (carWearChassis == ""):
		carWearChassis = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/font/text())"))
	carWearChassis = int((re.findall(r"\d+", carWearChassis))[0])
	carWearEngine = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/text())"))
	if (carWearEngine == ""):
		carWearEngine = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/font/text())"))
	carWearEngine = int((re.findall(r"\d+", carWearEngine))[0])
	carWearFrontWing = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/text())"))
	if (carWearFrontWing == ""):
		carWearFrontWing = str(
			tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/font/text())"))
	carWearFrontWing = int((re.findall(r"\d+", carWearFrontWing))[0])
	carWearRearWing = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/text())"))
	if (carWearRearWing == ""):
		carWearRearWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/font/text())"))
	carWearRearWing = int((re.findall(r"\d+", carWearRearWing))[0])
	carWearUnderbody = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/text())"))
	if (carWearUnderbody == ""):
		carWearUnderbody = str(
			tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/font/text())"))
	carWearUnderbody = int((re.findall(r"\d+", carWearUnderbody))[0])
	carWearSidepod = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/text())"))
	if (carWearSidepod == ""):
		carWearSidepod = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/font/text())"))
	carWearSidepod = int((re.findall(r"\d+", carWearSidepod))[0])
	carWearCooling = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/text())"))
	if (carWearCooling == ""):
		carWearCooling = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/font/text())"))
	carWearCooling = int((re.findall(r"\d+", carWearCooling))[0])
	carWearGears = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/text())"))
	if (carWearGears == ""):
		carWearGears = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/font/text())"))
	carWearGears = int((re.findall(r"\d+", carWearGears))[0])
	carWearBrakes = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/text())"))
	if (carWearBrakes == ""):
		carWearBrakes = str(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/font/text())"))
	carWearBrakes = int((re.findall(r"\d+", carWearBrakes))[0])
	carWearSuspension = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/text())"))
	if (carWearSuspension == ""):
		carWearSuspension = str(
			tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/font/text())"))
	carWearSuspension = int((re.findall(r"\d+", carWearSuspension))[0])
	carWearElectronics = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/text())"))
	if (carWearElectronics == ""):
		carWearElectronics = str(
			tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/font/text())"))
	carWearElectronics = int((re.findall(r"\d+", carWearElectronics))[0])

	# Setup calculations
	# Begin by storig the track base values
	trackBaseWingsSetup = float(trackData[trackName][0]) * 2
	trackBaseEngineSetup = float(trackData[trackName][1])
	trackBaseBrakesSetup = float(trackData[trackName][2])
	trackBaseGearsSetup = float(trackData[trackName][3])
	trackBaseSuspensionSetup = float(trackData[trackName][4])
	trackBaseWingSlitSetup = float(trackData[trackName][5])

	# A collection of offset values. These always stay the same, regardless of track
	baseOffsets = {
		"wingWeatherDry": 6,
		"wingWeatherWet": 1,
		"wingWeatherOffset": 263,

		"engineWeatherDry": -3,
		"engineWeatherWet": 0.7,
		"engineWeatherOffset": -190,

		"brakesWeatherDry": 6,
		"brakesWeatherWet": 3.988375441,
		"brakesWeatherOffset": 105.5325924,

		"gearsWeatherDry": -4,
		"gearsWeatherWet": -8.0019964182,
		"gearsWeatherOffset": -4.742711704,

		"suspensionWeatherDry": -6,
		"suspensionWeatherWet": -1,
		"suspensionWeatherOffset": -257,

		"wingDriverMultiplier": -0.001349079032746,
		"engineDriverMultiplier": 0.001655723,
		"engineDriverOffset": 0.0469416263186552
	}

	# Lot of info here and it's hard to see, but these offsets are used when calculating the influence of the level of a part on the setup
	carLevelOffsets = [
		[-19.74, 30.03, -15.07],
		[16.04, 4.9, 3.34],
		[6.04, -29.14, 6.11],
		[-41, 9],
		[-15.27, -10.72, 6.04, 31]
	]

	carWearOffsets = [
		[0.47, -0.59, 0.32],
		[-0.51, -0.09, -0.04],
		[-0.14, 0.71, -0.09],
		[1.09, -0.14],
		[0.34, 0.23, -0.12, -0.70]
	]

	# I know it seems a bit pointless to have this be an array of arrays, but it makes it easier to see which values affect each step.
	driverOffsets = [
		[0.3],
		[-0.5],
		[0.5],
		[0.75, 2]
	]

	'''
    Now, to calculate the session setup.
    There are 4 components that influence car setup for anyway given part:
        1. Weather
        2. Driver
        3. Part Level
        4. Part Wear
    We canculate these components in this order, then dump them into the equation to calculate setup.
    The reason we do them in order, is that some later components are affected by earlier ones, see driver setup on any part for an example
    '''

	# Wings
	sessionTemp = int(sessionTemp)
	weather = weather.upper()

	if (weather != "WET"):
		setupWeather = baseOffsets["wingWeatherDry"] * sessionTemp * 2
	else:
		setupWeather = ((baseOffsets["wingWeatherWet"] * sessionTemp) + baseOffsets["wingWeatherOffset"]) * 2
	setupDriver = driverTalent * (trackBaseWingsSetup + setupWeather) * baseOffsets["wingDriverMultiplier"]
	setupCarLevel = (carLevelOffsets[0][0] * carLevelChassis) + (carLevelOffsets[0][1] * carLevelFrontWing) + (
		carLevelOffsets[0][1] * carLevelRearWing) + (carLevelOffsets[0][2] * carLevelUnderbody)
	setupCarWear = ((carWearOffsets[0][0] * carWearChassis) + (carWearOffsets[0][1] * carWearFrontWing) + (
		carWearOffsets[0][1] * carWearRearWing) + (carWearOffsets[0][2] * carWearUnderbody))
	setupWings = (trackBaseWingsSetup + setupWeather + setupDriver + setupCarLevel + setupCarWear) / 2

	# Wing Split
	if (weather != "WET"):
		setupWingSplit = trackBaseWingSlitSetup + (driverTalent * -0.246534498671854) + (
			3.69107049712848 * (carLevelFrontWing + carLevelRearWing) / 2) + (setupWings * -0.189968386659174) + (
							 sessionTemp * 0.376337780506523)
	else:
		setupWingSplit = trackBaseWingSlitSetup + (driverTalent * -0.246534498671854) + (
			3.69107049712848 * (carLevelFrontWing + carLevelRearWing) / 2) + (setupWings * -0.189968386659174) + (
							 sessionTemp * 0.376337780506523) + 58.8818967363256
	setupFWi = setupWings + setupWingSplit
	setupRWi = setupWings - setupWingSplit

	# Engine
	if (weather != "WET"):
		setupWeather = baseOffsets["engineWeatherDry"] * sessionTemp
	else:
		setupWeather = ((baseOffsets["engineWeatherWet"] * sessionTemp) + baseOffsets["engineWeatherOffset"])
	setupDriver = (driverOffsets[0][0] * driverAggressiveness) + (driverExperience * (
		((trackBaseEngineSetup + setupWeather) * baseOffsets["engineDriverMultiplier"]) + baseOffsets[
		"engineDriverOffset"]))
	setupCarLevel = ((carLevelOffsets[1][0] * carLevelEngine) + (carLevelOffsets[1][1] * carLevelCooling) + (
		carLevelOffsets[1][2] * carLevelElectronics))
	setupCarWear = ((carWearOffsets[1][0] * carWearEngine) + (carWearOffsets[1][1] * carWearCooling) + (
		carWearOffsets[1][2] * carWearElectronics))
	setupEng = (trackBaseEngineSetup + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Brakes
	if (weather != "WET"):
		setupWeather = baseOffsets["brakesWeatherDry"] * sessionTemp
	else:
		setupWeather = ((baseOffsets["brakesWeatherWet"] * sessionTemp) + baseOffsets["brakesWeatherOffset"])
	setupDriver = (driverOffsets[1][0] * driverTalent)
	setupCarLevel = ((carLevelOffsets[2][0] * carLevelChassis) + (carLevelOffsets[2][1] * carLevelBrakes) + (
		carLevelOffsets[2][2] * carLevelElectronics))
	setupCarWear = ((carWearOffsets[2][0] * carWearChassis) + (carWearOffsets[2][1] * carWearBrakes) + (
		carWearOffsets[2][2] * carWearElectronics))
	setupBra = (trackBaseBrakesSetup + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Gears
	if (weather != "WET"):
		setupWeather = baseOffsets["gearsWeatherDry"] * sessionTemp
	else:
		setupWeather = ((baseOffsets["gearsWeatherWet"] * sessionTemp) + baseOffsets["gearsWeatherOffset"])
	setupDriver = (driverOffsets[2][0] * driverConcentration)
	setupCarLevel = ((carLevelOffsets[3][0] * carLevelGears) + (carLevelOffsets[3][1] * carLevelElectronics))
	setupCarWear = ((carWearOffsets[3][0] * carWearGears) + (carWearOffsets[3][1] * carWearElectronics))
	setupGea = (trackBaseGearsSetup + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Suspension
	if (weather != "WET"):
		setupWeather = baseOffsets["suspensionWeatherDry"] * sessionTemp
	else:
		setupWeather = ((baseOffsets["suspensionWeatherWet"] * sessionTemp) + baseOffsets["suspensionWeatherOffset"])
	if (weather != "WET"):
		setupDriver = (driverOffsets[3][0] * driverExperience) + (driverOffsets[3][1] * driverWeight)
	else:
		setupDriver = (driverOffsets[3][0] * float(driverExperience)) + (driverOffsets[3][1] * driverWeight) + (
			driverTechnicalInsight * 0.11)
	setupCarLevel = ((carLevelOffsets[4][0] * carLevelChassis) + (carLevelOffsets[4][1] * carLevelUnderbody) + (
		carLevelOffsets[4][2] * carLevelSidepod) + (carLevelOffsets[4][3] * carLevelSuspension))
	setupCarWear = ((carWearOffsets[4][0] * carWearChassis) + (carWearOffsets[4][1] * carWearUnderbody) + (
		carWearOffsets[4][2] * carWearSidepod) + (carWearOffsets[4][3] * carWearSuspension))
	setupSus = (trackBaseSuspensionSetup + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Take that calculated setup and turn it into an array for easier handling
	setup = [int(setupFWi), int(setupRWi), int(setupEng), int(setupBra), int(setupGea), int(setupSus)]
	return setup


'''
----- strategyCalc -----
Strategy Calc takes user information for accessing GPRO and calculates the optimal strategy
for the upcoming race
'''


def strategyCalc(username, password, minimumWear, laps):
	'''
    There are many factors that influence strategy:
        1. Tyre Supplier
        2. Track Wear on the Tyre
        3. Track Distance
    and many more, simply see the function "stopCalc" for most, and that only deals with the number of stops
    We would LIKE to also take clear track risk into account, but I don't know how risk fits into the equation, so simply cannot add it accurately.
    '''

	browser = mechanize.Browser()
	browser.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
	browser.open("https://gpro.net/gb/Login.asp")
	browser.select_form(id="Form1")
	browser.form["textLogin"] = username
	browser.form["textPassword"] = password
	browser.submit()

	# Request the track information page and scrape the track data
	browser.follow_link(url_regex=re.compile("TrackDetails\\.asp"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	trackName = str(tree.xpath("normalize-space(//h1[contains(@class, 'block')]/text())"))
	trackName = trackName.strip()
	trackTyreWearRating = str(
		tree.xpath("normalize-space(//td[contains(text(), 'Tyre wear')]/following-sibling::td/text())"))
	trackLaps = str(tree.xpath("normalize-space(//td[contains(text(), 'Laps:')]/../td[2]/text())"))
	trackLapsInt = float(re.search("\d+", trackLaps).group())
	trackLapDistance = str(tree.xpath("normalize-space(//td[contains(text(), 'Lap distance:')]/../td[2]/text())"))
	trackLapDistance = trackLapDistance.replace(" ", "")
	trackLapDistanceFloat = float(re.search("\d+\.\d+", trackLapDistance).group())
	trackDistance = str(tree.xpath("normalize-space(//td[contains(text(), 'Race distance:')]/../td[2]/text())"))
	try:
		trackDistanceFloat = float(re.search("\d+\.\d+", trackDistance).group())
	except:
		trackDistanceFloat = float(re.search("\d+", trackDistance).group())
	trackPitInOut = str(tree.xpath("normalize-space(//td[contains(text(), 'Time in/out of pits:')]/../td[2]/text())"))
	try:
		trackPitInOutFloat = float(re.search("\d+\.\d+", trackPitInOut).group())
	except:
		trackPitInOutFloat = float(re.search("\d+", trackPitInOut).group())

	# Check, while we're here, if the manager has a Technical Director and if they do, gather the TD stats
	try:
		browser.click_link(url_regex=re.compile("TechDProfile\\.asp"))
		technicalDirectorResult = html.fromstring(browser.response().get_data())
		browser.back()

		tree = html.fromstring(technicalDirectorResult.content)
		tdExperience = int(tree.xpath("//th[contains(text(), 'Experience:')]/../td[0]/text()")[0])
		tdPitCoordination = int(tree.xpath("//th[contains(text(), 'Pit coordination:')]/../td[0]/text()")[0])
		technicalDirectorValues = [0.0314707991001518, -0.0945456184596369, -0.0355383420267692, -0.00944695128810026,
								   -0.0112688398024834]
	except:
		technicalDirectorValues = [0.0355393906609645, -0.0797977676868435, 0, 0, 0]
		tdExperience = 0
		tdPitCoordination = 0

	# Request the staff page and scrape staff data
	browser.follow_link(url_regex=re.compile("StaffAndFacilities\\.asp"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	staffConcentration = int(tree.xpath("//th[contains(text(), 'Concentration:')]/../td/text()")[0])
	staffStress = int(tree.xpath("//th[contains(text(), 'Stress handling:')]/../td/text()")[0])

	# Request race strategy pace and scrape the race weather data
	browser.follow_link(url_regex=re.compile("RaceSetup\\.asp"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	rTempRangeOne = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[2]/td[1]/text())"))
	rTempRangeTwo = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[2]/td[2]/text())"))
	rTempRangeThree = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[4]/td[1]/text())"))
	rTempRangeFour = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[4]/td[2]/text())"))
	# This returns results like "Temp: 12*-17*", but we want just integers, so clean up the values
	rTempMinOne = int((re.findall(r"\d+", rTempRangeOne))[0])
	rTempMaxOne = int((re.findall(r"\d+", rTempRangeOne))[1])
	rTempMinTwo = int((re.findall(r"\d+", rTempRangeTwo))[0])
	rTempMaxTwo = int((re.findall(r"\d+", rTempRangeTwo))[1])
	rTempMinThree = int((re.findall(r"\d+", rTempRangeThree))[0])
	rTempMaxThree = int((re.findall(r"\d+", rTempRangeThree))[1])
	rTempMinFour = int((re.findall(r"\d+", rTempRangeFour))[0])
	rTempMaxFour = int((re.findall(r"\d+", rTempRangeFour))[1])
	# Find the averages of these temps for the setup
	rTemp = ((rTempMinOne + rTempMaxOne) + (rTempMinTwo + rTempMaxTwo) + (rTempMinThree + rTempMaxThree) + (
		rTempMinFour + rTempMaxFour)) / 8

	# Request the manager page and scrape tyre data
	browser.follow_link(url_regex=re.compile("Suppliers"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	tyreSupplierName = str(tree.xpath("//div[contains(@class, 'chosen')]/h2/text()")[0])

	# Request the car information page and scrape the car character and part level and wear data
	browser.follow_link(url_regex=re.compile("UpdateCar\\.asp"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	# Level
	carLevelEngine = int(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[2]/text())"))
	carLevelSuspension = int(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[2]/text())"))
	carLevelElectronics = int(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[2]/text())"))

	# Request the driver information page and scrape the driver data
	browser.follow_link(url_regex=re.compile("DriverProfile\\.asp"))
	tree = html.fromstring(browser.response().get_data())
	browser.back()

	driverConcentration = int(tree.xpath("normalize-space(//td[contains(@id, 'Conc')]/text())"))
	driverAggressiveness = int(tree.xpath("normalize-space(//td[contains(@id, 'Aggr')]/text())"))
	driverExperience = int(tree.xpath("normalize-space(//td[contains(@id, 'Experience')]/text())"))
	driverTechnicalInsight = int(tree.xpath("normalize-space(//td[contains(@id, 'TechI')]/text())"))
	driverWeight = int(tree.xpath("normalize-space(//tr[contains(@data-step, '14')]//td/text())"))

	# We start by defining some constants. Wear factors are just static hidden values that affect tyre wear based on compound, but only slightly.
	# Without these the equation doesn't QUITE add up properly.
	tyreSupplierFactor = {"Pipirelli": 1, "Avonn": 8, "Yokomama": 3, "Dunnolop": 4, "Contimental": 8, "Badyear": 7}
	tyreCompoundSupplierFactor = {
		"Pipirelli": 0, "Avonn": 0.015, "Yokomama": 0.05, "Dunnolop": 0.07, "Contimental": 0.07, "Badyear": 0.09
	}
	trackWearLevel = {"Very low": 0, "Low": 1, "Medium": 2, "High": 3, "Very high": 4}
	wearFactors = [0.998163750229071, 0.997064844817654, 0.996380346554349, 0.995862526048112, 0.996087854384523]

	# Calcualte the number of stops for each tyre choice
	stops = []
	for i in range(4):
		stops.append(int(stopCalc(trackDistanceFloat, trackWearLevel[trackTyreWearRating], rTemp,
								  tyreSupplierFactor[tyreSupplierName], i, carLevelSuspension, driverAggressiveness,
								  driverExperience, driverWeight, float(trackData[trackName][9]), minimumWear,
								  wearFactors[i], 1)))
	stops.append(int(
		stopCalc(trackDistanceFloat, trackWearLevel[trackTyreWearRating], rTemp, tyreSupplierFactor[tyreSupplierName],
				 5, carLevelSuspension, driverAggressiveness, driverExperience, driverWeight,
				 float(trackData[trackName][9]), minimumWear, wearFactors[4], 0.73)))

	stintlaps = []
	for i in range(5):
		stintlaps.append(int(math.ceil(trackLapsInt / (int(stops[i]) + 1))))

	# Calculate the fuel load for each stint given the above number of stops
	fuelFactor = (-0.000101165467155397 * driverConcentration) + (0.0000706080613787091 * driverAggressiveness) + (
		-0.0000866455021527332 * driverExperience) + (-0.000163915452803369 * driverTechnicalInsight) + (
					 -0.0126912680856842 * carLevelEngine) + (-0.0083557977071091 * carLevelElectronics)
	fuels = []
	for i in range(4):
		fuels.append(
			int(fuelLoadCalc(trackDistanceFloat, float(trackData[trackName][6]), fuelFactor, int(stops[i]) + 1)))
	fuels.append(int(fuelLoadCalc(trackDistanceFloat, float(trackData[trackName][7]), fuelFactor, int(stops[4]) + 1)))

	fuelLoads = []
	fuelLoads.append(str(math.ceil(
		customLapFuelLoadCalc(trackDistanceFloat, float(trackData[trackName][6]), fuelFactor, trackLapsInt,
							  laps))) + " L")
	fuelLoads.append(str(math.floor(
		customLapFuelLoadCalc(trackDistanceFloat, float(trackData[trackName][6]), fuelFactor, trackLapsInt,
							  laps + 1))) + " L")

	# Calculate the pit time for each tyre choice, given the fuel load
	pitTimes = []
	for i in range(5):
		pitTimes.append(round(float(
			pitTimeCalc(int(fuels[i]), technicalDirectorValues[0], technicalDirectorValues[1], staffConcentration,
						technicalDirectorValues[2], staffStress, technicalDirectorValues[3], tdExperience,
						technicalDirectorValues[4], tdPitCoordination, 0)), 2))

	pitTotals = []
	for i in range(4):
		pitTotals.append(round((float(stops[i]) * (float(pitTimes[i]) + float(trackPitInOutFloat))), 2))

	FLDs = []
	for i in range(4):
		FLDs.append(
			round(fuelTimeCalc(trackDistanceFloat, float(trackData[trackName][6]), fuelFactor, stops[i] + 1), 2))
	FLDs.append(round(fuelTimeCalc(trackDistanceFloat, trackData[trackName][7], fuelFactor, stops[4] + 1), 2))

	TCDs = [0, 0, 0, 0, 0]
	TCDs[0] = ("0.00")
	TCDs[1] = (round(compoundCalc(trackLapsInt, float(trackData[trackName][11]), trackLapDistanceFloat, rTemp,
								  tyreCompoundSupplierFactor[tyreSupplierName]), 2))
	TCDs[2] = (float(round(2 * float(TCDs[1]), 2)))
	TCDs[3] = (float(round(3 * float(TCDs[1]), 2)))
	TCDs[4] = ("0.00")

	totals = []
	totals.append(float(round(float(pitTotals[0]) + float(FLDs[0]), 2)))

	if (fuels[4] <= 0):
		fuels[4] = ("No Data!")
		pitTimes[4] = ("No Data!")
		pitTotals.append("No Data!")
		FLDs.append("No Data!")
		for i in range(3):
			totals.append(totalTimeCalc(pitTotals[i + 1], TCDs[i + 1], FLDs[i + 1]))
		totals.append("No Data!")
	else:
		for i in range(3):
			totals.append(totalTimeCalc(float(pitTotals[i + 1]), float(TCDs[i + 1]), float(FLDs[i + 1])))
		pitTotals.append(round((float(stops[4]) * (float(pitTimes[4]))), 2))
		totals.append(totalTimeCalc(float(pitTotals[4]), 0, float(FLDs[4])))

	fastestStrategy = 0

	for i in range(len(totals) - 1):
		if (float(totals[i]) < float(totals[fastestStrategy])):
			fastestStrategy = i

	strategy = [stops, stintlaps, fuels, pitTimes, TCDs, FLDs, pitTotals, totals, fuelLoads, fastestStrategy, trackName,
				trackLaps, trackLapDistance, trackDistance, trackPitInOutFloat]

	return strategy


'''
Pit Stop Calc
trackLapsInt = Track Distance
tracWearLevel = Very Low, Low, Medium, High, Very High, and it's relating factor, 0, 1, 2, 3, 4 respectively
rTemp = Race Temperature
tyreSupplierFactor = Tyre Brand Factor, 1 for Pipirello, 8 for Avonn, etc.
tyreType = Tyre Compound Factor, 0.998163750229071 for Extra Soft (look at wearFactors)
carLevelSuspension = Suspension Level equipped to car
driverAggressiveness = Driver Aggressiveness
driverExperience = Driver Experience
driverWeight = Driver Weight
clearTrackRisk = Clear Track Risk used, as a percentage
trackBaseWear = Track Base Wear from trackData.csv
wearLimit = The manager chosen limit for tyre wear before pitting, so at 10%, we assume the stint will end when the tyres hit 10% wear
'''


# trackLapsInt, trackWearLevel[trackTyreWearRating], rTemp, tyreSupplierFactor[tyreSupplierName], i, carLevelSuspension, driverAggressiveness, driverExperience, driverWeight, float(trackData[trackName][9]), minimumWear, wearFactors[i]
def stopCalc(trackDistanceTotal, trackWearLevel, rTemp, tyreSupplierFactor, tyreType, carLevelSuspension,
			 driverAggressiveness, driverExperience, driverWeight, trackBaseWear, wearLimit, tyreWearFactor, wetFactor):
	baseWear = 129.776458172062
	productFactors = (0.896416176238624 ** trackWearLevel) * (0.988463622 ** rTemp) * (
		1.048876356 ** tyreSupplierFactor) * (1.355293715 ** tyreType) * (1.009339294 ** carLevelSuspension) * (
						 0.999670155 ** driverAggressiveness) * (1.00022936 ** driverExperience) * (
						 0.999858329 ** driverWeight)
	stops = math.ceil((trackDistanceTotal) / (
		(productFactors * baseWear * trackBaseWear * wetFactor) * ((100 - wearLimit) / 100))) - 1
	return stops


'''
Fuel Load Calc
Here we very simply calculate how much fuel we will need across the entire race (distance * fuel per km) then divide by the stints (stops + 1)
'''


def fuelLoadCalc(trackDistanceTotal, trackFuelBase, fuelFactor, stints):
	fuelLoad = math.ceil((trackDistanceTotal * (trackFuelBase + fuelFactor)) / stints)
	return fuelLoad


'''
Same as Fuel Load Calc but for custom stint
'''


def customLapFuelLoadCalc(trackDistanceTotal, trackFuelBase, fuelFactor, trackLapsCount, laps):
	fuelLoad = (laps * (trackDistanceTotal * (trackFuelBase + fuelFactor)) / trackLapsCount)
	return fuelLoad


'''
Pit Time Calc
or how long we'll spend during a single pit stop, which is mainly affected by the fuel load required
i.e. Longer stints mean more fuel but less stops so less overall time
'''


def pitTimeCalc(fuelLoad, tdInfluenceFuel, tdInfluenceStaffConcentration, staffConcentration, tdInfluenceStaffStress,
				staffStress, tdInfluenceExperience, tdExperience, tdInfluencePitCoordination, tdPitCoordination,
				pitInOut):
	return round(((fuelLoad * tdInfluenceFuel) + 24.26 + (tdInfluenceStaffConcentration * staffConcentration) + (
		tdInfluenceStaffStress * staffStress) + (tdInfluenceExperience * tdExperience) + (
					  tdInfluencePitCoordination * tdPitCoordination) + pitInOut), 2)


'''
Fuel Time Calc
Here we calculate how much time is lost by being on the fuel load required to run our choice of tyre.
The idea here is that running longer stints means carrying around more fuel which loses you time.
'''


def fuelTimeCalc(trackLapsCount, trackFuelBase, fuelFactor, stints):
	return (0.0025 * ((trackLapsCount * trackLapsCount * (trackFuelBase + fuelFactor)) / stints))


'''
Compound Time Calc
Here we calculate how much time is lost from being on the compound of choice compared to the extra soft tyre, which is the fastest
The idea is to get a comparison for time lost on the tyre versus time saved in the pits from fewer stops
NOTE: Later I intend to implement some form of "wobble" calculation, which will consider how much time is
lost from being on the tyre of choice for too long.
For example, you might be able to stretch the extra soft tyre to 2 stops, over 3, by running them "bald" for a number of laps
the idea is to take into consideration that time lost, which is roughly 1-2 seconds per lap.
'''


def compoundCalc(trackLapsCount, trackCornerCount, trackDistanceLap, rTemp, tyreCompoundSupplierFactor):
	return (trackLapsCount * (
		(trackCornerCount * trackDistanceLap * 0.00018 * (50 - rTemp)) + tyreCompoundSupplierFactor))


'''
TODO: Total Time Calc
Here we calculate the overall time lost and gained for that tyre strategy.
The reason is so we can compare, say 3 stops on Extra Soft versus 2 stops on Soft.
This is calculated by comparing all the other time saves and losses.
Painfully simple function
'''


def totalTimeCalc(pitTime, compoundTime, fuelTime):
	return round(pitTime + compoundTime + fuelTime, 2)


def profileCalc(partName, partLevel):
	P = H = A = 0
	profile = [P, H, A]

	for i in range(3):
		profile[i] = (partLevel * profileFactors[partName][i])

	return profile


def wearCalc(startWear, partLevel, driverFactor, trackName, clearTrackRisk, i):
	levelFactors = [1.0193, 1.0100, 1.0073, 1.0053, 1.0043, 1.0037, 1.0043, 1.0097, 1.0052]
	return (wearData[trackName][i] * (levelFactors[partLevel - 1] ** clearTrackRisk) * driverFactor)
