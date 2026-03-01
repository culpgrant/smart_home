To be written

### Stack
- Computer/Server: [Beelink Mini S13]('https://www.amazon.com/dp/B0BW8JSQCH')
- Operating System: Ubuntu
- POE Switch: Netgear GS316EPP


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

## Thread
Helpful thread commands:
    - `docker exec -it otbr ot-ctl child table`
        - LQ IN should be a 3 and Age should be a small number (seconds since last communication)
    - `docker logs -f matter-server` -> is the matter server (software) understanding the message
    - `docker logs -f otbr` -> is the radio even getting the signal?



### TODO:
- get frigate running
- Code Coverage
- Add secrets scanner
- Add github runners
- Clear all of the TODOs
- Build and publish python package for home server
- Build monitoring solution for the SSH login attempts
- Reolink documentation (Mac client, https://10.0.0.202/#/network)
- How I am running matter - http://localhost:5580/
- Setup Equinox EV in the home assitant
- Water Sensor for rain gage (other outdoor climate) stuff
- get Frigate running on the reolink feed. save events for n days. long term - integrate it more into a security system. turn on lights when a person is detected after a certain time.
- get an external harddive for saving the recordings.
- Put Home assistant backups on the home server for video recordings?
