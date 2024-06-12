#!/usr/bin/env bash


zkServer.sh start &
zkCli.sh &
storm nimbus &
storm ui &
storm supervisor 
