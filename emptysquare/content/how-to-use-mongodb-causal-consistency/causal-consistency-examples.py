import logging

from pymongo import MongoClient, ReadPreference, monitoring
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

logging.basicConfig(level=logging.INFO)


class Logger(monitoring.CommandListener):
    def started(self, event: monitoring.CommandStartedEvent) -> None:
        logging.info(
            f"{event.command_name} with request id "
            f"{event.request_id} started on port "
            f"{event.connection_id[1]}: "
            f"{event.command}"
        )

    def succeeded(self, event: monitoring.CommandSucceededEvent) -> None:
        logging.info(
            f"{event.command_name} reply with request id "
            f"{event.request_id} on server port {event.connection_id[1]}: "
            f"{event.reply}"
        )

    def failed(self, event: monitoring.CommandFailedEvent) -> None:
        logging.info(
            f"Command {event.command_name} with request id "
            f"{event.request_id} on server port {event.connection_id[1]}: "
            f"{event.failure}"
        )


monitoring.register(Logger())
client = MongoClient("mongodb://localhost/?replicaSet=rs")
client.db.posts.with_options(write_concern=WriteConcern(w=3)).delete_many({})

posts_collection = client.db.get_collection(
    "posts",
    read_preference=ReadPreference.SECONDARY,
    read_concern=ReadConcern("majority")
)
with client.start_session() as s:
    posts_collection.insert_one(
        {"user_id": 42, "contents": "I'm very witty"},
        session=s)
    cluster_time = s.cluster_time
    operation_time = s.operation_time

client2 = MongoClient("mongodb://localhost/?replicaSet=rs")
with client2.start_session() as s2:
    s2.advance_cluster_time(cluster_time)
    s2.advance_operation_time(operation_time)
    user_posts2 = list(client2.db.get_collection(
        "posts",
        read_preference=ReadPreference.SECONDARY,
        read_concern=ReadConcern("majority")
    ).find(
        {"user_id": 42},
        session=s2
    ))

    print(user_posts2)
