# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: descarteslabs/common/proto/workflow/workflow.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from descarteslabs.common.proto.types import types_pb2 as descarteslabs_dot_common_dot_proto_dot_types_dot_types__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='descarteslabs/common/proto/workflow/workflow.proto',
  package='descarteslabs.workflows',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n2descarteslabs/common/proto/workflow/workflow.proto\x12\x17\x64\x65scarteslabs.workflows\x1a,descarteslabs/common/proto/types/types.proto\"\xff\x02\n\x08Workflow\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12+\n\x11\x63reated_timestamp\x18\x02 \x01(\x03R\x10\x63reatedTimestamp\x12+\n\x11updated_timestamp\x18\x03 \x01(\x03R\x10updatedTimestamp\x12\x12\n\x04name\x18\x07 \x01(\tR\x04name\x12 \n\x0b\x64\x65scription\x18\x08 \x01(\tR\x0b\x64\x65scription\x12\x37\n\x04type\x18\t \x01(\x0e\x32#.descarteslabs.workflows.ResultTypeR\x04type\x12\x18\n\x07\x63hannel\x18\n \x01(\tR\x07\x63hannel\x12)\n\x10serialized_graft\x18\x15 \x01(\tR\x0fserializedGraft\x12/\n\x13serialized_typespec\x18\x16 \x01(\tR\x12serializedTypespec\x12\x12\n\x04user\x18\x17 \x01(\tR\x04user\x12\x10\n\x03org\x18\x18 \x01(\tR\x03org\"V\n\x15\x43reateWorkflowRequest\x12=\n\x08workflow\x18\x01 \x01(\x0b\x32!.descarteslabs.workflows.WorkflowR\x08workflow\"$\n\x12GetWorkflowRequest\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\"V\n\x15UpdateWorkflowRequest\x12=\n\x08workflow\x18\x01 \x01(\x0b\x32!.descarteslabs.workflows.WorkflowR\x08workflow\"`\n\x14ListWorkflowsRequest\x12%\n\x0estart_datetime\x18\x01 \x01(\tR\rstartDatetime\x12!\n\x0c\x65nd_datetime\x18\x02 \x01(\tR\x0b\x65ndDatetime2\xa3\x03\n\x0bWorkflowAPI\x12\x65\n\x0e\x43reateWorkflow\x12..descarteslabs.workflows.CreateWorkflowRequest\x1a!.descarteslabs.workflows.Workflow\"\x00\x12\x65\n\rListWorkflows\x12-.descarteslabs.workflows.ListWorkflowsRequest\x1a!.descarteslabs.workflows.Workflow\"\x00\x30\x01\x12_\n\x0bGetWorkflow\x12+.descarteslabs.workflows.GetWorkflowRequest\x1a!.descarteslabs.workflows.Workflow\"\x00\x12\x65\n\x0eUpdateWorkflow\x12..descarteslabs.workflows.UpdateWorkflowRequest\x1a!.descarteslabs.workflows.Workflow\"\x00\x62\x06proto3'
  ,
  dependencies=[descarteslabs_dot_common_dot_proto_dot_types_dot_types__pb2.DESCRIPTOR,])




_WORKFLOW = _descriptor.Descriptor(
  name='Workflow',
  full_name='descarteslabs.workflows.Workflow',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='descarteslabs.workflows.Workflow.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='id', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_timestamp', full_name='descarteslabs.workflows.Workflow.created_timestamp', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='createdTimestamp', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='updated_timestamp', full_name='descarteslabs.workflows.Workflow.updated_timestamp', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='updatedTimestamp', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='descarteslabs.workflows.Workflow.name', index=3,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='name', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='descarteslabs.workflows.Workflow.description', index=4,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='description', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='type', full_name='descarteslabs.workflows.Workflow.type', index=5,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='type', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='channel', full_name='descarteslabs.workflows.Workflow.channel', index=6,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='channel', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='serialized_graft', full_name='descarteslabs.workflows.Workflow.serialized_graft', index=7,
      number=21, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='serializedGraft', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='serialized_typespec', full_name='descarteslabs.workflows.Workflow.serialized_typespec', index=8,
      number=22, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='serializedTypespec', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='user', full_name='descarteslabs.workflows.Workflow.user', index=9,
      number=23, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='user', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='org', full_name='descarteslabs.workflows.Workflow.org', index=10,
      number=24, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='org', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=126,
  serialized_end=509,
)


_CREATEWORKFLOWREQUEST = _descriptor.Descriptor(
  name='CreateWorkflowRequest',
  full_name='descarteslabs.workflows.CreateWorkflowRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='workflow', full_name='descarteslabs.workflows.CreateWorkflowRequest.workflow', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='workflow', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=511,
  serialized_end=597,
)


_GETWORKFLOWREQUEST = _descriptor.Descriptor(
  name='GetWorkflowRequest',
  full_name='descarteslabs.workflows.GetWorkflowRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='descarteslabs.workflows.GetWorkflowRequest.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='id', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=599,
  serialized_end=635,
)


_UPDATEWORKFLOWREQUEST = _descriptor.Descriptor(
  name='UpdateWorkflowRequest',
  full_name='descarteslabs.workflows.UpdateWorkflowRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='workflow', full_name='descarteslabs.workflows.UpdateWorkflowRequest.workflow', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='workflow', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=637,
  serialized_end=723,
)


_LISTWORKFLOWSREQUEST = _descriptor.Descriptor(
  name='ListWorkflowsRequest',
  full_name='descarteslabs.workflows.ListWorkflowsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='start_datetime', full_name='descarteslabs.workflows.ListWorkflowsRequest.start_datetime', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='startDatetime', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='end_datetime', full_name='descarteslabs.workflows.ListWorkflowsRequest.end_datetime', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, json_name='endDatetime', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=725,
  serialized_end=821,
)

_WORKFLOW.fields_by_name['type'].enum_type = descarteslabs_dot_common_dot_proto_dot_types_dot_types__pb2._RESULTTYPE
_CREATEWORKFLOWREQUEST.fields_by_name['workflow'].message_type = _WORKFLOW
_UPDATEWORKFLOWREQUEST.fields_by_name['workflow'].message_type = _WORKFLOW
DESCRIPTOR.message_types_by_name['Workflow'] = _WORKFLOW
DESCRIPTOR.message_types_by_name['CreateWorkflowRequest'] = _CREATEWORKFLOWREQUEST
DESCRIPTOR.message_types_by_name['GetWorkflowRequest'] = _GETWORKFLOWREQUEST
DESCRIPTOR.message_types_by_name['UpdateWorkflowRequest'] = _UPDATEWORKFLOWREQUEST
DESCRIPTOR.message_types_by_name['ListWorkflowsRequest'] = _LISTWORKFLOWSREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Workflow = _reflection.GeneratedProtocolMessageType('Workflow', (_message.Message,), {
  'DESCRIPTOR' : _WORKFLOW,
  '__module__' : 'descarteslabs.common.proto.workflow.workflow_pb2'
  # @@protoc_insertion_point(class_scope:descarteslabs.workflows.Workflow)
  })
_sym_db.RegisterMessage(Workflow)

CreateWorkflowRequest = _reflection.GeneratedProtocolMessageType('CreateWorkflowRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEWORKFLOWREQUEST,
  '__module__' : 'descarteslabs.common.proto.workflow.workflow_pb2'
  # @@protoc_insertion_point(class_scope:descarteslabs.workflows.CreateWorkflowRequest)
  })
_sym_db.RegisterMessage(CreateWorkflowRequest)

GetWorkflowRequest = _reflection.GeneratedProtocolMessageType('GetWorkflowRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETWORKFLOWREQUEST,
  '__module__' : 'descarteslabs.common.proto.workflow.workflow_pb2'
  # @@protoc_insertion_point(class_scope:descarteslabs.workflows.GetWorkflowRequest)
  })
_sym_db.RegisterMessage(GetWorkflowRequest)

UpdateWorkflowRequest = _reflection.GeneratedProtocolMessageType('UpdateWorkflowRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEWORKFLOWREQUEST,
  '__module__' : 'descarteslabs.common.proto.workflow.workflow_pb2'
  # @@protoc_insertion_point(class_scope:descarteslabs.workflows.UpdateWorkflowRequest)
  })
_sym_db.RegisterMessage(UpdateWorkflowRequest)

ListWorkflowsRequest = _reflection.GeneratedProtocolMessageType('ListWorkflowsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTWORKFLOWSREQUEST,
  '__module__' : 'descarteslabs.common.proto.workflow.workflow_pb2'
  # @@protoc_insertion_point(class_scope:descarteslabs.workflows.ListWorkflowsRequest)
  })
_sym_db.RegisterMessage(ListWorkflowsRequest)



_WORKFLOWAPI = _descriptor.ServiceDescriptor(
  name='WorkflowAPI',
  full_name='descarteslabs.workflows.WorkflowAPI',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=824,
  serialized_end=1243,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateWorkflow',
    full_name='descarteslabs.workflows.WorkflowAPI.CreateWorkflow',
    index=0,
    containing_service=None,
    input_type=_CREATEWORKFLOWREQUEST,
    output_type=_WORKFLOW,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='ListWorkflows',
    full_name='descarteslabs.workflows.WorkflowAPI.ListWorkflows',
    index=1,
    containing_service=None,
    input_type=_LISTWORKFLOWSREQUEST,
    output_type=_WORKFLOW,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetWorkflow',
    full_name='descarteslabs.workflows.WorkflowAPI.GetWorkflow',
    index=2,
    containing_service=None,
    input_type=_GETWORKFLOWREQUEST,
    output_type=_WORKFLOW,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateWorkflow',
    full_name='descarteslabs.workflows.WorkflowAPI.UpdateWorkflow',
    index=3,
    containing_service=None,
    input_type=_UPDATEWORKFLOWREQUEST,
    output_type=_WORKFLOW,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_WORKFLOWAPI)

DESCRIPTOR.services_by_name['WorkflowAPI'] = _WORKFLOWAPI

# @@protoc_insertion_point(module_scope)
