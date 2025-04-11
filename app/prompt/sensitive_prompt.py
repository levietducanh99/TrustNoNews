def generate_sensitive_prompt(label: str, text: str, is_sensitive: bool, criteria: list) -> str:
    criteria_description = "\n".join(
        [f"- {item['label']}: {item['description']} (Probability: {item['probability']})" for item in criteria]
    )
    if is_sensitive:
        prompt = (
            "You are a content moderation assistant.\n"
            "Please analyze the webpage containing the following text to determine if it uses sensitive language and explain why.\n\n"
            f"Content: {text}\n"
            f"Category: {label}\n"
            f"Criteria:\n{criteria_description}\n"
            f"Conclusion: Contains sensitive language\n"
            "Explanation: The content contains offensive, negative, or potentially harmful language that could upset or harm readers. "
            "Using such language may create discomfort or harm the community."
            "Please provide a brief explanation (about 2-4 sentences) in simple, soft language as to why this content is labeled as such. "
            "The explanation should be aimed at a general audience (no technical jargon), and you may use illustrative examples or relatable terms. "
            "Respond as if you are having a conversation with the user."
        )
    else:
        prompt = (
            "You are a content moderation assistant.\n"
            "Please analyze the following text to determine if it uses sensitive language and explain why.\n\n"
            f"Content: {text}\n"
            f"Category: {label}\n"
            f"Criteria:\n{criteria_description}\n"
            f"Conclusion: Does not contain sensitive language\n"
            "Explanation: The content is expressed politely and neutrally. "
            "There are no signs of hateful language, discrimination, or insults directed at individuals or groups."
        )

    return prompt
