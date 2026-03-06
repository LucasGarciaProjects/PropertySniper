# Scraper Debugging Instructions

## Issue: Price cannot be extracted

If you are seeing the error message **"Essential data could not be extracted. Price: None"**, follow these steps.

---

## 1. Use the debug endpoint (Backend – Port 8000)

The debug endpoint runs on the **backend** (port **8000**), NOT on the frontend (port **8080**).

### Option A: From the terminal

```
curl -X POST http://localhost:8000/debug/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_IDEALISTA_URL_HERE"}'
```

### Option B: From the browser (Swagger UI)

1. Open: http://localhost:8000/docs
2. Locate the endpoint `/debug/scrape`
3. Click **"Try it out"**
4. Paste your Idealista URL
5. Click **"Execute"**

---

## 2. Interpreting the results

The endpoint will return the following fields:

* `content_length`: Length of the extracted text content
* `html_length`: Length of the raw HTML
* `content_preview`: First 500 characters of the extracted content
* `extracted_price`: Extracted price (or `null` if not found)
* `extracted_m2`: Extracted square meters

---

## 3. Common Issues

### Issue: Captcha detected

**Symptom:** The content includes the word **"captcha"**

**Solution:**

* Idealista is blocking the scraping request
* Wait a few minutes and try again
* Try using a different property URL
* Consider using a proxy or a different configuration in Firecrawl

---

### Issue: Content too short

**Symptom:** `content_length` is less than **100 characters**

**Solution:**

* The page may not have loaded correctly
* Verify that the URL is valid and accessible
* The page may require login or may be protected

---

### Issue: Price is null but content exists

**Symptom:** `extracted_price` is `null` but `content_length` is large

**Solution:**

* The price format on the page may be different
* Check the `content_preview` to see how the price appears
* The regex patterns in `scraper.py` may need to be updated

---

## 4. Temporary workaround: Manual input

If scraping fails, you can temporarily modify the code to allow **manual input of property data** while the scraping issue is being resolved.

---

## 5. Support

If the issue persists, please provide:

* The URL you are trying to analyze
* The output from the `/debug/scrape` endpoint
* Any additional error messages
