import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0.7, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="deepseek-r1-distill-llama-70b")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
{job_description}

### LINK LIST (SKILLS & EXPERIENCE REPOSITORY):
{link_list}

### INSTRUCTION:
You are an AI assistant trained to help job applicants increase their chances of success by tailoring their resume and application based on job requirements.

Your task is to:

1. Analyze the job description and extract the **key skills**, **qualifications**, and **experience** expected.
2. Search through the `link_list` to identify matching **skills**, **projects**, **tools**, or **experience** that align with the job description.
3. Provide an **evaluation summary** that:
   - Highlights the strongest matches between the job description and the `link_list`
   - Points out any gaps or areas for improvement
4. Offer concrete suggestions to **adjust the CV** to increase alignment with the job description.
5. Generate a **tailored cover letter** for this specific role using a professional, confident, and personalized tone.

Keep your response in the following structure:

### EVALUATION SUMMARY:
(Provide bullet-point summary of match between JD and link_list)

### CV IMPROVEMENT SUGGESTIONS:
(Provide actionable pointers on what to highlight, add, or rephrase in the CV)

### COVER LETTER:
(Write a compelling cover letter personalized to the job description)

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))