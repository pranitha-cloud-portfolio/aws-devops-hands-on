# AWS Application Load Balancer Monitoring & Self-Healing Agent

## Overview

Built a Python-based monitoring and self-healing solution for an AWS Application Load Balancer (ALB) environment.

The monitoring agent continuously checks the ALB configuration, listeners, rules, target groups, target health, and application health-check behaviour.

The solution is designed to identify common application availability and health-check issues and initiate appropriate troubleshooting or recovery actions.

## Objective

Monitor an AWS Application Load Balancer and its backend application servers to detect availability and health-check issues and automate the recovery process.

## Architecture
                         Internet
                            |
                            v
              Application Load Balancer
                            |
                       Listener
                            |
                       Target Group
                       /          \
                      /            \
                     v              v
              WEBAPP1-EC2      WEBAPP2-EC2
                   |                |
                Docker           Docker
                   |                |
                Apache            Apache
                   |                |
                   +-------+--------+
                           |
                    Application Health
                           |
                           |  Monitor
                           v
                      Monitoring Agent
                           |
                     Monitoring Agent EC2
                           |
                        Docker
                           |
                         Python
                           |
                          IAM
                           |
                  AWS APIs / SSM

## AWS Services

- Amazon EC2
- Application Load Balancer (ALB)
- Target Groups
- IAM
- AWS Systems Manager (SSM)

## Technologies

- Python
- Docker
- Linux
- Apache HTTP Server
- AWS CLI
- AWS SDK for Python (Boto3)

## Implementation

### 1. Web Application Infrastructure

Configured two EC2-based web application servers as the backend application infrastructure.

The two web servers were configured to serve the application and were subsequently registered with an AWS Application Load Balancer
Target Group.

This infrastructure provides the backend targets whose health and availability are monitored by the self-healing agent.

### 2. Target Group

Created an Application Load Balancer Target Group and registered both EC2 web application servers as targets. Verified that the registered targets were healthy and accessible through the ALB.

### 3. Application Load Balancer

Created and configured an Application Load Balancer and associated the Target Group with the ALB.

Configured the listener and routing rules to distribute incoming HTTP traffic to the registered targets.

### 4. Monitoring Agent EC2 Instance

Created a dedicated EC2 instance to host the monitoring agent.

The monitoring application was packaged and executed inside a Docker container.

### 5. IAM Permissions

Updated the IAM role associated with the monitoring agent to allow the application to query ALB configuration and target health.

The following permissions were added:

    elasticloadbalancing:DescribeLoadBalancers
    elasticloadbalancing:DescribeListeners
    elasticloadbalancing:DescribeRules
    elasticloadbalancing:DescribeTargetGroups
    elasticloadbalancing:DescribeTargetHealth

### 6. ALB Monitoring

The monitoring agent checks:

- ALB state
- Listener configuration
- Listener rules
- Target Groups
- Target health
- Application health-check behaviour

### 7. Application Health Validation

The monitoring workflow validates the configured health-check endpoint and identifies application endpoint mismatches such as missing or incorrect `/index.html` paths.

### 8. Troubleshooting and Recovery

When an application or container issue affects target health, the agent can investigate the underlying application environment, including Apache, Docker and container-related issues.

## Monitoring Workflow

        Application Request
                |
                v
       Application Load Balancer
                |
                v
          Target Group
                |
                v
         Target Health Check
                |
                v
       +----------------------+
       | Target Healthy?      |
       +----------------------+
           /            \
         Yes             No
          |               |
          v               v
       Healthy        Diagnose Issue
      Application          |
                            +----------------+
                            |                |
                            v                v
                       Check Apache    Check Docker /
                                       Container /
                                       Endpoint
                            |                |
                            +-------+--------+
                                    |
                                    v
                             Recovery Action
                                    |
                                    v
                           Validate Target Health

## Testing

The monitoring solution was tested by intentionally introducing application health issues.

### Health-Check Endpoint Test

Modified the application environment by removing the expected `index.html` file from a web application and monitored the agent logs.

The agent detected the application health-check problem and provided the corresponding troubleshooting information.

### Target Health Validation

Verified the target health status through the Application Load Balancer and monitored the impact of application-level failures.

## Result

Successfully demonstrated AWS Application Load Balancer monitoring and application health troubleshooting using Python, Docker, IAM and AWS services.

The project demonstrates automated monitoring of ALB components, backend target health, application endpoints and container-based application issues.

## Key Learning

- Application Load Balancer
- Target Groups
- ALB listeners and rules
- Target health checks
- IAM permissions
- AWS Systems Manager
- Python automation
- Boto3
- Docker
- Apache troubleshooting
- Application endpoint validation
- Self-healing architecture
