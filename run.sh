.venv/bin/python api_gateway/main.py > api_gateway.log 2>&1 &
.venv/bin/python content_service/main.py > content_service.log 2>&1 &
.venv/bin/python recommendation_service/main.py > recommendation_service.log 2>&1 &
.venv/bin/python user_service/main.py > user_service.log 2>&1 &