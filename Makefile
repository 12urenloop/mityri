all: run

clean:
	docker-compose down --rmi all
