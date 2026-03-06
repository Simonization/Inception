all:
	@bash run_docker.sh

clean:
	@bash run_docker.sh --clean

fclean: clean
	@docker rmi -f $$(docker images -qa) 2>/dev/null || true
	@docker system prune -af 2>/dev/null || true

re: fclean
	@bash run_docker.sh --blank-start

.PHONY: all clean fclean re
