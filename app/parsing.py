#parsing.py

async def parse_deck(uploaded_file) -> list[dict]:
    content = await uploaded_file.text()

    cards = []
    for line in content.splitlines():
        cleaned = line.strip()

        if not cleaned or cleaned.startswith('#'):
            continue

        for delimiter in ('|', '\t', ',', ';', '::', ':'):
            if delimiter in cleaned:
                question, answer = cleaned.split(delimiter, 1)
                q_clean, a_clean = question.strip(), answer.strip()
                if q_clean and a_clean:
                    cards.append({"question": q_clean, "answer": a_clean})
                break

    return cards
