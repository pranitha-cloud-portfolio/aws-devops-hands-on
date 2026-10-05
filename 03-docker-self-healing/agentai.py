import logging
import subprocess
import time

import docker


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CHECK_INTERVAL = 10

WEBAPP1_CONTAINER = "webapp1-container"
WEBAPP2_CONTAINER = "webapp2-container"
APACHE_SERVICE = "httpd"


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# --------------------------------------------------
# Docker connection
# --------------------------------------------------

docker_client = docker.from_env()


# --------------------------------------------------
# Check Docker container
# --------------------------------------------------

def check_container(container_name):

    try:
        container = docker_client.containers.get(container_name)

        container.reload()

        status = container.status

        logging.info(
            "%s status: %s",
            container_name,
            status,
        )

        if status != "running":

            logging.warning(
                "%s is %s - starting container",
                container_name,
                status,
            )

            container.start()

            logging.info(
                "%s started successfully",
                container_name,
            )

    except docker.errors.NotFound:

        logging.error(
            "Container %s was not found",
            container_name,
        )

    except Exception:

        logging.exception(
            "Error while checking %s",
            container_name,
        )


# --------------------------------------------------
# Check Apache/httpd on EC2 host
# --------------------------------------------------

def check_httpd():

    try:

        result = subprocess.run(
            [
                "nsenter",
                "-t",
                "1",
                "-m",
                "-u",
                "-i",
                "-n",
                "-p",
                "--",
                "/usr/bin/systemctl",
                "is-active",
                "--quiet",
                APACHE_SERVICE,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if result.returncode == 0:

            logging.info(
                "httpd status: RUNNING"
            )

        else:

            logging.warning(
                "httpd status: STOPPED - starting httpd"
            )

            subprocess.run(
                [
                    "nsenter",
                    "-t",
                    "1",
                    "-m",
                    "-u",
                    "-i",
                    "-n",
                    "-p",
                    "--",
                    "/usr/bin/systemctl",
                    "start",
                    APACHE_SERVICE,
                ],
                check=True,
            )

            logging.info(
                "httpd started successfully"
            )

    except Exception:

        logging.exception(
            "Error while checking httpd"
        )


# --------------------------------------------------
# Main monitoring loop
# --------------------------------------------------

def main():

    logging.info("AIAgent started")

    while True:

        logging.info("----- Health Check -----")

        # Check WebApp1
        check_container(WEBAPP1_CONTAINER)

        # Check WebApp2
        check_container(WEBAPP2_CONTAINER)

        # Check Apache
        check_httpd()

        time.sleep(CHECK_INTERVAL)


# --------------------------------------------------
# Start agent
# --------------------------------------------------

if __name__ == "__main__":
    main()