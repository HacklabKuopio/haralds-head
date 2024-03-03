eyes:
	python3 -m haralds_head.eyes_of_harald

flask:
	python3 -m haralds_head.flask_of_harald

wall:
	python3 -m haralds_head.wall_of_harald

wall_debug:
	python3 -m haralds_head.wall_of_harald --debug

voice:
	echo "hello world" > /opt/haralds-head/haralds-greeting.txt
	python3 -m haralds_head.voice_of_harald


.PHONY: eyes flask wall wall_debug voice
