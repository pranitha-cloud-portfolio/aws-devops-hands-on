# AWS Apache Service Self-Healing Agent

## Overview

Built a Python-based monitoring agent to monitor the Apache HTTP service running on AWS EC2 web application servers.

When the Apache service is detected in a STOPPED state, the agent initiates the service start operation to restore application availability.

The monitoring agent is packaged and executed inside a Docker container.

## Objective

Automate the detection and recovery of Apache service failures without requiring manual intervention.

## Architecture

                         AWS Environment

                +---------------------------+
                |       AI Agent EC2        |
                |                           |
                |       Docker Container    |
                |              |            |
                |          Python Agent     |
                +--------------|------------+
                               |
                         AWS Systems Manager
                               |
                    +----------+----------+
                    |                     |
                    v                     v
              EC2 WebApp1           EC2 WebApp2
                    |                     |
                  Apache                Apache
                    |                     |
                    +---------------------+

## AWS Services

- Amazon EC2
- AWS Systems Manager (SSM)
- IAM

## Technologies

- Python
- Docker
- Linux
- Apache HTTP Server
- AWS CLI
- AWS Systems Manager

## Implementation

### 1. EC2 Web Application Servers

Configured Linux EC2 instances with Apache HTTP Server to host web applications.

### 2. AWS Systems Manager

Configured AWS Systems Manager to communicate with the web application servers and perform remote service operations.

### 3. IAM

Configured the required IAM permissions for the AI-Agent EC2 instance and the Systems Manager operations.

### 4. Monitoring Agent

Created:

- `agenttask2.py`
- `Dockerfile`

The Python monitoring agent checks the Apache service status.

### 5. Docker

Built the monitoring application as a Docker image and executed it as a container.

Example:

    docker build -t agenttask2-image -f Dockerfile .
    docker run -itd --name agenttask-container -P agenttask2-image

## Self-Healing Workflow

    Monitor Apache Service
            |
            v
    Is Apache STOPPED?
          /     \
        No       Yes
        |         |
        |         v
        |    Start Apache
        |         |
        +---------+
              |
              v
       Service Recovery

## Testing

The Apache service was stopped manually to simulate a service
failure.

The monitoring agent detected the service condition and initiated
the recovery operation.

AWS Systems Manager was used to execute commands on the web
application servers and validate the service status.

## Troubleshooting

During implementation, an IAM permission issue was encountered.

The IAM role associated with the AI-Agent EC2 instance was updated with the required permissions to allow the monitoring workflow to communicate with the target servers.

## Result

Successfully demonstrated automated Apache service monitoring and recovery using Python, Docker, IAM and AWS Systems Manager.

## Key Learning

- AWS Systems Manager
- IAM permissions
- EC2 service management
- Apache service monitoring
- Python automation
- Docker containerization
- Automated service recovery
- Troubleshooting AWS permission issues
