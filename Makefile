DOCKER=docker run --rm -it -v ${PWD}:/app packtpub-downloader:latest

.PHONY: build_test_container
build-dev-container:
	docker build \
		--tag packtpub-downloader:latest \
		-f Dockerfile .

.PHONY: enter-container
enter-container:
	${DOCKER} \
		bash

.PHONY: clean
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} \; | exit 0
	find . -name ".mypy_cache" -type d -exec rm -rf {} \; | exit 0
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

lint:
	black --check ./

tests: clean lint
	mypy ./
	python -m pytest --cov --pylama --verbose --color=yes ./
	coverage xml

