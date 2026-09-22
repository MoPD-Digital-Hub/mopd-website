"""Simple addition CAPTCHA for news comments (session-backed)."""
import random

SESSION_KEY = 'news_comment_math'
SESSION_PROMPT_KEY = 'news_comment_math_prompt'


def issue_math_captcha(request):
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    prompt = f'{a} + {b}'
    request.session[SESSION_KEY] = a + b
    request.session[SESSION_PROMPT_KEY] = prompt
    request.session.modified = True
    return prompt


def current_math_prompt(request):
    prompt = request.session.get(SESSION_PROMPT_KEY)
    if not prompt or SESSION_KEY not in request.session:
        return issue_math_captcha(request)
    return prompt


def verify_math_captcha(request, answer):
    expected = request.session.get(SESSION_KEY)
    try:
        value = int(str(answer).strip())
    except (TypeError, ValueError):
        return False
    if expected is None:
        return False
    return value == int(expected)


def consume_math_captcha(request):
    request.session.pop(SESSION_KEY, None)
    request.session.pop(SESSION_PROMPT_KEY, None)
    request.session.modified = True
