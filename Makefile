all:
	flask --app webapp/app --debug run --host=0.0.0.0 --port=8080

server:
	sudo python3 src/play_video_server.py