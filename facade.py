import logging
import uuid
from stores import instance_store, type_store
from queue_managers import send_message


def get_types():
    return type_store.get_all()


def create_instance(instance_type):
    types = get_types()
    if instance_type not in types:
        logging.debug('Unknown instance type: %s', instance_type)

    logging.debug('Creating instance for: %s', instance_type)
    instance = dict()
    instance['id'] = generate_id()
    instance['status'] = 'starting'
    instance['type'] = instance_type
    send_message(instance_type, 'create_instance', instance)
    send_message('info', 'instance_info', {'instance': instance})
    return instance


def delete_instance(instance_id):
    try:
        instance = get_instance(instance_id)[1]
    except TypeError as err:
        logging.error('Instance not in local store, therefore not deleting it'+err.message)
        return None
    logging.debug('Schedule deleting of %s' % instance_id)
    instance['status'] = 'deleting'
    send_message(instance['type'], 'delete_instance', instance)
    send_message('info', 'instance_info', {'instance': instance})
    return instance


def get_instance(instance_id):
    return instance_store.get(instance_id)


def get_all_instances():
    return instance_store.get_all()


def get_instances_of_type(instance_type_name):
    return {iid: desc for iid, desc in get_all_instances().iteritems() if
            desc['type'] == instance_type_name}


def generate_id():
    return uuid.uuid1().hex
