# Coderr API – Endpoint Documentation

## Authentication

### Registration

**POST** `/api/registration/`

**Description:**

Creates a new user. The user can be either a `customer` or `business`.

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

- 201 User successfully created
- 400 Invalid request
- 500 Internal server error

**Permissions:** None

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

- 200 Successful
- 400 Invalid credentials
- 500 Internal server error

**Permissions:** None

---

## Profile

### Get Profile

**GET** `/api/profile/{pk}/`

**Description:**

Retrieves profile data of a user.

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

**Permissions:** Authenticated

---

### Update Profile

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

- 200 Successfully updated
- 401 Not authenticated
- 403 No permission

---

### Business Profiles

**GET** `/api/profiles/business/`

**Permissions:** Authenticated

---

### Customer Profiles

**GET** `/api/profiles/customer/`

**Permissions:** Authenticated

---

## Offers

### Get All Offers

**GET** `/api/offers/`

**Query Parameters**

- `creator_id`
- `min_price`
- `max_delivery_time`
- `ordering`
- `search`
- `page_size`

**Success Response (shortened)**

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

**Permissions:** None

---

### Create Offer

**POST** `/api/offers/`

**Request Body**

```json
{
  "title": "Graphic Design Package",
  "description": "A comprehensive graphic design package",
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

**Permissions:** Only `business` users

---

### Get Offer Details

**GET** `/api/offers/{id}/`

---

### Update Offer

**PATCH** `/api/offers/{id}/`

---

### Delete Offer

**DELETE** `/api/offers/{id}/`

**Permissions:** Only creator

---

## Orders

### Get Orders

**GET** `/api/orders/`

**Description:**

Returns all orders of the logged-in user.

---

### Create Order

**POST** `/api/orders/`

**Request Body**

```json
{
  "offer_detail_id": 1
}

```

---

### Update Order Status

**PATCH** `/api/orders/{id}/`

```json
{
  "status": "completed"
}

```

**Permissions:** Business user

---

### Delete Order

**DELETE** `/api/orders/{id}/`

**Permissions:** Admin / Staff

---

### Order Count

**GET** `/api/order-count/{business_user_id}/`

---

### Completed Order Count

**GET** `/api/completed-order-count/{business_user_id}/`

---

## Reviews

### Get Reviews

**GET** `/api/reviews/`

---

### Create Review

**POST** `/api/reviews/`

```json
{
  "rating": 5,
  "description": "Everything was great!"
}

```

---

### Update Review

**PATCH** `/api/reviews/{id}/`

---

### Delete Review

**DELETE** `/api/reviews/{id}/`

**Permissions:** Only creator

---

## General Endpoints

### Base Information

**GET** `/api/base-info/`

```json
{
  "review_count": 10,
  "average_rating": 4.6,
  "business_profile_count": 45,
  "order_count": 150
}

```

**Permissions:** None

---