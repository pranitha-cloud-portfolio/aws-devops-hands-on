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

ssm = boto3.client("ssm", region_name=region)


while True:
    try:
        for instance_id in instance_ids:

            # Check Apache status
            command = """
            if systemctl is-active --quiet httpd
            then
                echo "Apache is RUNNING"
            else
                echo "Apache is STOPPED - starting Apache"
                systemctl start httpd

                if systemctl is-active --quiet httpd
                then
                    echo "Apache STARTED successfully"
                else
                    echo "ERROR: Apache failed to start"
                    exit 1
                fi
            fi
            """

            response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [command]
                },
            )

            command_id = response["Command"]["CommandId"]

            logging.info(
                "Apache health check sent to %s | Command ID: %s",
                instance_id,
                command_id,
            )

            time.sleep(2)

            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )

            output = result.get("StandardOutputContent", "").strip()

            if output:
                logging.info(
                    "%s: %s",
                    instance_id,
                    output.replace("\n", " | "),
                )

    except Exception:
        logging.exception("Apache check failed; retrying")

    time.sleep(10)