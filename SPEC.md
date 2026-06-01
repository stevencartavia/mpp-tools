# MPP SDK Specification

Minimum requirements for conformant MPP SDK implementations.

**Normative References:**

- [draft-ietf-httpauth-payment](https://github.com/tempoxyz/ietf-paymentauth-spec/blob/main/specs/core/draft-httpauth-payment-00.md) — Core protocol
- [draft-payment-intent-charge](https://github.com/tempoxyz/ietf-paymentauth-spec/blob/main/specs/intents/draft-payment-intent-charge-00.md) — Charge intent semantics
- [draft-tempo-charge](https://github.com/tempoxyz/ietf-paymentauth-spec/blob/main/specs/methods/tempo/draft-tempo-charge-00.md) — Tempo charge implementation

---

## Design Principles

- **Protocol-first** — Core types (`Challenge`, `Credential`, `Receipt`) map directly to HTTP headers
- **Pluggable methods** — Payment methods (Tempo, Stripe, etc.) are independently packaged and gated wherever possible.
- **Minimal dependencies** — Core has no or minimal dependencies.
- **Designed for extension** — Users should be able to extend interface to support new `Intent` and `Method`s without needing to make PRs against the core SDKs.
- **Well tested** -- All SDKs should have high test coverage and include fuzz testing whenever possible.

---

## Core Types

SDKs must implement all core types and control flow defined in [draft-ietf-httpauth-payment §5](https://github.com/tempoxyz/ietf-paymentauth-spec/blob/main/specs/core/draft-httpauth-payment-00.md).

## Methods

SDKs must implement at least the following payment method:

| Method | Spec |
|--------|------|
| `tempo` | [draft-tempo-charge](https://github.com/tempoxyz/ietf-paymentauth-spec/blob/main/specs/methods/tempo/draft-tempo-charge-00.md) |

Additional methods (e.g., `stripe`) may be implemented but are not required for conformance.

## Intents

SDKs must implement each of the following intents:

| Intent | Spec |
|--------|------|
| `charge` | [draft-payment-intent-charge](https://github.com/tempoxyz/ietf-paymentauth-spec/blob/main/specs/intents/draft-payment-intent-charge-00.md) |

Additional intents (e.g., `authorize`) may be implemented but are not required for conformance.

## Client

### 402 Transport

SDKs MUST provide an HTTP transport layer that intercepts responses and handles the 402 payment flow transparently. The transport wraps the underlying HTTP client and manages credential creation without requiring application code changes.

This interface should be able to be defined in an explicit way (e.g. wrapped client) as well as implicitly (e.g. a `fetch` polyfill).

### 402 Retry Scheme

When a 402 response is received, the transport MUST implement the following retry logic:

SDKs MUST provide an HTTP transport/client that automatically handles 402 responses:

1. Make initial request
2. On 402 response, parse `WWW-Authenticate` header
3. Match challenge `method` to a configured payment method
4. Call `method.create_credential(challenge)` to produce a credential
5. Retry request with `Authorization: Payment <credential>` header
6. Return final response (with receipt if present)

---

## Server

### Challenge Generation

SDKs MUST provide a way to generate challenges:

```
Intent.challenge(request: object) -> Challenge
```

The challenge:

- MUST generate a unique `id` bound to the challenge parameters
- MUST include `method`, `intent`, and `request`
- SHOULD include `expires` for time-limited challenges

### Verification

SDKs MUST provide a way to verify credentials.

Depending on method or intent, this may require making live API requests or submitting transactions to blockchains.

SDKs should keep these requirements in mind and ensure their primitives are configurable and their control flows reliable.

```
Intent.verify(credential: Credential, request: object) -> Receipt
```

Verification MUST:

1. Validate the `challenge.id` matches the expected binding
2. Validate `challenge` parameters match the original request
3. Validate `expires` has not passed
4. Verify the `payload` according to the payment method specification
5. Return a `Receipt` on success, or raise an error on failure

## Transports

SDKs SHOULD provide integrations for common HTTP client/server libraries.

### Client Transports

| SDK | Libraries |
|-----|-----------|
| `mppx` (TypeScript) | `fetch` polyfill, fetch wrapper |
| `pympp` (Python) | `httpx.AsyncClient`, `PaymentTransport` |
| `mpp-rs` (Rust) | `reqwest` middleware (example) |

### Server Integrations

| SDK | Frameworks |
|-----|------------|
| `mppx` (TypeScript) | Fetch `Request`/`Response`, Node.js `http` module |
| `pympp` (Python) | `@requires_payment` decorator (Starlette/FastAPI, Django) |
| `mpp-rs` (Rust) | `axum`, `actix-web` examples |

---
