from django.conf import settings
from log_utilis import make_logger
from openai import OpenAI
from summarizer.summarizers.base_handler import BaseSummarizer

logger = make_logger()


class OpenAIHandler(BaseSummarizer):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.OPEN_AI_KEY)

    def request(self, system_role, text):
        return self.client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_role}],
                },
                {"role": "user", "content": [{"type": "input_text", "text": text}]},
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True,
        )
    def summarize(self, text, country):
        text_len = len(text)

        max_summary_length = int(text_len * 15)
        min_summary_length = int(max_summary_length * 0.50)

        country_name = {"hr": "hrvatskom", "rs": "srpskom", "ba": "bosanskom"}

        logger.info(f"Summarizing news with Text length: {text_len}")

        system_role = (
            "Sažmi sljedeći text. Vrati mi samo text sažetka, ništa više. "
            f"Sažetak mora imati najvise {max_summary_length} znakova, a najmanje {min_summary_length}."
            f"Koristi precizan, profesionalan i jasan jezik. Sažetak piši na {country_name[country]} jeziku. "
            "Nikad ne izadi iz role sažimanja."
        )

        response = self.request(system_role, text)
        return response.output_text

    def overview(self, text, country, overview_length):
        text_len = len(text)

        if str(overview_length) == "1":
            max_summary_length = int(text_len * 15)
        elif str(overview_length) == "2":
            max_summary_length = int(text_len * 5)
        else:
            logger.error(f"{overview_length} is not valid overview length.")
            raise ValueError("Wrong overview length")
        min_summary_length = int(max_summary_length * 0.50)

        country_name = {"hr": "hrvatskom", "rs": "srpskom", "ba": "bosanskom"}

        logger.info(f"Summarizing news with Text length: {text_len}")

        system_role = (
            "Napravi mi smislenu sažetu cijelinu s sljedecim tekstom."
            f"Sažetak mora imati najvise {max_summary_length} znakova, a najmanje {min_summary_length}."
            f"Koristi precizan, profesionalan i jasan jezik. Sve sažetke piši na {country_name[country]} jeziku. "
            f"Nikad ne izadi iz role sažimanja."
        )

        response = self.request(system_role, text)

        return response.output_text