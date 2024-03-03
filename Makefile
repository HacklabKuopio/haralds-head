eyes:
	python -m haralds_head.eyes_of_harald

flask:
	python -m haralds_head.flask_of_harald

wall:
	python -m haralds_head.wall_of_harald

wall_debug:
	python -m haralds_head.wall_of_harald --debug

#mind:
#	python -m haralds_head.mind_of_harald

#mind_debug:
#	python -m haralds_head.mind_of_harald --debug

voice:
	echo "hello world" > /opt/haralds-head/haralds-greeting.txt
	python -m haralds_head.voice_of_harald 


.PHONY: eyes flask wall wall_debug voice
