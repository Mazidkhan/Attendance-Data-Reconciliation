from schema import Schema, Use, And, Optional

incoming_command_schema_1 = Schema([{
    'subscribeFrom': [{
        'topic': And(str, Use(lambda s: s.lower())),
        'publishType': And(str, Use(lambda s: s.upper()), lambda s: s in ('BROADCAST', 'ONE_TO_ONE')),
        'description': And(str),
        'responseAt': And(str, Use(lambda s: s.lower())),
        'heartbeat': And(str, Use(lambda s: s.lower()))
    }]
}])

# {
#     'identifier': 'alarm_annunciator',
#     'command':{
#         'status': 'ON',
#         'value': '0'
#     }
# }

incoming_command_schema = Schema({
    'name': And(Use(str)),
    'key': And(Use(str)),
    'command': {
        'identifier': And(Use(str)),
        'status': And(str, Use(lambda s: s.upper()), lambda s: s in ('ON', 'OFF', 'VALUE')),
        'value': And(str, Use(lambda s: s.lower())),
    },
    'alertMessage': {
        'code': And(Use(str)),
        'status': And(str, Use(lambda s: s.upper()), lambda s: s in ('ACTIVE', 'INACTIVE')),
        'message': And(Use(str)),
    },
    'data': {
        'nodeId': And(Use(int)),
        'n': And(Use(str)),
        'pv': And(Use(float)),
        'datetime': And(Use(int)),
        'dataQualifier': And(Use(str))
    }

})

