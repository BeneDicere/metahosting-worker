import time
from queue_manager import get_message_subject

from config import subscribe
from config import instance_store
from config import instance_type_store


def init():
    log('Init')
    subscribe('info', dispatcher)


def update_instance(instance):
    log('Updating instance %s ' % instance['id'])
    instance['last_info'] = time.time()
    instance_store.update(instance['id'], instance)


def dispatcher(message):
    msg_subject = get_message_subject(message)
    if msg_subject is None:
        print('Invalid message format')
        return

    if msg_subject == 'instance_type':
        register_instance_type(message['class'])
    elif msg_subject == 'instance_info':
        update_instance(instance=message['instance'].copy())
    else:
        log('Unknown message subject: %s' % msg_subject)


def register_instance_type(instance_type):
    if not is_proper_instance_type(instance_type):
        log('Error: invalid instance type = %s' % instance_type)

    name = instance_type['name']
    instance_type['ts'] = time.time()
    log('Registering class: %s' % name)
    instance_type_store.update(name, instance_type)


def is_proper_instance_type(instance_type):
    return 'name' in instance_type


def log(msg):
    print('[%s] %s' % (__name__, msg))