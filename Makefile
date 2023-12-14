test:
	pytest -vv -cov=app app/

install:
	pip install --upgrade pip &&\
	pip install -r requirements.txt

build:
	docker build -t data-upload-app:latest .

push:
	docker tag flask-app $(DOCKER_REPO)/data-upload-app:latest
	docker push $(DOCKER_REPO)/data-upload-app:latest

run: 
	docker run -d -p 5000:5000 flask-app