#coding: utf-8
from youey import *

from carnet_login import *

from types import SimpleNamespace
  
#View.default_theme = Theme(Grey1, Dark)

class DashboardApp(App):
  
  def __init__(self, car_data, **kwargs):
    self.car_data = car_data
    super().__init__(**kwargs)
  
  def setup(self):
    scrollview
    nav = NavigationView(self, title='ZLO', icon='solid:car')#, flow_direction=HORIZONTAL, spread=True)
    
    ImageView(nav.container, image='vw-model-egolf.png').dock_all().left=Width(nav.container, .2)
    
    semi_transparent_bg = Color(nav.theme.background, alpha=0.7)
    almost_opaque_bg = Color(nav.theme.background, alpha=0.8)
    
    
    container = ContainerView(nav.container, flow_direction=HORIZONTAL, spread=True, background_color=semi_transparent_bg).dock_all()
    
    self.car_data = CarData()
    
    dummy_values = {
      'celcius': 10,
      'externalPowerSupplyState': 'unavailable',
      'stateOfCharge': 89,
      'primaryEngineRange': 220,
      'climateHeatingStatus': 'on',
      'mileage': 21345,
      'climateHeatingWindowFrontStatus': 'off',
      'climateHeatingWindowRearStatus': 'off'
    }
    #self.car_data = SimpleNamespace(**dummy_values)
    
    cards = [
      ('Lämpötila', 'solid:cloud-sun', str(round(self.car_data.celcius)), '°C'),
      ('Lataus', 'solid:plug' if self.car_data.externalPowerSupplyState == 'available' else 'solid:car-battery', str(self.car_data.stateOfCharge), '%'), ('Matka', 'solid:charging-station', str(self.car_data.primaryEngineRange), 'KM'), ('Lämmitys', 'solid:thermometer-half', self.car_data.climateHeatingStatus, ''), ('Lukitus', 'solid:unlock', self.car_data.mileage, 'KM'), ('Ikkunat', 'solid:snowflake.svg', self.car_data.climateHeatingWindowFrontStatus + '\n\n' + self.car_data.climateHeatingWindowRearStatus, '') ]
    
    for i, (title, icon, data, unit) in enumerate(cards):
      card = StyledCardView(container, 
        width=Width(container, lambda: 1/2 if container.is_portrait else 1/3, offset=-10),
        height=Height(container, lambda: 1/3 if container.is_portrait else 1/2, offset=-10),
        background_color=almost_opaque_bg)
      
      card_caption = LabelView(card, 
        text=title.upper(), 
        font=card.theme.caption_1,
        text_color=card.theme.on_surface,
        text_align=RIGHT,
        padding=(5, 10)
      ).dock_bottom()
      
      card_icon = ImageView(card,
        image=icon,
        fill=card.theme.variant,
        middle=Height(card, .5),
        center=Width(card, .25),
        height=Height(card, .4),
        width=Height(card, .4),
      )
      
      card_text = LabelView(card, 
        text=str(data).upper(),
        font=card.theme.title_1,
        text_color=card.theme.primary,
        text_align=RIGHT,
        padding=(0,30),
        right=0,
        middle=Height(card, .5),
      )
      
      unit_text = LabelView(card,
        text=unit,
        font=card.theme.caption_1,
        text_color=card.theme.on_surface,
        text_align=RIGHT,
        padding=(0,30),
        top=Bottom(card_text),
        right=0
      )
      
      
import sys
import requests
import json

class CarData():

  # Fake the VW CarNet mobile app headers
  HEADERS = { 'Accept': 'application/json', 'X-App-Name': 'eRemote', 'X-App-Version': '1.0.0', 'User-Agent': 'okhttp/2.3.0' }

  def __init__(self):
    self.carNetLogon()
    self.retrieveCarNetInfo()

  def carNetLogon(self):
    global CARNET_USERNAME, CARNET_PASSWORD
    r = requests.post('https://msg.volkswagen.de/fs-car/core/auth/v1/VW/DE/token', data = { 'grant_type':'password', 
      'username':CARNET_USERNAME,
      'password':CARNET_PASSWORD
    }, headers=self.HEADERS)
    responseData = json.loads(r.content)
    token = responseData.get("access_token")
    self.HEADERS["Authorization"] = "AudiAuth 1 " + token
  
  def retrieveCarNetInfo(self):
    global VIN
    r = requests.get('https://msg.volkswagen.de/fs-car/bs/cf/v1/VW/DE/vehicles/' + VIN + '/position', headers=self.HEADERS)
    #print "Position request: " + r.content
    responseData = json.loads(r.content)
    carPosition = responseData.get("findCarResponse").get("Position").get("carCoordinate")
    latReversed = str(carPosition.get("latitude"))[::-1]
    lonReversed = str(carPosition.get("longitude"))[::-1]
    self.lat = latReversed[:6] + "." + latReversed[6:]
    self.lon = lonReversed[:6] + "." + lonReversed[6:]
    self.timeStampCarSend = responseData.get("findCarResponse").get("Position").get("timestampCarSent")
  
    # Retrieve car counter
    r = requests.get('https://msg.volkswagen.de/fs-car/bs/vsr/v1/VW/DE/vehicles/' + VIN + '/status', headers=self.HEADERS)
    #print "Vehicle request: " + r.content
    responseData = json.loads(r.content)
    try: self.mileage = responseData.get("StoredVehicleDataResponse").get("vehicleData").get("data")[1].get("field")[0].get("value")
    except: self.mileage = 0
  
    try: self.serviceInKm = responseData.get("StoredVehicleDataResponse").get("vehicleData").get("data")[2].get("field")[2].get("value")
    except: self.serviceInKm = 0
    self.serviceInKm = (self.serviceInKm * -1)
  
    try: self.serviceInDays = responseData.get("StoredVehicleDataResponse").get("vehicleData").get("data")[2].get("field")[3].get("value")
    except: self.serviceInDays = 0
    self.serviceInDays = (self.serviceInDays * -1)
  
    try: parkingLight = responseData.get("StoredVehicleDataResponse").get("vehicleData").get("data")[3].get("field")[0].get("value")
    except: parkingLight = 0
    if (parkingLight == 3):
      self.parkingLight = "left=on, right=off"
    elif (parkingLight == 4):
      self.parkingLight = "left=off, right=on"
    elif (parkingLight == 5):
      self.parkingLight = "left=on, right=on"
    else:
      self.parkingLight = "left=off, right=off"
  
    # Retrieve car temperature
    r = requests.get('https://msg.volkswagen.de/fs-car/bs/climatisation/v1/VW/DE/vehicles/' + VIN + '/climater', headers=self.HEADERS)
    #print "Climate request: " + r.content
    responseData = json.loads(r.content)
    carTemp = responseData.get("climater").get("status").get("temperatureStatusData").get("outdoorTemperature").get("content")
    carTempDot = str(carTemp)[:3] + "." + str(carTemp)[3:]
    self.celcius = float(carTempDot)-273
    self.climateHeatingStatus = responseData.get("climater").get("status").get("climatisationStatusData").get("climatisationState").get("content")
    self.climateHeatingWindowFrontStatus = responseData.get("climater").get("status").get("windowHeatingStatusData").get("windowHeatingStateFront").get("content")
    self.climateHeatingWindowRearStatus = responseData.get("climater").get("status").get("windowHeatingStatusData").get("windowHeatingStateRear").get("content")
  
    r = requests.get('https://msg.volkswagen.de/fs-car/bs/batterycharge/v1/VW/DE/vehicles/' + VIN + '/charger', headers=self.HEADERS)
    #print "Charger request: " + r.content
    responseData = json.loads(r.content)
    self.chargingMode = responseData.get("charger").get("status").get("chargingStatusData").get("chargingMode").get("content")
    self.chargingReason = responseData.get("charger").get("status").get("chargingStatusData").get("chargingReason").get("content")
    self.externalPowerSupplyState = responseData.get("charger").get("status").get("chargingStatusData").get("externalPowerSupplyState").get("content")
    self.energyFlow = responseData.get("charger").get("status").get("chargingStatusData").get("energyFlow").get("content")
    self.chargingState = responseData.get("charger").get("status").get("chargingStatusData").get("chargingState").get("content")
  
    self.stateOfCharge = responseData.get("charger").get("status").get("batteryStatusData").get("stateOfCharge").get("content")
    self.remainingChargingTime = responseData.get("charger").get("status").get("batteryStatusData").get("remainingChargingTime").get("content")
    self.remainingChargingTimeTargetSOC = responseData.get("charger").get("status").get("batteryStatusData").get("remainingChargingTimeTargetSOC").get("content")
  
    self.primaryEngineRange = responseData.get("charger").get("status").get("cruisingRangeStatusData").get("primaryEngineRange").get("content")
      
#car_data = CarData()

app = DashboardApp(None)
