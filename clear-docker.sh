docker container stop -f $(docker ps -aq)
docker container rm -f $(docker ps -aq)
docker volume rm -f $(docker volume ls)
docker rmi -f $(docker images -q)
docker system prune -a --force