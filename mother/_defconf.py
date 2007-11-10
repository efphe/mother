#
##
### Mother Configuration File
##      -> Commented values are default values <-
#

  #              #
  ###          ### 
  #  MOTHER MAP  #
  ###          ###
  #              #

#
##
# The MotherMap is the file where informations
# about database structure are stored.
# 
# Set here his location: to avoid problems, use
# an absolute path.
#
# Remember to launch mothermapper to create the
# Map file before to using Mother for this 
# environment.
##
#

MOTHER_MAP= '/my/mother/map'


  #                 #
  ##               ##
  ### MOTHER POOL ###
  ##               ##
  #                 #

#
##
# Are you planning to use Mother in a threaded environment?
# For example, for a web application.
#
# If you want to use Mother in a threaded environment,
# you need to use Sessions. To see how, please, refer
# to the official documentation.
#
# In this case, you may want a pool of persistent connections,
# instead of creating a new connection for each session.
# Yes, do it. Set to True the following variable.
##
#

# DB_POOL= False


#
##
# By default, Mother opens a persistent connection outside
# the Pool. This is the persistent connection used when
# the Pool is disabled and is used also when no session is
# specified for db actions. 
#
# If you choose to use the Mother Pool feature (recommended),
# it's possbile to disable this connection by setting the
# following variable to False (recommended).
# If you disable the persistent connection, you *have* to
# work always inside sessions.
#
# Note that the following variable is automatically setted 
# to True when the DB_POOL is disabled.
##
#

# DB_PERSISTENT_ONE = False

#
##
### How many connections in your Pool?
##
# You can specify a min and a max.
# `min' means that the pool will be initialized with
# `min' connections.
#
# When a connection is requested, but no connection
# is availbale, a new connection will be created if 
# `max' connections are not established yet.
# Otherwise, the request will wait until a connection
# will be available.
#
# This is not always True: it depends also on which type
# of pool will be choosed. Anyway, this behaviour is the
# default behaviour. See the next sections.
## 
#

# DB_POOL_MIN= 4
# DB_POOL_MAX= 10

#
##
### Timeout
##
# This is the timeout for the Queue. 
# A request will wait at maximum DB_POOL_TIMEOUT 
# seconds: after that, an exception will be raised.
#
# If DB_POOL_TIMEOUT is set to None, the request 
# blocks until an available connection will be ready.
##
#

# DB_POOL_TIMEOUT= 15


#
##
### Pool Type
##
# Mother supports three different types of pools:
#
#  - DB_POOL_LIMITED
#  - DB_POOL_ELASTIC
#  - DB_POOL_GROWING
#
# The default behaviour (Limited) is already explained: 
# if you like it, just skip this section ;)
#
# When `Limited`, the pool will have a minimum and
# a maximum number of connections. When a connection
# is requested and no connection is available, if the
# number of connection present on the pool is less
# then DB_POOL_MAX, a new connection will be created.
# If the number of connections on the pool is equal to
# DB_POOL_MAX, the request will wait for an available 
# connection at maximum DB_POOL_TIMEOUT seconds.  
# After that, an exception will be raised.
#
# When `Elastic`, each time that a new connection is
# requested and no connection is available, a new 
# connection will be created without limits. When the
# session ends, if the number of connections present
# on the pool is greater then DB_POOL_MIN, the 
# connection will be closed and removed from the pool.
# With `Elastic`, DB_POOL_MAX is ignored (-1).
#
# When `Growing`, each time that a new connection is
# requested and no connection is available, a new
# connection will be created without limits. When the
# session ends, the connection is NOT closed and the
# Pool is greater then before.
# With `Growing`, DB_POOL_MAX is ignored (-1).
#
# Note that, in each case, during the initialization, a
# DB_POOL_MIN number of connections will be established.
##
#

# DB_POOL_TYPE = DB_POOL_LIMITED


#
##
### Pool Patient
##
# A new connection is created when all the connections 
# indide the Pool are employed and the Pool is not full.
#
# By default, the Pool does not wait to create a new
# connection.
#
# If you set the following variable to True, before
# to create a new connection, the Pool will wait at
# maximum DB_POOL_TIMEOUT seconds for an available
# one. After that, if necessary, a new connection is
# created.
## 
#

# DB_POOL_PATIENT= False


#
##
### Default Session name
##
# Each session has a name. If you don't specify
# a session name, Mother assigns a random name
# obtained with the following string, followed by 
# a random integer. 
# If you want, you can decide the prefix that 
# Mother will be use.
#
# Note: the name of sessions is *very* useful 
# when reading logs, so it's a good idea to name
# your sessions.
##
#

# MOTHER_SESSION_NAME = 'MoSession-'



    #           #
    ###       ### 
    #  LOGGING  #
    ###       ###
    #           #

#
## Which prefix for logs output?
#

# LOG_PREFIX= "Mother"

#
## Logging with colors?
# Note: on win32 systems, colors are always 
# disabled. 
##
#

# LOG_COLOR= True

#
##
# LOG_LEVEL 
# 
#  Decreasing:
#
#   - DBG_CRITICAL
#   - DBG_ERROR   
#   - DBG_WARNING 
#   - DBG_INFO    
#   - DBG_INSANE
#   - DBG_NOISE
#   - DBG_SOFT 
#   - DBG_NORMAL
#
# Use DBG_WARNING if you want to see
# only error, warning and critical messages, 
# for example.
#
# To disable logging, use: 
#
#   - DBG_NONE  
##
#

# LOG_LEVEL= DBG_INFO

#
## 
# Log to standard output?
##
#

# LOG_TO_STDOUT= True

#
## 
# Log to file?
# If yes, specify here the file to be used, 
# otherwise set LOG_TO_FILE to None
#
# If enabled, you can use log rotation 
# capability: each LOG_FILE_ROTATE hours,
# the log file will be rotated.
# A LOG_FILE_NUMBER number of files will be
# maintained.
##
#

# LOG_TO_FILE= None

#
## Rotate the log file every day (minutes)
## and maintain logs for a week (days):
#

# LOG_FILE_ROTATE= 60 * 24
# LOG_FILE_NUMBER= 7

#
##  
#  Unix Only
#  Log to Syslog? If yes, which facility? 
#  Note that to use this feature, you have to
#  enable TCP in your syslog configuration.
##
#

# LOG_TO_SYSLOG = False
# LOG_FACILITY  = LOG_USER
# LOG_SERVER    = ('localhost', 514)

#
## 
# Enable SMTP logging?
# If you enable SMTP logging, use Speaker.log_mail()
# to send log strings via mail.
##
#

# LOG_TO_SMTP= False

#
## If LOG_TO_SMTP is True, set the following:
#

# LOG_SMTP_SERVER=  'localhost'
# LOG_SMTP_SENDER=  'debug@debug.debug'
# LOG_SMTP_RCPT=    'destination@debug.debug'
# LOG_SMTP_SUBJECT= 'debug message from Mother'


  #                       #
  ##                     ##
  ### Database Settings ###
  ##                     ##
  #                       #


  #               #
  ##             ##
  ### DB ENGINE ###
  ##             ##
  #               #

#
##
# Mother supports postgres and sqlite db:
#
#   - DB_ENGINE_PGRES
#   - DB_ENGINE_SQLITE
##
#

