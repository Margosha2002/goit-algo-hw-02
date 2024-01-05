def is_palindrome(text: str) -> bool:
    from collections import deque

    text_deque: deque = deque(text.lower().replace(" ", ""))
    for _ in range(len(text_deque) // 2):
        if text_deque.pop() != text_deque.popleft():
            return False
    return True
