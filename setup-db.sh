#!/bin/sh
set -e

# Create the database
psql -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE DATABASE vlans;
EOSQL

# Populate the schema and min/max vlan Ids
psql -v ON_ERROR_STOP=1 --username ${POSTGRES_USER} --dbname vlans <<-EOSQL
  CREATE TABLE records(
    tag INT PRIMARY KEY NOT NULL,
    person  TEXT NOT NULL,
    vlan_name TEXT NOT NULL
  );

  CREATE UNIQUE INDEX vlan_names
    on records (vlan_name)
  ;

  INSERT INTO records(tag, person, vlan_name)
  VALUES
  (${VLAB_VLAN_ID_MIN}, 'noone', 'noone_min'),
  (${VLAB_VLAN_ID_MAX}, 'noone', 'noone_max')
  ;
EOSQL
