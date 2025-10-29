To be written

### To Do List
- Hookup Thermostat
- Download Home Assistant in the car
- Setup Equinox EV in the home assitant
- Buy the hookup for the garage door
- Water Sensor for rain gage (other outdoor climate) stuff
- announcement in bathroom when i am home

### Stack
- Computer/Server: [Beelink Mini S13]('https://www.amazon.com/dp/B0BW8JSQCH')
- Operating System: Ubuntu


### Setup Instructions
- Create a bootable USB with linux OS on it. [Help Document]('https://ubuntu.com/tutorials/create-a-usb-stick-on-macos#1-overview')
- Setup computer for development
    - [uv](https://docs.astral.sh/uv/getting-started/installation/)
    - git
        - `sudo apt install git`
    - vscode
        - Ubuntu App Center
    - ssh
        - Need to also secure SSH logins. Please do own research
        - `/etc/ssh/sshd_config`
        - fail2ban
- [Install Docker](https://docs.docker.com/engine/install/ubuntu/) (Docker Desktop optional)


### How to update Home Assitant
- Ensure automated backup was taken
- `docker ps`
- `docker stop (contianer_id from above)`
- Update `docker-compose.yml` image with the correct version
- `docker compose up -d`
- To confirm the version:
- `docker exec -it (container_id) bash`
- `hass --version`
- `exit`


### TODO:
- Build and publish python package for home server
- Build monitoring solution for the SSH login attempts
