#!/bin/bash
# mongo database upgrade 
export PATH=$PATH:$MONGO_HOME/bin
export MONGO_HOST=$1
export MONGO_PORT=$2
export MONGO_USER=$3
export MONGO_PWD=$4
export AUTH_DB=$5
export DATA_BASE=$6
export FUNC_SWITCH=$7

versions=(R1.8.0)

if [ -z "$MONGO_HOST" ]
then
	echo "set the MONGO_HOST path"
	exit
fi

if [ -z "$MONGO_PORT" ]
then
	echo "set the MONGO_PORT path"
	exit
fi

if [ -z "$MONGO_USER" ]
then
	echo "set the MONGO_USER"
	exit
fi

if [ -z "$MONGO_PWD" ]
then
	echo "set the MONGO_PWD"
	exit
fi

if [ -z "$AUTH_DB" ]
then
	echo "set the AUTH_DB name"
	exit
fi

if [ -z "$DATA_BASE" ]
then
	echo "set the DATA_BASE name"
	exit
fi

if [ -z "$FUNC_SWITCH" ]
then
	echo "set the FUNC_SWITCH:example sourceid"
	exit
fi

for (( i = 0 ; i < ${#versions[@]} ; i++ ))
do
mongo $MONGO_HOST:$MONGO_PORT -u $MONGO_USER -p $MONGO_PWD --authenticationDatabase ${AUTH_DB} --quiet ./${DATA_BASE}_${FUNC_SWITCH}_upgrade_db/sourceid/${versions[$j]}/*.js
done

