def validate_comment(title, body):
    errors = []
    title = title.strip() if title else ""
    body  = body.strip()  if body  else ""

    if len(title) < 3:
        errors.append("Comment title must be at least 3 characters.")
    elif len(title) > 120:
        errors.append("Comment title must be 120 characters or fewer.")

    if len(body) < 10:
        errors.append("Comment must be at least 10 characters.")
    elif len(body) > 2000:
        errors.append("Comment must be 2000 characters or fewer.")

    return {"ok": len(errors) == 0, "errors": errors}


def validate_post(title, body, tags_raw):
    errors = []
    title    = title.strip()    if title    else ""
    body     = body.strip()     if body     else ""
    tags_raw = tags_raw.strip() if tags_raw else ""

    if len(title) < 5:
        errors.append("Title must be at least 5 characters.")
    elif len(title) > 200:
        errors.append("Title must be 200 characters or fewer.")

    if len(body) < 50:
        errors.append("Post body must be at least 50 characters.")

    tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]
    if len(tags) > 8:
        errors.append("Maximum 8 tags.")
    for tag in tags:
        if len(tag) < 2:
            errors.append(f"Tag '{tag}' is too short.")
        elif len(tag) > 30:
            errors.append(f"Tag '{tag}' is too long.")

    return {"ok": len(errors) == 0, "errors": errors, "tags": tags}