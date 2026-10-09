# TODO

## General

- Evaluate which routes need to be async.
- Evaluate whether we documented all responses where we removed the "message" wrapping.
- Check whether `feedback` part of textpair can actually be optional???
- Consider whether we shouldn't hard-code the outline of the feedback `rating` (currently just a dict).
- Consider splitting feedback by mode?

## Route Changes

- POST `/api/analyze` -> POST `/analysis`
  - The route now does not wrap its response in a "message" dict so the consuming route should be adjusted as well.
  - The request body also switched parameters from `skip_barriers` (with default "False") to `check_barriers` (default "True").
- POST `/api/domain/` -> GET `/parlance/domains`
  - No longer takes any parameters. I made this decision to take load off of our mongoDB. Given the _tiny_ number of supported domains, we can just always send all of them and have any search in the drop-down be performed by the frontend application.
- POST `/api/parlance_words` -> GET `/parlance`
  - Parameters are URL-encoded now.
- POST `/api/all_barriers` -> GET `/analysis/barriers`
  - Also no longer wraps the definitions into "message" dict.
- POST `/api/store` -> POST `/feedback`
  - Feedback definition has also changed:
    - `normal_text`: `text_original`
    - `top_text`: `text_translated`
    - `similarity`: `strategy`
