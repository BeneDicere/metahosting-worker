import uuid
from config import instance_type_store
from config import send_message
from config import instance_store


def get_instance_types():
    return instance_type_store.get_all()


def create_instance(instance_type_name):
    instance_types = get_instance_types()
    if instance_type_name not in instance_types:
        log('Unknown instance type: ' % instance_type_name)

    log('Creating instance for %s' % instance_type_name)
    instance = dict()
    instance['id'] = generate_id()
    instance['status'] = 'starting'
    instance['class'] = instance_types[instance_type_name]
    send_message(instance_type_name, 'create_instance', instance)
    send_message('info', 'instance_info', {'instance': instance})
    return instance


def get_all_instances():
    return instance_store.get_all()


# client method
def get_instance(instance_id):
    return instance_store.get(instance_id)


def generate_id():
    return uuid.uuid1().hex


def log(msg):
    print('[%s] %s' % (__name__, msg))


def get_instances_of_type(instance_type_name):
    def filter_function(x):
        return x[1]['class']['name'] == instance_type_name
    return filter(filter_function, get_all_instances().iteritems())
