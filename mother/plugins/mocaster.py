""" Form And Fields Adaption

MotherCaster is a MotherPlugin that controls fields types and, 
optionally, required fields.

To use this plugin, you have to subclass your Mother class with 
MotherCaster and you have to define a dictionnary for fieds types.

Example:

  # Begin Code
  ClsStars(DbMother, MotherCaster):
      self.cast_fields = {star_mass: int}
      # and optionally:
      self.required_fields= ['star_age']

      def __init__(self, d, flag, session):
          MotherCaster.__init__(self, autocast= True)
          DbMother.__init__(self, d, flag, session)
  # End Code

Fields with wrong types are casted (if possible).
If you don't like that, turn off autocast.

The dict to initialize Mother must have all fields listed on 
required_fields (if specified).

On errors, a MoWrongFields is raised. 

  try:
    Sun= ClsStars(MyDict, MO_SAVE)
  except MoWrongFields, wrongs:
    print wrongs.ifields
    print wrongs.mfields

where wrong.ifields means invalid fields (not castable) and
wrong.mfields means missing fields (required but not present).

    """



class MoWrongFields(Exception):
    def __init__(self, ifields, mfields):
        self.ifields = ifields
        self.mfields = mfields
    def __str__(self):
        l= self.ifields + self.mfields
        return ','.join([str(k) for k in l])


class MotherCaster:

    def __init__(self, autocast= True):

        self._motherInitStore= self._initStore
        self._initStore= self._casterInitStore
        self._autocast= autocast

        if not hasattr(self, 'required_fields'):
            self.required_fields= []

    def _casterInitStore(self, store, flag):

        newstore= {}
        ifields= []

        for k, v in store.iteritems():

            if k not in self.fields:
                continue

            if k not in self.cast_fields:
                newstore[k]= v
                continue

            t= self.cast_fields[k]
            if not isinstance(v, t):

                if not self.autocast:
                    ifields.append(k)
                    continue

                try:
                    newv= t(v)
                except:
                    ifields.append(k)

            else:
                newv= v
            
            newstore[k]= newv

        mfields= set(self.required_fields) - set(newstore)

        if mfields or ifields:
            raise MoWrongFields(ifields, list(mfields))

        return self._motherInitStore(newstore, flag)


