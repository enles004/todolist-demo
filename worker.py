import json

import pika

from config import local, queue_user_account, queue_delete_project
from handlers.email import send_register_notify_email, send_delete_project_notify_email

connection = pika.BlockingConnection(pika.ConnectionParameters(local))
channel = connection.channel()
channel.queue_declare(queue=queue_user_account)
channel.queue_declare(queue=queue_delete_project)

handler_mapping = {
    "send_mail_register": send_register_notify_email,
    "send_mail_delete_project": send_delete_project_notify_email
}


def main():
    def callback(ch, method, properties, body):
        print(f" [x] Received {json.loads(body)}")
        parsed_body = json.loads(body)
        command = parsed_body.get("command_type")
        handler = handler_mapping.get(command)
        try:
            handler(parsed_body)
        except Exception as e:
            print("Error " + str(e))

    channel.basic_consume(queue=queue_user_account, auto_ack=True, on_message_callback=callback)
    channel.basic_consume(queue=queue_delete_project, auto_ack=True, on_message_callback=callback)
    print(" [*] Waiting for message. To exit press Ctrl + C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[*] You have exited")
