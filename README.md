# prospie

prospie is an AI tool to support trusts fundraisers in the third sector. prospie will speed up and improve the trusts prospecting process, saving money for charities and contributing to better fundraiser wellbeing ✨

## Repo Structure

1. Generates a sample of *n* funders from Charity Commission data (1000 for the prototype)
2. Gets all registered (non-removed) charities from [Charity Commission data](https://register-of-charities.charitycommission.gov.uk/en/register/full-register-download) to serve as potential recipients
3. Builds a database of funders, grants and recipients using the Charity Commission and [360Giving](https://www.360giving.org/explore/technical/api/) APIs
4. Builds a database of grants and recipients using PDFs of official charity accounts
5. Gets information from [The List](https://the-list.uk/) and adds to database
6. EDA - explores, cleans and visualises the data   
    6.1. Stores checkpoints locally     
    6.2. Reprocesses PDFs to extract accounts sections using Claude LLM instead of regex
7. Explores the best model and approach for the embeddings    
    7.1. Stores checkpoints locally     
    7.2. Compares embedding models to select the most suitable for the project      
    7.3. Experiments with different approaches to embedding the text to be used in semantic similarity comparisons      
8. Prepares data ready for modelling        
    8.1. Stores checkpoints locally     
9. An evaluation form to gather professional fundraisers' opinions on the alignment of a sample of funder-recipient pairs, to assess the performance of the app
10. Develops the logic behind the alignment score       
    10.1. Stores checkpoints locally    
    10.2. Develops the scoring logic function-by-function       
    10.3. Tests the scoring logic through iterations by adding and refactoring weightings 
11. A backend to deliver the calculated alignment score of a user's charity and their chosen funder  
12. A frontend to interact with the app 

## How to...

### Build the Database

The database is built in stages by running Python scripts in folders 01-05. Each stage processes and uploads data to your Supabase instance.

#### Prerequisites

- Supabase project with appropriate tables configured [per the schema](https://github.com/lico27/prospie/blob/64276f68aa005a70749cb7eb20427adc115679bc/schema.sql/)
- API keys stored in a `.env` file in the project root:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service role key
- `ANTHROPIC_KEY` - Claude API key (for PDF processing in step 04)

#### Steps

TBC

----

### Use the App

TBC

----

### Evaluate the App

Visit [https://lico27.github.io/prospie/](https://lico27.github.io/prospie/). 