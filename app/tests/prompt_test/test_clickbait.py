from app.services.generate_prompt import check_clickbait

def test_clickbait_explain():
    title = "Clickbait Research Will Make You Lose Some Faith In Humanity"
    content = "Even when they visit sites that specialize in finance and politics, readers do not want to click on articles about finance and politics, a new study has found. The researchers looked at data from 11 online news outlets to figure out what kinds of stories online readers were most likely to click on. The data was then modelled and explained to researchers what kinds of stories they were most likely to click on. Notably, BBC, New York Times, Wall Street Journal, and Yahoo were among the most likely to click on."
    similarity = 0.4832

    result = check_clickbait(title, content, similarity)
    print(result)

