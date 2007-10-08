from mother.mothers import *

class ClsLifeforms(DbMother):
    table_name= 'lifeforms'
    def __init__(self, store= {}, flag= MO_NOA, session= None):
        DbMother.__init__(self, store, flag, session)

class ClsMoons(DbMother):
    table_name= 'moons_info'
    def __init__(self, store= {}, flag= MO_NOA, session= None):
        DbMother.__init__(self, store, flag, session)

class ClsPlanets(DbMother, MotherManager):
    table_name= 'planets'
    def __init__(self, store= {}, flag= MO_NOA, session= None):
        self.initRelationManager([ClsLifeforms])
        self.initChildManager([ClsMoons])
        DbMother.__init__(self, store, flag, session)

class ClsStars(DbMother, MotherManager):
    table_name= 'stars'
    def __init__(self, store= {}, flag= MO_NOA, session= None):
        self.initChildManager([ClsPlanets])
        DbMother.__init__(self, store, flag, session)
