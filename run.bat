start cmd /k "py casino.py"
start cmd /k "py pay_service.py"
start cmd /k "py pay_service_db.py"
start cmd /k "py session_auth.py"
start cmd /k "py match_simulation.py"

IF "%1"=="test" (
    start cmd /k "py test.py"
)
