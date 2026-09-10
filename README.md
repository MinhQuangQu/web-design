# House price prediction

## Run

From the project root:

```bash
cd backend
uvicorn main:app --reload
```

Open the frontend at http://127.0.0.1:8000/static/house_form.html. The API docs are at http://127.0.0.1:8000/docs.

The test request `area=80`, `bedrooms=3`, `location=hanoi` returns:

```json
{"area":80.0,"bedrooms":3,"location":"hanoi","predicted_price":2405000000.0}
```

Calling `/predict` without `location` works because it has the default value `"other"`, so no multiplier is applied. Calling it without `area` returns HTTP `422` because `area` is a required query parameter with no default value.

The form uses the relative URL `/predict` because FastAPI serves the page and API from the same origin (`127.0.0.1:8000`), so the browser does not make a cross-origin request.
