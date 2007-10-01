# Testing and Example script

from sample import *

init_mother('PUT_HERE_YOUR_CONF_FILE')

# Let's create a Sessiona named 'ExampleSession'
ms= MotherSession(name= 'ExampleSession')

try:
 # Insert the Sun Star
 # Sun is created inside our session...
 SunDict= dict(star_name='sun', star_mass=20, star_age=10)
 Sun= ClsStars(SunDict, MO_SAVE, session= ms)

 # Insert two plantes on the solar system...
 EarthDict= dict(planet_name='earth', planet_mass=1)
 MarsDict= dict(planet_name='mars', planet_mass=2)

 # Once more, Sun was created inside the session,
 # so each action is there.
 # Earth and Mars too will be initialized with Sun Session
 Earth= Sun.insertPlanets(EarthDict)
 Mars= Sun.insertPlanets(MarsDict)

 # Take all planets on solar system:
 MyBox= Sun.getMultiplePlanets()
 # Take all planets on solar system with mass > 1:
 MyBox= Sun.getMultiplePlanets(filter= 'planet_mass>1')

 # Create new form of lifes and, at the same time,
 # create a relation with planets to say that a form
 # of life is living on the planet:
 HumanDict=   dict(life_name='humans', life_age= 12)
 MartianDict= dict(life_name='martians')
 MouseDict=  dict(life_name='mouses', life_age= 12)

 # Inside Session, because Earth and Mars are there
 Humans=   Earth.assignLifes(HumanDict, MO_SAVE)
 Martians= Mars.assignLifes(MartianDict, MO_SAVE)
 Mouses=   Earth.assignLifes(MouseDict, MO_SAVE)

 # take all form of lifes living on Earth:
 MyBox= Earth.joinLifes()

 # take all planets with two moons
 MyFilter= dict(num_moons=2)
 MyBox= Sun.getMultiplePlanets(jbuilder= ClsMoons, jfilter= MyFilter)

 # take all planets with humans
 MyFilter= dict(Humans.getFields('life_id'))
 MyBox= Sun.getMultiplePlanets(jbuilder= ClsLifes, jfilter= MyFilter)

# rollback session if some wrongs
except Exception, ss:
    print "Guai!!! ", str(ss)
    ms.rollback()

# Finally, put session inside the pool.
# Note that this produces a commit.
ms.endSession()
