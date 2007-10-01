  #               #
  ##             ##
  ### DB ENGINE ###
  ##             ##
  #               #

#
##
# Mother supports different db:
#
#   - DB_ENGINE_PGRES
#   - DB_ENGINE_SQLITE
##
#

DB_ENGINE= DB_ENGINE_PGRES

#
##  Postgresql Oids
#
# By default, Mother uses OIDs.
# This will be changed when postgres-8.2.3 will be the 
# most diffused version of postgres.
#
# OIDs have been deprecated with postgres-8.1, but 
# they are completely working and supported.
#
# Anyway, it's possible to avoid OIDs, but to do that
# a postgres version >= 8.2.3 is needed.
#
# If you run a postgres version >= 8.2.3, set the 
# following to False. It's all.
#
# If you run a version < 8.1, use True. It's all.
#
# Otherwise, you HAVE to set the following to True
# and your tables have to be created WITH OIDS:
#
#   CREATE TABLE my_table ( ... ) WITH OIDS;
#
# If you decide to upgrade postgres to 8.2.3, it's 
# safe to change this switch to False.
# If you decide to upgrade to 8.1, make sure that 
# your tables use OIDs.
#
# If you use a postgres version < 8.2.3 and you don't
# want to use OIDs, choose another ORM, but forget
# the Mother introspection ;)
##
#

# MOTHER_OIDS= True

#
## DB info
#
# If DB_HOST is None, Unix Sockets will be used (Unix only)
# In this case, DB_PORT is ignored.
##
#

DB_HOST= 'localhost'
DB_NAME= "universe"
DB_USER= "space_man"
DB_PASSWD= "space_password"
# DB_PORT= 5432

  
