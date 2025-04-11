
## **Prerequisites**
1. **Python**: Ensure Python is installed on your system.
2. **Redis**: Install and start Redis as the message broker.
   - Install Redis:
     ```bash
     sudo apt update
     sudo apt install redis
     ```
   - Start Redis:
     ```bash
     sudo service redis start
     ```
   - Verify Redis is running:
     ```bash
     redis-cli ping
     ```
     You should see `PONG` if Redis is running.

3. **Install Dependencies**:
   Install the required Python packages from [requirements.txt](http://_vscodecontentref_/0):
   ```bash
   pip install -r requirements.txt

4. **Start Celery Worker**:
    celery -A MyDoctor-hub worker --loglevel=info

5. **check Celery Status**:
    sudo service redis status

6. **Restart Celery Status**:
    sudo service redis restart

7. **Configure SERVICE_ACCOUNT_FILE In .env**

