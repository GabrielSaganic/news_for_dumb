from log_utilis import make_logger


from openai import OpenAI
from summarizer.summarizers.base_handler import BaseSummarizer
from django.conf import settings
logger = make_logger()

class OpenAIHandler(BaseSummarizer):
  def __init__(self):
    super().__init__()
    self.client = OpenAI(api_key=settings.OPEN_AI_KEY)

  def summarize(self, text, country):
    text_len = len(text)
    max_summary_length_part_1 = int(text_len * 50)
    min_summary_length_part_1 = int(max_summary_length_part_1 * 0.50)

    max_summary_length_part_2 = int(text_len * 30)
    min_summary_length_part_2 = int(max_summary_length_part_1 * 0.50)

    country_name = {
      "hr": "hrvatskom",
      "rs": "srpskom",
      "ba": "bosanskom"
    }

    logger.info(f"Summarizing news with Text length: {text_len}")

    system_role = (
      f"Sažmi ovaj tekst dva puta. Ispisi prvi sazetak zatim ispisi '-------------' a zatim ispisi drugi sazetak."
      f"Prvi sazetak mora imati najvise {max_summary_length_part_1} znakova, a najmanje {min_summary_length_part_1}."
      f"Drugi sazetak mora imati najvise {max_summary_length_part_2} znakova, a najmanje {min_summary_length_part_2}."
      f"Koristi precizan, profesionalan i jasan jezik. Sve sažetke piši na {country_name[country]} jeziku. "
      f"Nikad ne izadi iz role sažimanja."
    )

    response = self.client.responses.create(
      model="gpt-4o-mini",
      input=[
        {
          "role": "system",
          "content": [
            {
              "type": "input_text",
              "text": system_role
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "input_text",
              "text": text
            }
          ]
        },
      ],
      text={
        "format": {
          "type": "text"
        }
      },
      reasoning={},
      tools=[],
      temperature=1,
      max_output_tokens=2048,
      top_p=1,
      store=True
    )

    content_list = response.output_text.split('-------------')
    if len(content_list) > 1:
      return content_list[0], content_list[1]
    return "", ""