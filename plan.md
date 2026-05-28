1. **Initialize and Restore Database**
   - Restore `bd_teraka.sql` into PostgreSQL 17.
   - Verify table structures and initial data.
2. **Fix Schema and Migration Inconsistencies**
   - Patch migrations to use `email` instead of `username`.
   - Add missing Django Auth columns to the legacy `users` table.
   - Align UUID/BigInt types between database and models.
3. **Setup and Configure Servers**
   - Install PostgREST binary.
   - Configure Django and PostgREST to work together (JWT, ports).
   - Start servers using `run_servers.py`.
4. **Populate Data for Testing**
   - Create superuser.
   - Inject data via Django ORM.
   - Inject data via PostgREST API (after fixing permissions).
5. **Verify System Functionality**
   - Run automated tests (`test_full_system.py`, `test_end_to_end.py`).
   - Perform visual verification with screenshots.
6. **Dockerization**
   - Update `Dockerfile` and `docker-compose.yml`.
   - Build and verify the Docker image.
7. **Complete pre commit steps**
   - Ensure proper testing, verification, review, and reflection are done.
8. **Submit the change**
