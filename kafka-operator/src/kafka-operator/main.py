import asyncio
import kopf
import pykube
import yaml
from confluent_kafka.admin import (AdminClient, NewTopic, NewPartitions, ConfigResource, ConfigSource) 
from confluent_kafka import KafkaException

@kopf.on.startup()
async def startup_fn_simple(logger, **kwargs):
    logger.info('Starting in 1s...')
    await asyncio.sleep(1)

@kopf.on.create('topics')
def create_1(body, meta, spec, status, **kwargs):
    t = createTopic(body)

    kopf.info(body, reason='AnyReason')
    kopf.event(body, type='Warning', reason='SomeReason', message="Cannot do something")
    kopf.event(t, type='Normal', reason='SomeReason', message="Created as part of the job1step")

    return {'topic-status': t}

def createTopic(body):
  conf = {'bootstrap.servers':  body['spec']['kafkaServer'], 'sasl.mechanism': 'SCRAM-SHA-512', 'sasl.username': 'admin', 'sasl.password': 'mypassword', 'security.protocol': 'sasl_ssl'}
  adm = AdminClient(conf)
  newTopic = adm.create_topics([NewTopic(body['spec']['topicName'], num_partitions=3, replication_factor=1)])
  for topic, f in newTopic.items():
    try:
      f.result()
      print("Topic {} created".format(topic))
    except Exception as e:
      print("Failed to create topic {}: {}".format(topic, e))
