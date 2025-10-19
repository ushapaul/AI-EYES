@echo off
echo ============================================================
echo Cleaning up dismissed alerts from MongoDB
echo ============================================================
python -c "import sys; sys.path.append('.'); from database.models import alert_model, log_model; alerts = alert_model.find_all(); dismissed = [a for a in alerts if a.get('status') == 'dismissed']; print(f'\nFound {len(dismissed)} dismissed alerts'); deleted = sum(1 for a in dismissed if alert_model.delete_by_id(a['id'])); log_model.create_log(camera_id='system', action='cleanup', description=f'Deleted {deleted} alerts') if deleted > 0 else None; print(f'Deleted {deleted} dismissed alerts\n')"
echo.
echo ============================================================
echo Done! Check your MongoDB to verify.
echo ============================================================
pause
