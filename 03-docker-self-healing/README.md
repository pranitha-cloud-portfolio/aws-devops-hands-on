# Docker Self-Healing Agent

## Overview

Built a container-based self-healing solution on an AWS EC2 instance to monitor Docker application containers and the Apache HTTP service.

The solution uses a dedicated monitoring agent container to detect application or service failures and initiate recovery actions.

## Objective

Create and monitor multiple application containers on a single EC2 instance and automatically recover the environment when a container or Apache service becomes unavailable.

## Architecture

                         AWS EC2 Instance
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        WebApp1 Container  WebApp2 Container  Monitoring Agent
              |                |                |
            Nginx            Nginx             Python
                                                 |
                                           Docker Socket
                                                 |
                                                 v
                                           Docker Engine
                                                 |
                                                 v
                                           Apache Service

## AWS Services

- Amazon EC2
- IAM

## Technologies

- Docker
- Python
- Nginx
- Apache HTTP Server
- Linux
- AWS CLI

## Implementation

### 1. EC2 Instance

Launched a Linux EC2 instance and prepared the environment for running multiple Docker containers.

### 2. Docker Installation

Installed and enabled Docker on the EC2 instance.

### 3. Web Application Containers

Created two containerized web applications using Nginx.

The containers were exposed on separate host ports for testing and validation.

### 4. Apache Service

Installed and configured the Apache HTTP service on the EC2 host.

### 5. Self-Healing Agent

Created:

- `agentai.py`
- `Dockerfile`

The monitoring agent runs inside a Docker container and interacts with the Docker engine to monitor the application containers.

### 6. Docker Socket Access

The monitoring container was configured with access to the Docker socket so that the agent could monitor and perform container operations.

The agent container was configured to run continuously.

## Self-Healing Workflow

    Monitor Containers / Apache
              |
              v
       Failure Detected?
          /          \
        No            Yes
        |              |
        |              v
        |        Recovery Action
        |              |
        +--------------+
               |
               v
       Service / Container
          Availability

## Testing

The self-healing functionality was tested by intentionally introducing failures.

### Container Failure

Stopped the WebApp container manually and monitored the AI-agent container logs to verify the recovery behaviour.

### Apache Service Failure

Stopped the Apache HTTP service using:

    systemctl stop httpd

The monitoring agent was then used to detect and recover from the service failure.

## Docker Commands

Build the AI-agent image:

    docker build -t aiimage -f Dockerfile .

Run the AI-agent container:

    docker run -d --name ai-container \
      --privileged \
      --pid=host \
      -v /var/run/docker.sock:/var/run/docker.sock \
      --restart unless-stopped \
      aiimage

Check the agent logs:

    docker logs -f ai-container

## Result

Successfully demonstrated container and service monitoring with automated recovery using Docker, Python and Linux on AWS EC2.

## Key Learning

- Docker container management
- Docker image creation
- Container failure simulation
- Docker socket integration
- Python-based automation
- Nginx container deployment
- Apache service management
- Linux troubleshooting
- Self-healing automation
