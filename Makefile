clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -f tests/.coverage
	-docker rm `docker ps -a -q`
	-docker rmi `docker images -q --filter "dangling=true"`

build: clean
	python setup.py bdist_wheel --universal

uninstall:
	-pip uninstall -y vlab-vlan

install: uninstall build
	pip install -U dist/*.whl

test: uninstall install
	cd tests && nosetests -v --with-coverage --cover-package=vlab_vlan

images: build
	sudo docker build -f ApiDockerfile -t willnx/vlab-vlan-api .
	sudo docker build -f PgsqlDockerfile -t willnx/vlab-vlan-db .
	sudo docker build -f CeleryDockerfile -t willnx/vlab-vlan-celery .

up:
	docker-compose -p vlabVlan -f docker-compose.yml -f docker-compose.devmode.yml up
