# Mock it till you Rock it

`docker-compose up` to spin up virtual stations in a docker network.

## Mocking

- Configure the ronny's in the src/config.py file
- Bind the postgres ports to your local machine so you can insert into the database: `ssh -L 5432:localhost:6001 172.12.50.101`


## Roadmap

- Send packets to the actual station configured in the docker network. Decide wheter to directly insert in the database or add a debug web endpoint.
- Configure playback speed. Atm it is in real-time.
- Add reliability option. Be able to make a station unreliable and occasionally drop packets.


### ui

- # send detections
- # dropped detections
- small graph of where we are in the time of the event
- more zoomed graph of the detections comming in on our terrain laid out in a line
