from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch


class Summarize:
    """
    Uses the given model to summarize a text.
    """
    def __init__(self, 
            input_text, 
            model_name='google/pegasus-cnn_dailymail', 
            use_file=False,
            chunk=4000,
            output_path='summary.txt',
        ):
        """
        :input_text: file or text depending on input
        :model_name: used in match/case method
        :use_file: whether to read as string or path
        :chunk: How many characters to split the text into
        :input_text_list will be a list of texts to process in chunks
        """
        self.input_text = input_text if not use_file else self._read_file(input_text)
        self.model_name = model_name
        self.use_file = use_file
        self.chunk = chunk
        self.output_path = output_path
        self.input_text_list = []
        self.processed_text_list = []
        self.device = torch.device('cpu')
        self.final_text = ''
        

    def summarize(self):
        """
        Divides the text into reasonable sections to summarize. 
        """
        self._divide_text()
        for text in self.input_text_list:
            self._summarize_text(text)
        self._recap()


    def _summarize_text(self, text):
        """
        Calls the child methods in the correct order to summarize the text. 
        """
        # Create the tokenizer and model objects
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name, 
            local_files_only=True
        ).to(self.device)

        # Calculate the input tokens (size of text)
        input_tokens = len(tokenizer(text)['input_ids'])
        
        # Create the summary using the paramaters
        summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
        paramaters = self._get_paramaters(input_tokens)
        summary = summarizer(
            text,
            max_length=paramaters['max_length'],  # > for longer summaries (0.75 words or 4 char per token)
            min_length=paramaters['min_length'],  # Summary can't me shorter than this (will repeat)
            length_penalty=paramaters['length_penalty'],  # > for more detailed, < for more concise [1.0]
            num_beams=paramaters['num_beams'],  # > better summary at resource cost ( diminishing returns [4, 5, 6])
            no_repeat_ngram_size=3,  # prevents repeating any x word phrase [3]
            do_sample=False,  # True = more creative, less for factual summarization
            truncation=True,  # google/Pegasus max tokens = 1024 (4000 char-ish)
            early_stopping=True,
        )
        raw_result = summary[0]['summary_text']
        cleaned_result = self._clean_summary(raw_result)
        self.processed_text_list.append(cleaned_result)


    def _clean_summary(self, text):
        """
        Cleans and formats the generated summary.
        """
        return text.replace('<n>', '\n')


    def _recap(self):
        """
        Prints details about the process
        """
        print(f'\nLength of input text: {self.input_text}')
        print(f'Number of sections: {len(self.input_text_list)}')


    def _get_paramaters(self, input_tokens):
        """
        Calls the methods to get all the parameters and returns them as a 
        dictionary.
        """
        paramaters = {
            'num_beams': 6 if input_tokens < 500 else 8,
            'length_penalty': 1 if input_tokens < 300 else 1.2,
        }
        paramaters['min_length'], paramaters['max_length'] = self._calculate_min_max(input_tokens) 
        return paramaters


    def _calculate_min_max(self, input_tokens):
        """
        Calculates the min_length and max_length based on the number of input
        tokens and returns them. 
        """
        # First determine the ratio to use in the calculation
        if input_tokens < 100:
            ratio = 0.5
        elif input_tokens < 300:
            ratio = 0.35
        elif input_tokens < 800:
            ratio = 0.25
        else:
            ratio = 0.18

        # Set the max/min based on the ratio
        max_length = int(input_tokens * ratio)
        min_length = int(max_length * 0.6)

        # Set reasonable limits
        max_length = min(max_length, 256)
        min_length = max(min_length, 30)

        # Return the results
        return min_length, max_length


    def _divide_text(self):
        """
        Divides the text into parts is longer than 2000 characters.
        """
        self.input_text_list.extend(
            [self.input_text[i:i+self.chunk] for i in range(0, len(self.input_text), self.chunk)]
        )


    def _read_file(self, filepath):
        """
        Is called if use_file=True to read the file. 
        """
        with open(str(filepath), 'r') as file:
            return file.read()
        

    def _write_file(self):
        """
        Is called if use_file=True to read the file. 
        """
        with open(self.output_path, 'r') as file:
            return file.write(self.final_text)
        

if __name__ == '__main__':
    summary = Summarize('scraped_text.txt', use_file=True)
    summary.summarize()
    for text in summary.processed_text_list:
        print('\n\n')
        print(text)
        print('\n\n')


 ### add in recursive loop while self.input_text_list > 1?
 ### work on how best to divide text and adjust paramaters