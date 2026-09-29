def score_submission(questions, post_data):
    """Coktan secmeli sorulari POST verisine gore degerlendirir.

    `questions`: choices'lari prefetch edilmis Question queryset/listesi.
    `post_data`: her soru icin 'question_<id>' alaninda secilen Choice id'sini
    tasiyan bir mapping (request.POST). Hem quiz hem okuma anlama sorulari
    bu ortak fonksiyonu kullanir.
    """
    results = []
    score = 0
    total = 0

    for question in questions:
        total += 1
        choices = list(question.choices.all())
        selected_id = post_data.get(f'question_{question.id}')
        selected_choice = next((c for c in choices if str(c.id) == selected_id), None)
        correct_choice = next((c for c in choices if c.is_correct), None)
        is_correct = bool(selected_choice and selected_choice.is_correct)

        if is_correct:
            score += 1

        results.append({
            'prompt': question.prompt,
            'explanation': question.explanation,
            'is_correct': is_correct,
            'selected_text': selected_choice.text if selected_choice else None,
            'correct_text': correct_choice.text if correct_choice else None,
        })

    return results, score, total
