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
    6.2.Reprocesses PDFs to extract accounts sections using Claude LLM instead of regex
7. Explores the best model and approach for the embeddings      
    7.1. Compares embedding models to select the most suitable for the project      
    7.2. Experiments with different approaches to embedding the text to be used in semantic similarity comparisons      
8. Prepares data ready for modelling
9. An evaluation form to gather professional fundraisers' opinions on the alignment of a sample of funder-recipient pairs, to assess the performance of the app
- A frontend to interact with the app 
- An informed scoring logic to calculate the alignment score of a user's charity and their chosen funder

## How to...

### Build the Database

TBC

### Use the Frontend

TBC

### Evaluate the App

Visit [https://lico27.github.io/prospie/](https://lico27.github.io/prospie/). 