import logging
import time

import boto3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

region = "ap-south-1"  # Mumbai
instance_ids = [
    "i-0e8d6524cd0f0156c",  # inst-1
    "i-0ffa2b9196e959df5",  # inst-2
]

ec2 = boto3.client("ec2", region_name=region)

while True:
    try:
        response = ec2.describe_instances(InstanceIds=instance_ids)

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                state = instance["State"]["Name"]
                name = next(
                    (
                        tag["Value"]
                        for tag in instance.get("Tags", [])
                        if tag["Key"] == "Name"
                    ),
                    instance_id,
                )

                logging.info("%s (%s): %s", name, instance_id, state)

                if state == "stopped":
                    ec2.start_instances(InstanceIds=[instance_id])
                    logging.warning(
                        "Start requested for %s (%s)", name, instance_id
                    )

    except Exception:
        logging.exception("Check failed; retrying")

    time.sleep(10)