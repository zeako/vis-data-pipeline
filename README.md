# vis-data-pipeline

This project describes a data detection pipeline.  

Architecture diagram is available at `assets/`.

There are two key Lambdas in this project which glues the AWS components.
Only `frame_detection` was provided, since it does the heavy lifting,
it doesn't include any exceptions handling.  

If we would want to implement `frame_input` as well we would need to better understand from where we ingest the data (two options described in architecture diagram), validate the input and save it to `S3`.

This repo doesn't include an E2E test because there are a lot of moving parts which some of them can be deployed using the provided terraform definitions at `infra/` folder.