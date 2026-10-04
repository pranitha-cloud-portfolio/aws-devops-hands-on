# AWS EC2 Self-Healing Agent

## Overview

Built a Python-based monitoring agent to continuously monitor two AWS EC2 web application servers.

When an EC2 instance is detected in a STOPPED state, the agent automatically starts the instance.

The monitoring agent is packaged and executed inside a Docker container on a dedicated EC2 instance.

## Architecture

                         Internet
                            |
                            v
              AWS Application Load Balancer
                            |
                            v
                     Target Group
                       /       \
                      /         \
                     v           v
              EC2 WebApp1    EC2 WebApp2
                  |               |
                Apache          Apache
                  |               |
                  +-------+-------+
                          |
                          v
                  AI Monitoring Agent EC2
                          |
                        Docker
                          |
                        Python
                          |
                     AWS EC2 / IAM
## AWS Services

- Amazon EC2
- Application Load Balancer
- Target Groups
- IAM
- Amazon Linux
- Docker

## Technologies

- Python
- Docker
- AWS CLI
- AWS SDK
- Linux
- Apache HTTP Server

## Implementation

### 1. EC2 Web Servers

Created two Linux EC2 instances and configured Apache HTTP servers to host simple static websites.

### 2. Application Load Balancer

Created a Target Group and registered both EC2 web servers as targets. Configured an Application Load Balancer (ALB) and associated the Target Group with the ALB to distribute incoming HTTP traffic across the web servers.

### 3. IAM

Created an IAM role with EC2 permissions and attached it to the AI-Agent EC2 instance, enabling the monitoring application to securely interact with AWS EC2 resources.

### 4. Monitoring Agent

Created:

- `agent.py`
- `Dockerfile`

The Python agent monitors the EC2 instances and checks their current state.

### 5. Docker

Built and executed the monitoring agent as a Docker container.

Example:

    docker build -t agent-image -f Dockerfile .
    docker run -itd --name agent-container -P agent-image

## Testing

The solution was tested by manually stopping an EC2 web server.

The monitoring agent detected the stopped instance and initiated the start operation.

Agent logs were used to verify the monitoring and recovery process.

## Result

Successfully demonstrated automated EC2 monitoring and self-healing using Python, Docker, IAM and AWS EC2.

## Key Learning

- EC2 instance lifecycle management
- IAM role-based AWS access
- AWS infrastructure monitoring
- Python automation
- Docker containerization
- Application Load Balancer and Target Groups
- Failure simulation and automated recovery
