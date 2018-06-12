# -*- coding: UTF-8 -*-
"""
This module contains all the logic for interacting with the vLAN database
"""
import random

import psycopg2
from vlab_api_common import get_logger

from vlab_vlan.lib import const


logger = get_logger(__name__, loglevel=const.VLAB_VLAN_LOG_LEVEL)


def get_db_connection():
    """A connection factory to centralize database connection parameters.

    :Returns: Tuple - (conn, cur)
    """
    conn = psycopg2.connect(database='vlans', host=const.INF_DB_HOSTNAME,
               user='postgres', password=const.POSTGRES_PASSWORD)
    cur = conn.cursor()
    return conn, cur


def register_vlan(username, vlan_name):
    """Create a new record for tracking which vLAN owns which tag id.

    Every vLAN requires a unique vLAN tag in order to maintain network isolation.
    This function guarantees the returned vLAN tag id to be unique, regardless
    of how many callers there are at any time.

    :Returns: Integer

    :Raises: RuntimeError - If no vLANs tags are available

    :Raises: ValueError - If vLAN name is already taken

    :param username: The vLab user who wants to create a new vLAN
    :type username: String

    :param vlan_name: The name of the new vLAN being created
    :type vlan_name: String
    """
    tags_sql = """SELECT all_tags as available_tags FROM \
                  generate_series((SELECT MIN(tag) FROM records), (SELECT MAX(tag) FROM records)) all_tags \
                  EXCEPT \
                  SELECT tag from records;"""
    # Remeber to escape the input to avoid SQL injection
    add_sql = """INSERT INTO records(tag, person, vlan_name) VALUES (%(tag)s, %(person)s, %(vlan_name)s);"""
    lvan_name_exists_sql = """SELECT person, vlan_name, tag FROM records WHERE vlan_name LIKE %s;"""
    add_dict = {'tag': None, 'person': username, 'vlan_name': vlan_name}

    conn, cur = get_db_connection()
    cur.execute(tags_sql)

    available_tags = set([x[0] for x in cur.fetchall()]) # x[0] b/c result is tuple of 1 element
    record_created = False
    while available_tags:
        try:
            # Avoid contention if many users try to create a vlan at the same time
            vlan_tag = random.sample(available_tags, k=1)[0] # k is the number of items to return
            add_dict['tag'] = vlan_tag
            cur.execute(add_sql, add_dict)
        except psycopg2.IntegrityError as doh:
            if doh.pgcode != '23505': # 23505 means unique_violation; vlan already registered
                conn.close()
                raise
            conn.rollback()
            cur.execute(lvan_name_exists_sql, (vlan_name,))
            if cur.rowcount > 0:
                msg = 'vLAN {} already exits'.format(vlan_name)
                logger.error(msg + ': DB results: {}'.format(str(cur.fetchall())))
                conn.close()
                raise ValueError(msg)
            available_tags.remove(vlan_tag) # so we don't try the same tag twice
            continue
        else:
            conn.commit()
            conn.close()
            record_created = True
            break

    if record_created:
        return vlan_tag
    else:
        msg = 'Unable to register vLan; no more tags available'
        raise RuntimeError(msg)


def delete_vlan(vlan_name, username):
    """Remove a vLAN from the database records.

    :Raises: RuntimeError - when multiple vLANs would be deleted

    :Raises: ValueError - when no such vLAN exists

    :param vlan_name: The name of the vLAN to delete
    :type vlan_name: String

    :param username: The vLab user who wants to delete a new vLAN
    :type username: String
    """
    nuke_sql = """DELETE FROM records WHERE vlan_name LIKE %s and person LIKE %s;"""
    conn, cur = get_db_connection()
    try:
        cur.execute(nuke_sql, (vlan_name, username))
        if cur.rowcount == 1:
            conn.commit()
        elif cur.rowcount == 0:
            msg = "No such vLAN: {}".format(vlan_name)
            raise ValueError(msg)
        else:
            msg = 'Expected 1 or zero records, found {}. Owner {}, vLAN name: {}'.format(cur.rowcount, username, vlan_name)
            raise RuntimeError(msg)
    finally:
        conn.close()


def get_vlan(username):
    """Obtain all the different vLANs given person owns. The returned dictionary
    maps the vLAN name to its tag id.

    :Returns: Dictionary

    :param username: The owner of the vLANs
    :type username: String
    """
    # Order of vlan_name, tag matters
    get_sql = """SELECT vlan_name, tag FROM records WHERE person LIKE %s;"""
    conn, cur = get_db_connection()
    try:
        cur.execute(get_sql, (username,))
        # x[0] should be the vlan name, x[1] should be the tag id
        result = {x[0]:x[1] for x in cur.fetchall()}
    finally:
        conn.close()
    return result
