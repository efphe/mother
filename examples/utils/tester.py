from sample import *
from mother.speaker import Speaker

use_session= False

# ei, don't pretend order: this is just a test field

init_mother('moconf')
session = use_session and MotherSession('TestSession') or None

Sun= ClsStars({'star_name': 'sun'}, MO_SAVE, session= session)
id_sun= Sun.getField('star_id')
print ' ## Sun inserted with id', id_sun

Sun= ClsStars({'star_id': id_sun}, session= session)
print ' ## Sun name: ', Sun.getField('star_name', autoload= True)
Sun.load()
Sun.setField('star_mass', 12)
Sun.update()
Sun.setFields({'star_mass': 13, 'star_age': 3})
Sun.update()
Sun.delete()

Sun= ClsStars({'star_name': 'sun'}, MO_SAVE, session= session)
id_sun= Sun.getField('star_id')
Sun= ClsStars({'star_id': id_sun}, session= session)
Sun.getFields(Sun.fields, autoload= True)

Alpha= ClsStars({'star_name': 'alpha centauri'}, session= session)
Alpha.insert()

star_box= MotherBox(ClsStars, filter= None, flag= MO_LOAD, session= session)
print ' ## there are %d stars in universe' % len(star_box)

star_box= MotherBox(ClsStars, filter= {'star_name': 'sun'}, flag= MO_LOAD, session= session)
print ' ## there are %d stars in universe with name sun' % len(star_box)

star_box= MotherBox(ClsStars, filter= "star_name != 'sun'", flag= MO_LOAD, session= session)
print ' ## there are %d stars in universe with name != sun' % len(star_box)

star_box= MotherBox(ClsStars, filter= "star_name != 'sun'", flag= MO_DEL, session= session)
star_box= MotherBox(ClsStars, filter= None, flag= MO_LOAD, session= session)
print ' ## there are %d stars in universe' % len(star_box)

Alpha= ClsStars({'star_name': 'alpha centauri'}, session= session)
Alpha.insert()
alpha_id= Alpha.getField('star_id')

MotherBox(ClsStars, filter= None, fields= {'star_mass': 44}, flag= MO_UP, session= session)

Alpha= ClsStars({'star_id': alpha_id}, session= session)
res= Alpha.load(fields= ['star_mass'])
print ' ## Alpha fields: ', res

Earth= Sun.insertPlanets({'planet_name': 'earth', 'planet_mass': 42})
earth_id= Earth.getField('planet_id')
print ' ## Earth inserted with id: ', earth_id

Mars= Sun.insertPlanets({'planet_name': 'mars'})

planet_box = Sun.getMultiplePlanets()
print ' ## there are %d planets on the solar system' % len(planet_box)

planet_box= Sun.getMultiplePlanets(filter= {'planet_name': 'mars'}, order = ['planet_id'])
print ' ## there are %d planets on the solar system named mars' % len(planet_box)

try:
  planet= Sun.getPlanets({'planet_name': 'earth'})
except:
  print " ## No planet on the solar system with name earth"

Sun.updateMultiplePlanets({'planet_mass': 23})
Sun.updateMultiplePlanets({'planet_mass': 77}, filter= "planet_name = 'mars'")
Sun.updateMultiplePlanets({'planet_mass': 99}, filter= {'planet_name': 'earth'})

Sun.deleteMultiplePlanets(filter= "planet_name = 'mars'")
Sun.deleteMultiplePlanets(filter= {'planet_name': 'earth'})

Earth= Sun.insertPlanets({'planet_name': 'earth', 'planet_mass': 42})
Mars= Sun.insertPlanets({'planet_name': 'mars'})

GreenPeople= Mars.assignLifes({'life_name': 'green people'}, MO_SAVE)
green_id= GreenPeople.getField('life_id')
print ' ## inserted green people with id: ', green_id

params= Mars.paramsLifes(GreenPeople)
print ' ## relation between mars and green people: ', params

Worms = Mars.assignLifes({'life_name': 'worms'}, MO_SAVE, params= {'age': 22})
params= Mars.paramsLifes(Worms.getFields())
print ' ## relation between mars and worms: ', params

mars_lifes= Mars.joinLifes(fields= ['life_name', 'life_id'])
for m in mars_lifes.getRecords(flag_obj= True):
    print ' ## On mars %s lives' % m.getField('life_name')

mars_lifes= Mars.joinLifes(fields= ['life_name'], jfilter= {'life_name': 'worms'}, filter= {'age': 22})
print ' ## there are %d lifes on mars named worms, age 22' % len(mars_lifes)

Mars.dropMultipleLifes(jfilter= {'life_name': 'worms'}, filter= {'age': 22}, flag= MO_DEL)
Mars.dropMultipleLifes(jfilter= {'life_name': 'green people'}, flag= MO_NOA)
Mars.assignLifes({'life_id': green_id})

lifes= MotherBox(ClsLifes, filter= None, flag= MO_LOAD, session = session)
print ' ## There are %d lifes on universe' % len(lifes)

marsmoons= Mars.insertMoonsInfo({'num_moons': 3})
earthmoons= Earth.insertMoonsInfo({'num_moons': 1})

box= Sun.getMultiplePlanets(jbuilder= ClsMoon, jfilter= {'num_moons': 3})
print ' ## there are %d planets on the solar system with 3 moons' % len(box)

box= Sun.getMultiplePlanets(filter= "planet_name != 'rere'", jbuilder= ClsMoon, jfilter= {'num_moons': 3})
print ' ## there are %d planets not named rere on the solar system with 3 moons' % len(box)

box= Sun.getMultiplePlanets(fields= ['planet_name'], filter= {"planet_name": 'rere'}, jbuilder= ClsMoon, jfilter= {'num_moons': 3})
print ' ## there are %d planets named rere on the solar system with 3 moons' % len(box)

box= Sun.getMultiplePlanets(jbuilder= ClsLifes, jfilter= {'life_id': green_id})
print ' ## there are %d planets on the solar system where green people lives' % len(box)

box= Sun.getMultiplePlanets(filter= "planet_name != 'rere'", jbuilder= ClsLifes, jfilter= {'life_id': green_id})
print ' ## there are %d planets not named rere on the solar system where green people lives' % len(box)

box= Sun.getMultiplePlanets(fields= ['planet_name'], filter= {"planet_name": 'rere'}, jbuilder= ClsLifes, jfilter= {'life_id': green_id})
print ' ## there are %d planets named rere on the solar system where green lives' % len(box)

if session:
    session.endSession()
