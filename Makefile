all:
	@bash run_docker.sh

clean:
	@bash run_docker.sh --clean

fclean: clean

re:
	@bash run_docker.sh --blank-start

.PHONY: all clean fclean re
