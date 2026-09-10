# House price prediction

## Run

From the project root:

```bash
cd backend
uvicorn main:app --reload
```

Open the frontend at http://127.0.0.1:8000/static/house_form.html. The API docs are at http://127.0.0.1:8000/docs.

## GET /predict tests

The test request `area=80`, `bedrooms=3`, `location=hanoi` returns:

```json
{"area":80.0,"bedrooms":3,"location":"hanoi","predicted_price":2405000000.0}
```

**Explain why #1:** Calling `/predict` without `location` works because it has the default value `"other"`, so no multiplier is applied.
 
**Explain why #2:** Calling it without `area` returns HTTP `422` because `area` is a required query parameter with no default value.

The same GET request can also be tested directly in the browser address bar:

```text
http://127.0.0.1:8000/predict?area=80&bedrooms=3&location=hanoi
```

Without `location`, this URL still works:

```text
http://127.0.0.1:8000/predict?area=80&bedrooms=3
```

It works because `location` is optional and defaults to `"other"`. Without `area`, for example `/predict?bedrooms=3`, FastAPI returns `422 Unprocessable Entity` because `area` is required and has no default value. FastAPI validates required query parameters before calling the endpoint.

## POST /predict (JSON body bonus)

There is also a second `POST /predict` endpoint using the `HouseInput` Pydantic model:

```json
{
  "area": 80,
  "bedrooms": 3,
  "location": "hanoi"
}
```

Query parameters are sent in the URL and are convenient for a simple GET request. A JSON body is sent inside the request body and is better suited to structured data in a POST request; Pydantic validates the body fields and applies the default location when it is omitted.

The form uses the relative URL `/predict` because FastAPI serves the page and API from the same origin (`127.0.0.1:8000`). The browser therefore sends the request to the same host and port, so it is not a cross-origin request and does not require CORS configuration.
