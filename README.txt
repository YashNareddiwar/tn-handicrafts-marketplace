Tamil Nadu Handicrafts DPI - Clean Demo / Deployment Version

LOCAL RUN
1. Open PowerShell in this folder.
2. python -m pip install -r requirements.txt
3. python app.py
4. Open http://127.0.0.1:8010

DEMO ACCOUNTS
buyer / buyer
farmer / farmer
shg / shg
bank / bank
admin / admin

CLEAN DATA STATE
- The packaged ZIP contains no SQLite database, orders, carts, loans, documents, or travel records.
- The uploads folder is empty.
- On first startup, the app automatically creates a fresh SQLite database containing ONLY the six listed products and the five demo accounts.
- Product images are kept as the product image URLs already defined in the app.

FREE DEPLOYMENT (RENDER)
- Push this folder to a GitHub repository.
- On Render, create a new Web Service from the repository and choose the Free plan.
- Build command: pip install -r requirements.txt
- Start command: gunicorn app:app --bind 0.0.0.0:$PORT
- The included render.yaml can also be used as the deployment blueprint.

IMPORTANT
Render Free web services have an ephemeral filesystem. SQLite data and uploaded files can be lost when the service restarts, spins down, or redeploys. This is suitable for a prototype/demo, not production data.
