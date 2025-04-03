# from transformers import pipeline
# from log_utilis import make_logger
# import re
# from summarizer.summarizers.base_handler import BaseSummarizer
# logger = make_logger()
#
# MAX_TOKEN_LENGTH = 1024
#
#
# class BartHandler(BaseSummarizer):
#     def __init__(self):
#         super().__init__()
#
#         self.summarizer = pipeline(
#             "summarization",
#             model="facebook/bart-large-cnn",
#             device=0
#         )
#
#     def summarize(self, text, percentage):
#         """
#         Summarize the given text to the given percentage.
#
#         Args:
#             text (str): Input text to be summarized.
#             percentage (float): Percentage of the text to summarize to, e.g. 0.5 for 50% of the text.
#
#         Returns:
#             str: Summarized text, joined by spaces.
#         """
#         input_length = len(self.summarizer.tokenizer.encode(text))
#         content_info_list = self.__split_text_to_chunks(input_length, text)
#
#         logger.info(f"Summarizing text in {len(content_info_list)} chunks.")
#
#         summarized_content_list = []
#         for content_info in content_info_list:
#             content = content_info.get("content", "")
#             input_length = content_info.get("input_lenght", 0)
#             max_summary_length = int(input_length * percentage)
#             min_summary_length = int(max_summary_length * 0.50)
#
#             logger.info(f"Summarizing text of length: {input_length} to length: {min_summary_length} - {max_summary_length}")
#             summarized_content = self.summarizer(content, max_length=max_summary_length, min_length=min_summary_length, do_sample=False)
#             summarized_content_list.append(summarized_content[0]["summary_text"])
#
#         return " ".join(summarized_content_list)
#
#
#     def __split_text_to_chunks(self, biggest_input_length, content):
#         """
#         Split given text into chunks if it exceeds the MAX_TOKEN_LENGTH.
#
#         Args:
#             input_length (int): Length of the input text
#             content (str): Input text to be split
#
#         Returns:
#             tuple: A tuple containing the list of split content and the length of the longest content
#         """
#         content_info_list = [{
#             "input_lenght": biggest_input_length,
#             "content": content
#         }]
#         while biggest_input_length > MAX_TOKEN_LENGTH:
#             biggest_input_length = 0
#             tmp_content_list = []
#             for content_info in content_info_list:
#                 if content_info.get("input_lenght", 0) > MAX_TOKEN_LENGTH:
#                     content_1, content_2 = self.__split_text_in_half(content_info.get("content", ""))
#                     input_len = len(self.summarizer.tokenizer.encode(content_1))
#
#                     if input_len > biggest_input_length:
#                         biggest_input_length = input_len
#
#                     tmp_content_list.append({
#                         "input_lenght": input_len,
#                         "content": content_1
#                     })
#                     input_len = len(self.summarizer.tokenizer.encode(content_2))
#                     if input_len > biggest_input_length:
#                         biggest_input_length = input_len
#                     tmp_content_list.append({
#                         "input_lenght": input_len,
#                         "content": content_2
#                     })
#                 else:
#                     tmp_content_list.append(content_info)
#
#             content_info_list = tmp_content_list
#         return content_info_list
#
#     @staticmethod
#     def __split_text_in_half(text):
#         """
#         Split the given text into two parts of approximately equal length.
#         It split the text based on punctuation.
#
#         Args:
#             text (str): Input text to be split
#
#         Returns:
#             tuple: A tuple containing the two parts of the split text
#         """
#         sentences = re.split(r'(?<=[.!?])', text)
#
#         part1 = []
#         part2 = []
#         current_length = 0
#         half_length = len(text) // 2
#         second_part = False
#
#         for sentence in sentences:
#             if not second_part and current_length + len(sentence) <= half_length:
#                 part1.append(sentence)
#                 current_length += len(sentence) + 1
#             else:
#                 second_part = True
#                 part2.append(sentence)
#         return " ".join(part1), " ".join(part2)
