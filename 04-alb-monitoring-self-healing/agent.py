import os
import time
import logging

import boto3
from botocore.exceptions import ClientError


# ============================================================
# Configuration
# ============================================================

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
ALB_NAME = os.getenv("ALB_NAME", "Agent-AI-ALB")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# ============================================================
# AWS Client
# ============================================================

elbv2 = boto3.client(
    "elbv2",
    region_name=AWS_REGION
)


# ============================================================
# Find ALB
# ============================================================

def get_load_balancer():
    try:
        response = elbv2.describe_load_balancers(
            Names=[ALB_NAME]
        )

        load_balancers = response.get("LoadBalancers", [])

        if not load_balancers:
            logging.error(
                "ALB not found: %s",
                ALB_NAME
            )
            return None

        return load_balancers[0]

    except ClientError:
        logging.exception(
            "Error while finding ALB"
        )
        return None


# ============================================================
# Check ALB
# ============================================================

def check_alb():
    logging.info("=" * 60)
    logging.info("ALB HEALTH CHECK")
    logging.info("=" * 60)

    alb = get_load_balancer()

    if not alb:
        return

    alb_name = alb["LoadBalancerName"]
    alb_arn = alb["LoadBalancerArn"]
    dns_name = alb["DNSName"]

    state = alb["State"]["Code"]
    reason = alb["State"].get("Reason", "N/A")

    logging.info("ALB Name : %s", alb_name)
    logging.info("DNS Name : %s", dns_name)
    logging.info("State    : %s", state)
    logging.info("Reason   : %s", reason)

    # --------------------------------------------------------
    # ALB state diagnosis
    # --------------------------------------------------------

    if state == "active":
        logging.info("ALB status: HEALTHY / ACTIVE")

    elif state == "provisioning":
        logging.warning(
            "ALB is still provisioning"
        )

    elif state == "active_impaired":
        logging.error(
            "ALB is ACTIVE_IMPAIRED"
        )

    elif state == "failed":
        logging.error(
            "ALB is in FAILED state"
        )

    else:
        logging.warning(
            "Unknown ALB state: %s",
            state
        )

    # --------------------------------------------------------
    # Listener check
    # --------------------------------------------------------

    check_listeners(alb_arn)

    # --------------------------------------------------------
    # Target groups
    # --------------------------------------------------------

    check_target_groups(alb_arn)


# ============================================================
# Listener Check
# ============================================================

def check_listeners(alb_arn):

    logging.info("-" * 60)
    logging.info("LISTENER CHECK")
    logging.info("-" * 60)

    try:
        response = elbv2.describe_listeners(
            LoadBalancerArn=alb_arn
        )

        listeners = response.get(
            "Listeners",
            []
        )

        if not listeners:
            logging.error(
                "No listeners found for ALB"
            )
            return

        for listener in listeners:

            listener_arn = listener["ListenerArn"]
            protocol = listener["Protocol"]
            port = listener["Port"]

            logging.info(
                "Listener: %s : %s",
                protocol,
                port
            )

            check_listener_rules(
                listener_arn
            )

    except ClientError:
        logging.exception(
            "Error checking listeners"
        )


# ============================================================
# Listener Rules
# ============================================================

def check_listener_rules(listener_arn):

    try:
        response = elbv2.describe_rules(
            ListenerArn=listener_arn
        )

        rules = response.get(
            "Rules",
            []
        )

        for rule in rules:

            priority = rule.get(
                "Priority",
                "N/A"
            )

            conditions = rule.get(
                "Conditions",
                []
            )

            actions = rule.get(
                "Actions",
                []
            )

            logging.info(
                "Rule priority: %s",
                priority
            )

            # ------------------------------
            # Path conditions
            # ------------------------------

            for condition in conditions:

                if condition.get(
                    "Field"
                ) == "path-pattern":

                    values = condition.get(
                        "Values",
                        []
                    )

                    logging.info(
                        "Path pattern: %s",
                        values
                    )

            # ------------------------------
            # Forward actions
            # ------------------------------

            for action in actions:

                if action.get(
                    "Type"
                ) == "forward":

                    target_group_arn = action.get(
                        "TargetGroupArn"
                    )

                    if target_group_arn:
                        logging.info(
                            "Forward Target Group: %s",
                            target_group_arn
                        )

    except ClientError:
        logging.exception(
            "Error checking listener rules"
        )


# ============================================================
# Target Group Check
# ============================================================

def check_target_groups(alb_arn):

    logging.info("-" * 60)
    logging.info("TARGET GROUP CHECK")
    logging.info("-" * 60)

    try:

        response = elbv2.describe_target_groups(
            LoadBalancerArn=alb_arn
        )

        target_groups = response.get(
            "TargetGroups",
            []
        )

        if not target_groups:

            logging.error(
                "No target groups associated with ALB"
            )

            return

        for target_group in target_groups:

            tg_name = target_group[
                "TargetGroupName"
            ]

            tg_arn = target_group[
                "TargetGroupArn"
            ]

            protocol = target_group[
                "Protocol"
            ]

            port = target_group[
                "Port"
            ]

            health_protocol = target_group.get(
                "HealthCheckProtocol",
                "N/A"
            )

            health_port = target_group.get(
                "HealthCheckPort",
                "N/A"
            )

            health_path = target_group.get(
                "HealthCheckPath",
                "N/A"
            )

            matcher = target_group.get(
                "Matcher",
                {}
            )

            success_codes = matcher.get(
                "HttpCode",
                "N/A"
            )

            logging.info(
                "Target Group: %s",
                tg_name
            )

            logging.info(
                "Protocol/Port: %s/%s",
                protocol,
                port
            )

            logging.info(
                "Health Check: %s %s %s",
                health_protocol,
                health_port,
                health_path
            )

            logging.info(
                "Expected HTTP Code: %s",
                success_codes
            )

            check_target_health(
                tg_name,
                tg_arn
            )

    except ClientError:
        logging.exception(
            "Error checking target groups"
        )


# ============================================================
# Target Health
# ============================================================

def check_target_health(
    target_group_name,
    target_group_arn
):

    logging.info(
        "TARGET HEALTH: %s",
        target_group_name
    )

    try:

        response = elbv2.describe_target_health(
            TargetGroupArn=target_group_arn
        )

        targets = response.get(
            "TargetHealthDescriptions",
            []
        )

        if not targets:

            logging.warning(
                "No registered targets"
            )

            return

        for target in targets:

            target_id = target[
                "Target"
            ]["Id"]

            target_port = target[
                "Target"
            ].get("Port", "N/A")

            health = target[
                "TargetHealth"
            ]

            state = health.get(
                "State",
                "unknown"
            )

            reason = health.get(
                "Reason",
                "N/A"
            )

            description = health.get(
                "Description",
                "N/A"
            )

            logging.info(
                "Target: %s:%s",
                target_id,
                target_port
            )

            logging.info(
                "State : %s",
                state
            )

            logging.info(
                "Reason: %s",
                reason
            )

            if description != "N/A":

                logging.info(
                    "Description: %s",
                    description
                )

            # ------------------------------------------------
            # Diagnosis
            # ------------------------------------------------

            diagnose_target(
                target_id,
                state,
                reason
            )

    except ClientError:
        logging.exception(
            "Error checking target health"
        )


# ============================================================
# Diagnosis
# ============================================================

def diagnose_target(
    target_id,
    state,
    reason
):

    if state == "healthy":

        logging.info(
            "DIAGNOSIS: %s is HEALTHY",
            target_id
        )

        return

    logging.warning(
        "DIAGNOSIS: %s is NOT HEALTHY",
        target_id
    )

    if reason == "Target.ResponseCodeMismatch":

        logging.error(
            "Application returned an unexpected HTTP response."
        )

        logging.error(
            "Possible causes:"
        )

        logging.error(
            "1. Incorrect health-check path"
        )

        logging.error(
            "2. Application endpoint does not exist"
        )

        logging.error(
            "3. Application returned unexpected HTTP status"
        )

    elif reason == "Target.Timeout":

        logging.error(
            "Health check timed out."
        )

        logging.error(
            "Possible causes:"
        )

        logging.error(
            "1. Apache/httpd stopped"
        )

        logging.error(
            "2. Docker stopped"
        )

        logging.error(
            "3. Container stopped"
        )

        logging.error(
            "4. Network/Security Group issue"
        )

    elif reason == "Target.FailedHealthChecks":

        logging.error(
            "Target failed health checks."
        )

        logging.error(
            "Check Apache, Docker, container and application."
        )

    elif reason == "Target.NotRegistered":

        logging.error(
            "Target is not registered with Target Group."
        )

    elif reason == "Target.NotInUse":

        logging.error(
            "Target Group is not being used by the ALB."
        )

    elif reason == "Target.InvalidState":

        logging.error(
            "Target is in an invalid state."
        )

    else:

        logging.error(
            "Reason reported by ALB: %s",
            reason
        )


# ============================================================
# Main
# ============================================================

def main():

    logging.info("=" * 60)
    logging.info("AI AGENT STARTED")
    logging.info("=" * 60)

    logging.info(
        "Region: %s",
        AWS_REGION
    )

    logging.info(
        "ALB: %s",
        ALB_NAME
    )

    while True:

        try:

            check_alb()

        except Exception:

            logging.exception(
                "Unexpected error in monitoring loop"
            )

        logging.info(
            "Next health check in %s seconds",
            CHECK_INTERVAL
        )

        time.sleep(
            CHECK_INTERVAL
        )


if __name__ == "__main__":
    main()
