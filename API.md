# Coderr API – Endpoint Dokumentation

## Authentication

### Registrierung

**POST** `/api/registration/`

**Beschreibung:**

Erstellt einen neuen Benutzer. Der Benutzer kann entweder ein `customer` oder `business` sein.

**Request Body**

```json
{
  "username": "exampleUsername",
  "email": "example@email.de",
  "password": "examplePassword",
  "password2": "examplePassword",
  "type": "customer"
}

```

**Success Response**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "username": "exampleUsername",
  "email": "example@email.de",
  "user_id": 1
}

```

**Status Codes**

- 201 Benutzer erfolgreich erstellt
- 400 Ungültige Anfrage
- 500 Interner Serverfehler

**Permissions:** keine

---

### Login

**POST** `/api/login/`

**Request Body**

```json
{
  "username": "exampleUsername",
  "password": "examplePassword"
}

```

**Success Response**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "username": "exampleUsername",
  "email": "example@email.de",
  "user_id": 1
}

```

**Status Codes**

- 200 Erfolgreich
- 400 Ungültige Anmeldedaten
- 500 Interner Serverfehler

**Permissions:** keine

---

## Profile

### Profil abrufen

**GET** `/api/profile/{pk}/`

**Beschreibung:**

Ruft die Profildaten eines Benutzers ab.

**Success Response**

```json
{
  "user": 1,
  "username": "max_mustermann",
  "first_name": "Max",
  "last_name": "Mustermann",
  "file": "profile_picture.jpg",
  "location": "Berlin",
  "description": "Business description",
  "working_hours": "9-18",
  "type": "business",
  "created_at": "2023-01-01T12:00:00Z"
}

```

**Permissions:** Authentifiziert

---

### Profil aktualisieren

**PATCH** `/api/profile/{pk}/`

**Request Body**

```json
{
  "first_name": "Max",
  "last_name": "Mustermann",
  "location": "Berlin",
  "description": "Updated business description",
  "working_hours": "9-18"
}

```

**Status Codes**

- 200 Erfolgreich aktualisiert
- 401 Nicht authentifiziert
- 403 Keine Berechtigung

---

### Business Profile

**GET** `/api/profiles/business/`

**Permissions:** Authentifiziert

---

### Customer Profile

**GET** `/api/profiles/customer/`

**Permissions:** Authentifiziert

---

## Angebote (Offers)

### Alle Angebote abrufen

**GET** `/api/offers/`

**Query Parameter**

- `creator_id`
- `min_price`
- `max_delivery_time`
- `ordering`
- `search`
- `page_size`

**Success Response (gekürzt)**

```json
{
  "count": 11,
  "results": [
    {
      "id": 1,
      "title": "Website Design",
      "min_price": 100,
      "min_delivery_time": 5
    }
  ]
}

```

**Permissions:** keine

---

### Angebot erstellen

**POST** `/api/offers/`

**Request Body**

```json
{
  "title": "Grafikdesign Paket",
  "description": "Ein umfassendes Grafikdesign-Paket",
  "details": [
    {
      "title": "Basic Design",
      "price": 100,
      "delivery_time_in_days": 5,
      "features": ["Logo Design"]
    }
  ]
}

```

**Permissions:** Nur `business` User

---

### Angebotsdetails

**GET** `/api/offers/{id}/`

---

### Angebot aktualisieren

**PATCH** `/api/offers/{id}/`

---

### Angebot löschen

**DELETE** `/api/offers/{id}/`

**Permissions:** Nur Ersteller

---

## Bestellungen (Orders)

### Bestellungen abrufen

**GET** `/api/orders/`

**Beschreibung:**

Gibt alle Bestellungen des eingeloggten Users zurück.

---

### Bestellung erstellen

**POST** `/api/orders/`

**Request Body**

```json
{
  "offer_detail_id": 1
}

```

---

### Bestellstatus ändern

**PATCH** `/api/orders/{id}/`

```json
{
  "status": "completed"
}

```

**Permissions:** Business User

---

### Bestellung löschen

**DELETE** `/api/orders/{id}/`

**Permissions:** Admin / Staff

---

### Order Count

**GET** `/api/order-count/{business_user_id}/`

---

### Completed Order Count

**GET** `/api/completed-order-count/{business_user_id}/`

---

## Bewertungen (Reviews)

### Bewertungen abrufen

**GET** `/api/reviews/`

---

### Bewertung erstellen

**POST** `/api/reviews/`

```json
{
  "rating": 5,
  "description": "Alles war top!"
}

```

---

### Bewertung aktualisieren

**PATCH** `/api/reviews/{id}/`

---

### Bewertung löschen

**DELETE** `/api/reviews/{id}/`

**Permissions:** Nur Ersteller

---

## Übergreifende Endpoints

### Basisinformationen

**GET** `/api/base-info/`

```json
{
  "review_count": 10,
  "average_rating": 4.6,
  "business_profile_count": 45,
  "order_count": 150
}

```

**Permissions:** keine

---